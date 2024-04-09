import numpy as np
import pandas as pd

from .data_reader import DataReader
from .data_structures import Particle
from .objective_function import ObjectiveFunction


class PSO:
    def __init__(
        self, data_reader: DataReader, uuid: str, results_dir: str
    ) -> None:
        self.data_reader = data_reader
        self.uuid = uuid
        self.results_dir = results_dir

        self.particles = self.__set_particles()
        self.best = self.__set_best()
        self.hyperparameters = self.__set_hyperparameters()

    def __set_particles(self) -> dict:
        particles = {
            particle: Particle(
                objective_function=0.0,
                variables=np.array([]),
                velocity=np.array([]),
                points_p=np.array([]),
                points_a=np.array([]),
                splines=list(),
                results=dict(),
            )
            for particle in range(
                self.data_reader.optimization_data.get("quantityOfParticles")
            )
        }

        return particles

    def __set_best(self):
        best = {
            "p_best": self.particles.copy(),
            "g_best": {0: self.particles.get(0)},
        }

        return best

    def __set_hyperparameters(self) -> dict:
        if self.data_reader.optimization_data.get("constantHyperParameters"):
            hyperparameters = {
                "c1": lambda t: 2.05,
                "c2": lambda t: 2.05,
                "w": lambda t: 0.72984,
            }

            return hyperparameters

        number_of_iterations = self.data_reader.optimization_data.get(
            "maximumIterations"
        )
        hyperparameters = {
            "c1": lambda t: -3 * t / number_of_iterations + 3.5,
            "c2": lambda t: 3 * t / number_of_iterations + 0.5,
            "w": lambda t: 0.4 * (t - number_of_iterations) / number_of_iterations**2
            + 0.4,
        }

        return hyperparameters

    def __check_convergence(self) -> bool:
        pass

    def __check_constrainsts(self):
        def penalize(self):
            pass

        pass

    def __update_p_best(self):
        pass

    def __update_g_best(self):
        pass

    def __update_velocity(self):
        pass

    def __update_variables(self):
        pass

    def __update_objective_function(self):
        pass

    def set_initial_conditions(self):
        init_cond_inst = ObjectiveFunction(
            airfoil_name=self.data_reader.propeller_geometric_conditions.get("airfoil"),
            particles=self.particles,
            flight_conditions=self.data_reader.flight_conditions,
            propeller_geometry=self.data_reader.propeller_geometric_conditions,
            uuid=self.uuid,
            xfoil_instances=self.data_reader.optimization_data.get("xfoilInstances"),
        )
        init_cond_inst.set_initial_conditions()

    def iterate(self):
        for t in range(self.data_reader.optimization_data.get("maximumIterations")):
            self.__check_constrainsts()
            self.__update_p_best()
            self.__update_g_best()
            self.__update_velocity()
            self.__update_variables()
            if self.__check_convergence():
                break
            self.__update_objective_function()
