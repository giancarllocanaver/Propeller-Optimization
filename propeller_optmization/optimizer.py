import numpy as np
from typing import NamedTuple

from .data_reader import DataReader


class Particle(NamedTuple):
    objective_function: float
    variables: np.ndarray
    velocity: np.ndarray
    points_p: np.ndarray
    points_a: np.ndarray


class PSO:
    def __init__(self, data_reader: DataReader, airfoil_coordinates_dir: str, results_dir: str) -> None:
        self.data_reader = data_reader
        self.airfoil_coordinates_dir = airfoil_coordinates_dir
        self.results_dir = results_dir

        self.particles = self._set_particles()
        self.best = self._set_best()
        self.hyperparameters = self._set_hyperparameters()

    def _set_particles(self) -> dict:
        particles = {
            particle: Particle(
                objective_function=0.0,
                variables=np.array([0.0 for _ in range(7)]),
                velocity=np.array([0.0 for _ in range(7)]),
                points_p=np.array([0.0 for _ in range(7)]),
                points_a=np.array([0.0 for _ in range(7)]),
            )
            for particle in range(self.data_reader.optimization_data.quantityOfParticles)
        }

        return particles

    def _set_best(self):
        best = {
            "p_best": {
                particle: Particle(
                    objective_function=0.0,
                    variables=np.array([0.0 for _ in range(7)]),
                    points_p=np.array([0.0 for _ in range(7)]),
                    points_a=np.array([0.0 for _ in range(7)]),
                )
                for particle in range(self.data_reader.optimization_data.quantityOfParticles)
            },
            "g_best": {
                0: Particle(
                    objective_function=0.0,
                    variables=np.array([0.0 for _ in range(7)]),
                    points_p=np.array([0.0 for _ in range(7)]),
                    points_a=np.array([0.0 for _ in range(7)]),
                )
            }
        }

        return best

    def _set_hyperparameters(self) -> dict:
        if self.data_reader.optimization_data.constantHyperParameters:
            hyperparameters = {
                "c1": lambda t: 2.05,
                "c2": lambda t: 2.05,
                "w": lambda t: 0.72984,
            }

            return hyperparameters
        
        number_of_iterations = self.data_reader.optimization_data.maximumIterations
        hyperparameters = {
            "c1": lambda t: -3*t/number_of_iterations + 3.5,
            "c2": lambda t: 3*t/number_of_iterations + 0.5,
            "w": lambda t: 0.4*(t - number_of_iterations)/number_of_iterations**2 + 0.4,
        }

        return hyperparameters

    def _check_convergence(self) -> bool:
        pass
    
    def _check_constrainsts(self):
        def penalize(self):
            pass
        
        pass

    def _update_p_best(self):
        pass

    def _update_g_best(self):
        pass

    def _update_velocity(self):
        pass

    def _update_variables(self):
        pass

    def _update_objective_function(self):
        pass

    def set_initial_condition(self):
        pass

    def iterate(self):
        for t in range(self.data_reader.optimization_data.maximumIterations):
            self._check_constrainsts()
            self._update_p_best()
            self._update_g_best()
            self._update_velocity()
            self._update_variables()            
            if self._check_convergence():
                break
            self._update_objective_function()



    




    
        
        

