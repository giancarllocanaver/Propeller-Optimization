from secrets import randbits
import numpy as np

from src.utilities.airfoil_creation import AirfoilCreation
from src.utilities.constants import POINTS_BETWEEN_POINTS_P


class GeometryManagement(AirfoilCreation):
    def __init__(self):
        self.p_points = None

        super().__init__()

    def create_base_airfoil(self, base_airfoil_name: str) -> np.ndarray:
        self.generate_airfoil(base_airfoil_name)
        self.p_points = self.obtain_p_points()

        return self.p_points

    def generate_bezier_points(self) -> np.ndarray:
        def bezier_coefficients(points_p):
            n = len(points_p) - 1

            M = np.zeros((n, n))

            M[0, 0] = 2.0
            M[-1, -1] = 7.0

            np.fill_diagonal(M[1:], 1.0)
            np.fill_diagonal(M[0:-1, 1:], 1.0)
            np.fill_diagonal(M[1:-1, 1:-1], 4.0)

            M[-1, -2] = 2.0

            u = np.zeros((n, 1))

            for i in range(n):
                u[i] = 2 * (2 * points_p[i] + points_p[i + 1])

            u[0, 0] = points_p[0] + 2 * points_p[1]
            u[-1, 0] = 8 * points_p[-2] + points_p[-1]

            a = np.linalg.solve(M, u)
            b = np.zeros(n)

            for i in range(n - 1):
                b[i] = 2 * points_p[i + 1] - a[i + 1]

            b[n - 1] = (a[n - 1] + points_p[n]) / 2

            a = a.reshape((a.shape[0],))
            b = b.reshape((b.shape[0],))

            return a, b

        def line(i, j, a, b):
            return (
                lambda t: (1 - t) ** 3 * i
                + 3 * t * (1 - t) ** 2 * a
                + 3 * t**2 * (1 - t) * b
                + t**3 * j
            )

        n = len(self.p_points[0]) - 1

        splines, a_points, b_poins = list(), list(), list()
        for j in range(2):
            a, b = bezier_coefficients(self.p_points[j])
            spline = [
                line(self.p_points[j, i], self.p_points[j, i + 1], a[i], b[i])
                for i in range(n)
            ]
            bezier_spline = [
                h(t)
                for h in spline
                for t in np.linspace(0, 1, num=POINTS_BETWEEN_POINTS_P)
            ]
            splines.append(bezier_spline)
            a_points.append(a)
            b_poins.append(b)

        splines = np.array(splines)
        a_points = np.array(a_points)
        b_poins = np.array(b_poins)

        airfoil_spline = np.reshape(splines, (splines.shape[0], splines.shape[1]))
        a_points = np.reshape(a_points, (a_points.shape[0], a_points.shape[1]))

        return a_points

    def update_airfoil(self, a_points: np.ndarray, p_points: np.ndarray):
        def create_new_p_points(a: np.ndarray, p_points: np.array, n: int):
            p_1 = (2 * a[0] + a[1] - p_points[0]) / 2
            p_n_minous_1 = (2 * a[-2] + 7 * a[-1] - p_points[-1]) / 8

            intermediate_points = np.array(p_points[0])
            intermediate_points = np.append(intermediate_points, p_1)

            for i in range(1, n - 2):
                p_i_plus_1 = (
                    a[i - 1] + 4 * a[i] + a[i + 1]
                ) / 2 - 2 * intermediate_points[i]
                intermediate_points = np.append(intermediate_points, p_i_plus_1)

            intermediate_points = np.append(intermediate_points, p_n_minous_1)
            intermediate_points = np.append(intermediate_points, p_points[-1])

            return intermediate_points

        def create_new_b_points(a: np.ndarray, p_points: np.ndarray, n: int):
            b = np.array([2 * p_points[i + 1] - a[i + 1] for i in range(0, n - 1)])
            b = np.append(b, (a[n - 1] + p_points[n]) / 2)

            return b

        def create_new_spline(p_i, p_i_plus_1, a, b):
            return (
                lambda t: (1 - t) ** 3 * p_i
                + 3 * t * (1 - t) ** 2 * a
                + 3 * t**2 * (1 - t) * b
                + t**3 * p_i_plus_1
            )

        def ajust_splines(splines: np.ndarray):
            x_coordinates = list()
            y_coordinates = list()

            for i in range(len(splines[0])):
                if splines[0, i] not in x_coordinates:
                    x_coordinates.append(splines[0, i])
                    y_coordinates.append(splines[1, i])

            x_coordinates.append(1)
            y_coordinates.append(0)

            return np.array((x_coordinates, y_coordinates))

        def check_intersection(splines: np.ndarray):
            def intersection(x1, x2, x3, x4, y1, y2, y3, y4):
                d = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
                if d:
                    xs = (
                        (x1 * y2 - y1 * x2) * (x3 - x4)
                        - (x1 - x2) * (x3 * y4 - y3 * x4)
                    ) / d

                    if (xs >= min(x1, x2) and xs <= max(x1, x2)) and (
                        xs >= min(x3, x4) and xs <= max(x3, x4)
                    ):
                        return True

                return False

            xs = [
                True
                for i in range(len(splines[0]) - 1)
                for j in range(i - 1)
                if intersection(
                    splines[0, i],
                    splines[0, i + 1],
                    splines[0, j],
                    splines[0, j + 1],
                    splines[1, i],
                    splines[1, i + 1],
                    splines[1, j],
                    splines[1, j + 1],
                )
            ]

            return True if len(xs) > 1 else False

        n = len(p_points[0]) - 1

        splines, b_points, new_p_points = list(), list(), list()
        for j in range(2):
            new_points = create_new_p_points(a_points[j], p_points[j], n)
            b = create_new_b_points(a_points[j], new_points, n)

            spline = [
                create_new_spline(
                    new_points[i], new_points[i + 1], a_points[j, i], b[i]
                )
                for i in range(0, n)
            ]
            bezier_spline = [
                h(t)
                for h in spline
                for t in np.linspace(0, 1, num=POINTS_BETWEEN_POINTS_P)
            ]

            splines.append(bezier_spline)
            b_points.append(b)
            new_p_points.append(new_points)

        splines, b_points, new_p_points = (
            np.array(splines),
            np.array(b_points),
            np.array(new_p_points),
        )
        splines = ajust_splines(splines)

        return splines if not check_intersection(splines) else None
