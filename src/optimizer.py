import os
import numpy as np
import pandas as pd
from tqdm import tqdm

from .data_modules.data_reader import DataReader
from .data_modules.data_structures import Particle
from .objective_function import ObjectiveFunction


class PSO:
    def __init__(self, data_reader: DataReader, uuid: str, results_dir: str) -> None:
        self.data_reader = data_reader
        self.uuid = uuid
        self.results_dir = results_dir
        self.results_per_time = dict()
        self.fo_per_time = dict()

        self.particles = self.__set_particles()
        self.best = self.__set_best()
        self.best_objective = self.__set_best_objective()
        self.hyperparameters = self.__set_hyperparameters()

    def __set_particles(self) -> dict:
        """
        Method responsible for setting
        new particles to the optimizer

        :return: particles dict
        """
        particles = {
            particle: Particle(
                objective_function=0.0,
                variables=np.array([]),
                velocity=np.array([0.0 for _ in range(7)]),
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
        """
        Method responsible for setting
        the best particles instance.
        
        :return:: best particles in
            a dict
        """
        best = {
            "p_best": self.particles.copy(),
            "g_best": {0: self.particles.get(0)},
        }

        return best

    def __set_best_objective(self):
        """
        Method responsible for setting
        the best objective of particles.

        :return: best objective dict
        """
        best_obj = {
            "p_best_obj": {particle: 0.0 for particle in self.particles},
            "g_best_obj": {0: 0.0},
        }

        return best_obj

    def __set_hyperparameters(self) -> dict:
        """
        Method responsible for setting the hyperparameters
        for the optimizer.

        :return: hyperparameters dict
        """
        r = np.random.rand(2)

        if self.data_reader.optimization_data.get("constantHyperParameters"):
            hyperparameters = {
                "c1": lambda t: 2.05,
                "c2": lambda t: 2.05,
                "w": lambda t: 0.72984,
                "r": r,
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
            "r": r,
        }

        return hyperparameters

    def __check_convergence(self) -> bool:
        """
        Method responsible for checking if
        the optimization is converged.

        :return: True if the optimization
            is converged
        """
        best_variables = list(self.best.get("g_best").values())[0].variables

        converg_counter = 0
        for i, var in enumerate(best_variables):
            distances = np.array(
                [part.variables[i] - var for part in self.particles.values()]
            )
            mean_distances = np.mean(np.abs(distances))

            if mean_distances <= self.data_reader.optimization_data.get("tolerance"):
                converg_counter += 1

        if converg_counter == len(best_variables):
            return True

        return False

    def __check_constrainsts(self):
        """
        Method responsible for checking
        if the constraints are valid, if
        not, a penalty is applied in the
        FO of the corresponding particle.
        """
        def penalize(fo: float) -> float:
            """
            Method responsible for penalizing
            the objective function if the
            constraints are not fullfiled.

            :param fo: objective function
            ...
            :return: new FO, penalized.
            """
            if fo > 1:
                penalty = np.random.uniform(1, fo)
            elif fo < 0:
                penalty = np.random.uniform(fo, 0)
            else:
                penalty = np.random.uniform(0, fo)

            return fo - penalty

        def check_fo_condition(fo: float) -> bool:
            """
            Method responsible for checking
            if the objective function is
            valid.

            :param fo: objective function
                value
            ...
            :return: True if the value is
                value
            """
            return True if (fo < 1) & (fo >= 0) else False

        def check_thickness_condition(x: np.ndarray) -> bool:
            """
            Method responsible for checking
            if the thickness values based
            on variables are valid.

            :param x: variables to optmize
            ...
            :return: True if the check is
                ok
            """
            condition = {False for id_ in range(len(x)) if x[0] > x[id_]}

            return False if condition else True

        for id_part, particle in self.particles.items():
            fo_condition = check_fo_condition(particle.objective_function)
            thickness_condition = check_thickness_condition(particle.variables)

            if (not fo_condition) or (not thickness_condition):
                new_fo = penalize(particle.objective_function)
                self.particles[id_part] = particle._replace(objective_function=new_fo)

    def __update_p_best(self):
        """
        Method responsible for updating
        the best particles in the best
        attribute.
        """
        for id_p, particle in self.particles.items():
            if particle.objective_function >= self.best_objective.get("p_best_obj").get(
                id_p
            ):
                self.best["p_best"][id_p] = particle
                self.best_objective["p_best_obj"][id_p] = particle.objective_function

    def __update_g_best(self):
        """
        Method responsible for updating
        the best particle in the best
        attribute.
        """
        part_obj = {p.objective_function: p_idx for p_idx, p in self.particles.items()}
        best_obj = max(part_obj.keys())
        best_part = part_obj.get(best_obj)

        if best_obj >= list(self.best["g_best"].values())[0].objective_function:
            self.best["g_best"] = {best_part: self.particles.get(best_part)}
            self.best_objective["g_best_obj"] = {
                best_part: self.particles.get(best_part)
            }

    def __update_velocity(self, t: int):
        """
        Method responsible for updating the
        velocity terms.

        :param t: the step iteration
        """
        for id_part, p_best_part in self.best.get("p_best").items():
            particle_variables = self.particles.get(id_part).variables
            p_best_variables = p_best_part.variables
            g_best_variables = list(self.best.get("g_best").values())[0].variables

            new_velocity = (
                self.hyperparameters.get("c1")(t)
                * self.hyperparameters.get("r")[0]
                * (p_best_variables - particle_variables)
            ) + (
                self.hyperparameters.get("c2")(t)
                * self.hyperparameters.get("r")[1]
                * (g_best_variables - particle_variables)
            )

            if id_part not in list(self.best.get("g_best").keys()):
                new_velocity += (
                    self.hyperparameters.get("w")(t)
                    * self.particles.get(id_part).velocity
                )

            self.particles[id_part] = self.particles.get(id_part)._replace(
                velocity=new_velocity
            )

    def __update_variables(self):
        """
        Method responsible for updating
        the particle variables.
        """
        for id_particle, particle in self.particles.items():
            new_position = particle.velocity + particle.variables

            self.particles[id_particle] = particle._replace(variables=new_position)

    def __update_objective_function(self):
        """
        Method responsible for updating the
        objective function of the variables.
        """
        obj_func_instance = ObjectiveFunction(
            airfoil_name=self.data_reader.propeller_geometric_conditions.get("airfoil"),
            particles=self.particles,
            flight_conditions=self.data_reader.flight_conditions,
            propeller_geometry=self.data_reader.propeller_geometric_conditions,
            uuid=self.uuid,
            xfoil_instances=self.data_reader.optimization_data.get("xfoilInstances"),
            airfoil_shape=self.data_reader.airfoil_geometry,
        )
        obj_func_instance.set_new_conditions()

        self.particles = obj_func_instance.particles

    def set_initial_conditions(self):
        """
        Method responsible for setting
        the initial conditions to run
        the optimizer.
        """
        init_cond_inst = ObjectiveFunction(
            airfoil_name=self.data_reader.propeller_geometric_conditions.get("airfoil"),
            particles=self.particles,
            flight_conditions=self.data_reader.flight_conditions,
            propeller_geometry=self.data_reader.propeller_geometric_conditions,
            uuid=self.uuid,
            xfoil_instances=self.data_reader.optimization_data.get("xfoilInstances"),
            airfoil_shape=self.data_reader.airfoil_geometry,
        )
        init_cond_inst.set_initial_conditions()

        self.particles = init_cond_inst.particles

        self.__check_constrainsts()
        self.__update_p_best()
        self.__update_g_best()
        self.__update_velocity(1)
        self.__update_variables()

        self.fo_per_time[1] = list(self.best["g_best"].values())[0].objective_function
        self.results_per_time[1] = self.particles.copy()

    def iterate(self):
        """
        Method responsible for iterating
        the optimizer.
        """
        for t in tqdm(
            range(2, self.data_reader.optimization_data.get("maximumIterations") + 1)
        ):
            self.__update_objective_function()
            self.__check_constrainsts()
            self.__update_p_best()
            self.__update_g_best()

            self.fo_per_time[t] = list(self.best["g_best"].values())[
                0
            ].objective_function
            self.results_per_time[t] = self.particles.copy()

            if self.__check_convergence():
                break
            self.__update_velocity(t)
            self.__update_variables()

            os.system("cls")
