import os
import random
import psutil
import numpy as np
from uuid import uuid4

from subprocess import Popen, TimeoutExpired

N_CRIT = 9


class DoubleSolutionError(Exception):
    pass


class XfoilManagement:
    def __init__(self, reynolds: float, mach: float) -> None:
        self.reynolds = reynolds
        self.mach = mach

    def execute_xfoil(
        self,
        splines_file: str,
        l_AoA: float,
        u_AoA: float,
        AoA_step: float,
        iter: int,
        **kwargs,
    ):
        self.splines_file = splines_file
        self.l_AoA = l_AoA
        self.u_AoA = u_AoA
        self.AoA_step = AoA_step
        self.iter = iter

        self.change_pannels = True if "ch_pannels" in kwargs else False
        self.viscous_solution = True if "viscous" in kwargs else False
        self.mach_solution = True if "mach" in kwargs else False
        self.xfoil_instance = kwargs.get("xfoil_instance", 0)

        if self.viscous_solution and self.mach_solution:
            raise DoubleSolutionError(
                "Cannot execute xfoil with viscous and mach solution set to True"
            )

        self.input_filename, self.output_filename = self.__create_xfoil_file_commands()
        self.__execute_xfoil_file()

    def __create_xfoil_file_commands(self) -> str:
        file_uuid = str(uuid4())[:10].replace("-", "")

        input_filename = f"xfoil_input_{file_uuid}.txt"
        input = os.path.join(
            os.getcwd(),
            "processing",
            "execution_steps",
            input_filename,
        )

        output_filename = f"xfoil_output_{file_uuid}.txt"

        with open(input, "w") as file:
            file.write("PLOP" + "\n")
            file.write("G" + "\n")
            file.write("\n")
            file.write("LOAD" + "\n")
            file.write(self.splines_file + "\n")

            if self.change_pannels:
                file.write("PPAR" + "\n")
                file.write("N" + "\n")
                file.write("200" + "\n")
                file.write("\n")
                file.write("\n")

            file.write("oper" + "\n")

            if self.viscous_solution:
                file.write("visc " + str(self.reynolds) + "\n")
                file.write("vpar" + "\n")
                file.write("N" + "\n")
                file.write(str(N_CRIT) + "\n")
                file.write("\n")

            if self.mach_solution:
                file.write("mach" + str(self.mach) + "\n")

            file.write("iter " + str(self.iter) + "\n")
            file.write("pacc" + "\n")
            file.write(f"processing/execution_steps/" + output_filename + "\n")
            file.write("\n")
            file.write(
                "aseq "
                + str(self.l_AoA)
                + " "
                + str(self.u_AoA)
                + " "
                + str(self.AoA_step)
                + "\n"
            )
            file.write("\n")
            file.write("quit")
            file.write("\n")
            file.write("quit")

            file.close()

        return input_filename, output_filename

    def __execute_xfoil_file(self):
        def kill_process(proc_pid: int):
            try:
                process = psutil.Process(proc_pid)
                for proc in process.children(recursive=True):
                    proc.kill()

                process.kill()
            except psutil.NoSuchProcess:
                return

        xfoil_base_dir = os.path.join(
            "processing",
            "xfoil_instances",
            f"xfoil_{self.xfoil_instance}.exe",
        )
        input_filename = os.path.join(
            "processing",
            "execution_steps",
            self.input_filename,
        )

        try:
            p = Popen(f"{xfoil_base_dir} < " + input_filename, shell=True)
            p.wait(1)
        except TimeoutExpired:
            kill_process(p.pid)
        except Exception as e:
            print(e)

    def obtain_cl_cd(self):
        output_dir = os.path.join(
            os.getcwd(),
            "processing",
            "execution_steps",
            self.output_filename,
        )

        try:
            airfoil_data = np.loadtxt(output_dir, skiprows=12)
        except (OSError, Exception):
            return 0, 1

        if not airfoil_data.size:
            return 0, 1

        cl = airfoil_data[1]
        cd = abs(airfoil_data[2])

        return cl, cd
