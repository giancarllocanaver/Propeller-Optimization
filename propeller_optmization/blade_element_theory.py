import time
import numpy as np
from multiprocessing.pool import Pool

from .utilities.xfoil_management import XfoilManagement


class BladeElementTheory:
    def __init__(
        self,
        uuid: str,
        airfoils: dict,
        flight_conditions: dict,
        propeller_geometric_conditions: dict,
        **kwargs
    ):
        self.uuid = uuid
        self.airfoils = airfoils
        self.flight_conditions = flight_conditions
        self.propeller_geometric_conditions = propeller_geometric_conditions
        self.AoA = propeller_geometric_conditions.get("AoAInMaximumEfficiency")
        self.q_xfoil_intances = kwargs.get("xfoil_instances", 1)

    def calculate_propeller_results(self) -> dict:
        self.__calculate_tangencial_velocity()
        self.__calculate_advance_rate()
        self.__calculate_phi()
        self.__calculate_resultant_velocity()
        self.__calculate_reynolds_and_mach()
        self.__calculate_Cl_and_Cd()

        return self.results

    def __calculate_tangencial_velocity(self):
        self.tangencial_velocity = (
            2.0
            * np.pi
            / 60.0
            * np.array(self.flight_conditions.get("engineSpin"))
            * np.array(self.propeller_geometric_conditions.get("radius"))
        )

    def __calculate_advance_rate(self):
        self.advance_rate = (
            60
            * self.flight_conditions.get("speed")
            * 1
            / self.flight_conditions.get("engineSpin")
            * 1
            / self.propeller_geometric_conditions.get("bladeDiameter")
        )

    def __calculate_phi(self):
        self.phi = np.arctan(
            self.flight_conditions.get("speed") / self.tangencial_velocity
        )
        self.phi[-1] = 0.0

    def __calculate_resultant_velocity(self):
        self.resultant_velocity = self.tangencial_velocity / np.cos(self.phi)

    def __calculate_reynolds_and_mach(self):
        self.reynolds = (
            self.flight_conditions.get("airDensity")
            * self.flight_conditions.get("speed")
            * self.propeller_geometric_conditions.get("bladeDiameter")
            / self.flight_conditions.get("viscosity")
        )
        self.mach = self.resultant_velocity / np.sqrt(
            1.4 * 287 * self.flight_conditions.get("temperature")
        )

    def __calculate_Cl_and_Cd(self):
        def split_instances_per_time() -> dict:
            splines_copy = list(self.airfoils.items())
            t_inst_airf = dict()
            t = 0

            while True:
                t_inst_airf[t] = list()
                for inst in range(self.q_xfoil_intances):
                    if not len(splines_copy):
                        break

                    t_inst_airf[t].append((inst, splines_copy[0]))
                    splines_copy.pop(0)

                if not len(splines_copy):
                    break

                t += 1

            return t_inst_airf

        time_instances = split_instances_per_time()

        results = list()
        for t in time_instances:
            p_instances = Pool(processes=self.q_xfoil_intances)
            results_t = p_instances.starmap(
                execute_xfoil,
                [
                    (
                        section_caract[1],
                        inst,
                        section_caract[0],
                        self.AoA,
                        self.reynolds,
                        self.mach,
                    )
                    for inst, section_caract in time_instances.get(t)
                ],
            )

            results += results_t

        self.cl_cd_results = results


def execute_xfoil(
    spline: str,
    xfoil_instance_numb: int,
    section: int,
    alpha: float,
    reynolds: float,
    mach: float,
) -> tuple:
    xfoil_instance = XfoilManagement(reynolds, mach)
    xfoil_instance.execute_xfoil(
        splines_file=spline,
        l_AoA=alpha,
        u_AoA=alpha,
        AoA_step=0,
        iter=200,
        viscous=True,
        ch_pannels=True,
        xfoil_instance=xfoil_instance_numb,
    )
    cl, cd = xfoil_instance.obtain_cl_cd()

    return section, cl, cd
