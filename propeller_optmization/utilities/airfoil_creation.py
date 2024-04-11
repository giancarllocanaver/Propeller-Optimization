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

    def generate_airfoil(self, airfoil_name: str) -> None:
        self.airfoil_name = airfoil_name
        self.airfoil_dir = os.path.join(
            os.getcwd(),
            "processing",
            "execution_steps",
            airfoil_name + ".txt",
        )

        self.__create_airfoil()

    def obtain_p_points(self):
        points = np.loadtxt(self.airfoil_dir, skiprows=1)
        points_p = np.array([points[:, 0], points[:, 1]])

        points_p[1][0] = 0
        points_p[1][-1] = 0

        return points_p

    def __create_airfoil(self):
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
    def create_airfoil_in_xfoil_from_splines(spline: np.ndarray) -> str:
        if spline is None:
            return None
        
        spline = spline.reshape((spline.shape[0], spline.shape[1]))
        x_points = spline[0]
        y_points = spline[1]

        uuid_airfoil = str(uuid4())[:10].replace("-", "")
        filename_dir = f"processing/execution_steps/airfoil_{uuid_airfoil}.dat"

        with open(filename_dir, "w") as writer:
            for point in range(len(x_points)):
                writer.write(
                    f"{round(x_points[point], 4)}    {round(y_points[point], 4)}\n"
                )
            writer.close()

        return filename_dir
