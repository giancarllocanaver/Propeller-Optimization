import subprocess
import time
import os

import numpy as np

# from propeller_optmization.data_structures import PPoints
from uuid import uuid4


class AirfoilCreation:
    def __init__(self) -> None:
        self.airfoil_name = None
        self.airfoil_dir = None

    def generate_airfoil_naca(self, airfoil_name: str) -> None:
        """
        Method responsible for executing the creation of
        new NACA foils and saving the coordinates into a
        txt file.

        :param airfoil_name: airfoil name
        """
        self.airfoil_name = airfoil_name
        self.airfoil_dir = os.path.join(
            os.getcwd(),
            "processing",
            "execution_steps",
            airfoil_name + ".txt",
        )

        self.__create_airfoil()

    def obtain_p_points_by_file(self) -> np.ndarray:
        """
        Method responsible for obtaining the P points
        created by xfoil into a certain txt file.

        :return: P points generated
        """
        points = np.loadtxt(self.airfoil_dir, skiprows=1)
        points_p = np.array([points[:, 0], points[:, 1]])

        points_p[1][0] = 0
        points_p[1][-1] = 0

        return points_p

    def suit_p_points(self, airfoil_data: dict) -> np.ndarray:
        """
        Method responsible for adapting the airfoil bezier P
        points passed in input to the corresponding format
        used in the optimizer.

        :param airfoil_data: corresponding bezier P points of
            the airfoil
        ...
        :return: addapted airfoil P points to numpy array
        """
        points_p = np.array([airfoil_data.get("xPoints"), airfoil_data.get("yPoints")])

        points_p[1][0] = 0
        points_p[1][-1] = 0

        return points_p

    def __create_airfoil(self) -> None:
        """
        Method responsible for creating new NACA foils
        and saving the P points into a txt file.
        """
        airfoil_generation_dir_file = (
            "processing/execution_steps/generation_airfoil_file.txt"
        )

        with open(airfoil_generation_dir_file, "w") as writer:
            writer.write("PLOP\n")
            writer.write("G\n")
            writer.write(f"\n")
            writer.write(f"{self.airfoil_name}\n")
            writer.write(f"\n")
            writer.write(f"PPAR\n")
            writer.write(f"n\n")
            writer.write(f"5\n")
            writer.write(f"\n")
            writer.write(f"\n")
            writer.write(f"save\n")
            writer.write(f"processing/execution_steps/{self.airfoil_name}.txt\n")
            writer.write(f"\n")
            writer.write(f"quit\n\n")

        exe_dir = os.path.join(
            "processing",
            "xfoil_instances",
            "xfoil.exe",
        )

        subprocess.Popen(
            exe_dir + " < " + airfoil_generation_dir_file,
            shell=True,
        )
        time.sleep(0.5)

    @staticmethod
    def create_airfoil_in_xfoil_from_splines(
        spline: np.ndarray, results_filename: str = None
    ) -> str:
        """
        Method responsible for writing the airfoil
        coordinates in a txt file, which will be u-
        sed by xfoil to calculate the objective fun-
        ction.

        :param spline: spline of the foil
        :param results_filename: the filename of the
            airfoil
        ...
        :return: the complete patch name of the airfoil
        """
        if spline is None:
            return None

        spline = spline.reshape((spline.shape[0], spline.shape[1]))
        x_points = spline[0]
        y_points = spline[1]

        uuid_airfoil = str(uuid4())[:10].replace("-", "")

        if results_filename is None:
            filename_dir = f"processing/execution_steps/airfoil_{uuid_airfoil}.dat"
        else:
            filename_dir = results_filename

        with open(filename_dir, "w") as writer:
            for point in range(len(x_points)):
                writer.write(
                    f"{round(x_points[point], 4)}    {round(y_points[point], 4)}\n"
                )
            writer.close()

        return filename_dir
