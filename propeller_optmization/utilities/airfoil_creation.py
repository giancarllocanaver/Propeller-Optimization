import subprocess
import time

import numpy as np

from propeller_optmization.data_structures import PPoints

class AirfoilCreation:
    def __init__(self) -> None:
        self.airfoil_name = None
        self.airfoil_dir = None

    def generate_airfoil(self, airfoil_name: str) -> None:
        self.airfoil_name = airfoil_name
        self.airfoil_dir = f'processing/execution_steps/{airfoil_name}.txt'

        self._create_airfoil()
    
    def obtain_p_points(self):
        points = np.loadtxt(self.airfoil_dir, skiprows=1)        
        points_p = np.array([points[:,0], points[:,1]])

        points_p[1][0]  = 0
        points_p[1][-1] = 0

        return points_p

    def _create_airfoil(self):
        airfoil_generation_dir_file = 'processing/execution_steps/generation_airfoil_file.txt'
        
        with open(airfoil_generation_dir_file, 'w') as writer:
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
            writer.write(f"{self.airfoil_dir}\n")
            writer.write(f"\n")
            writer.write(f"quit\n\n")

        subprocess.Popen(
            "xfoil.exe < " + airfoil_generation_dir_file, shell=True
        )
        time.sleep(0.5)

    @staticmethod
    def create_airfoil_in_xfoil_from_splines() -> str:
        pass
