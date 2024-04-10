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
        self.__calculate_gamma()
        self.__calculate_dt_and_dq()
        self.__calculate_efficiency()

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

    def __calculate_gamma(self):
        self.gamma = [
            np.arctan(sec[2] / sec[1]) if sec[1] != 0 else None
            for sec in self.cl_cd_results
        ]

    def __calculate_dt_and_dq(self):
        q = (
            0.5
            * self.flight_conditions.get("airDensity")
            * self.flight_conditions.get("speed") ** 2
        )

        den = lambda secao: np.cos(self.gamma[secao]) * np.sin(self.phi[secao]) ** 2

        self.dt = [
            (
                (
                    q
                    * sec[1]
                    * self.propeller_geometric_conditions.get("chord")[sec[0]]
                    * np.cos(self.phi[sec[0]] + self.gamma[sec[0]])
                    / den(sec[0])
                )
                if self.gamma[sec[0]] is not None
                else 0
            )
            for sec in self.cl_cd_results
        ]
        self.dt.append(0)

        self.dq = [
            (
                (
                    q
                    * sec[1]
                    * self.propeller_geometric_conditions.get("chord")[sec[0]]
                    * self.propeller_geometric_conditions.get("radius")[sec[0]]
                    * np.sin(self.phi[sec[0]] + self.gamma[sec[0]])
                    / den(sec[0])
                )
                if self.gamma[sec[0]] is not None
                else 0
            )
            for sec in self.cl_cd_results
        ]
        self.dq.append(0)

    def __calculate_efficiency(self):
        def integrate(y: list, x: list):
            i = 0
            for n in range(1, len(x)):
                i += (x[n] - x[n - 1]) * (y[n] + y[n - 1]) / 2

            return i

        traction = integrate(self.dt, self.propeller_geometric_conditions.get("radius"))
        torque = integrate(self.dq, self.propeller_geometric_conditions.get("radius"))

        n = self.flight_conditions.get("engineSpin") / 60

        t_coeffic = traction / (
            self.flight_conditions.get("airDensity")
            * n**2
            * self.propeller_geometric_conditions.get("bladeDiameter") ** 4
        )
        q_coeffic = torque / (
            self.flight_conditions.get("airDensity")
            * n**2
            * self.propeller_geometric_conditions.get("bladeDiameter") ** 5
        )
        p_coeffic = 2 * np.pi * q_coeffic

        self.efficiency = (
            self.advance_rate * t_coeffic / p_coeffic if p_coeffic != 0 else None
        )


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
