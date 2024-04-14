from typing import Dict

import numpy as np

from .utilities.geometry_management import GeometryManagement
from .data_modules.data_structures import Particle
from .utilities.constants import (
    LIMITS_FOR_RANDOM_PROPELLER_SECTION_CHOOSE,
)
from .utilities.airfoil_creation import AirfoilCreation
from .blade_element_theory import BladeElementTheory


class ObjectiveFunction:
    def __init__(
        self,
        airfoil_name: str,
        particles: Dict[int, Particle],
        flight_conditions: dict,
        propeller_geometry: dict,
        uuid: str,
        **kwargs
    ):
        self.airfoil_name = airfoil_name
        self.particles = particles
        self.flight_conditions = flight_conditions
        self.propeller_geometry = propeller_geometry
        self.uuid = uuid
        self.airfoil_shape = kwargs.get("airfoil_shape", None)
        self.xfoil_instances = kwargs.get("xfoil_instances", 1)

        self.geometry_management = GeometryManagement()
        self.p_points = None

    def set_initial_conditions(self) -> None:
        """
        Method responsible for calling the functions which
        will instantiate new properties to each particle
        and calculate the objective function value.
        """
        self.__create_bezier_initial_points()
        self.__set_initial_variables()
        self.__calculate_objective_function()

    def set_new_conditions(self) -> None:
        """
        Method responsible for setting a new condition to
        update the objective function value.
        """
        self.__update_geometry()
        self.__calculate_objective_function()

    def __create_bezier_initial_points(self) -> None:
        """
        Method responsible for creating the bezier points
        based on the airfoil passed in the input.
        """
        self.p_points = self.geometry_management.create_base_airfoil(
            self.airfoil_name, self.airfoil_shape
        )
        self.a_points = self.geometry_management.generate_bezier_points()

        for particle_id, particle in self.particles.items():
            self.particles.update(
                {
                    particle_id: particle._replace(
                        points_p=self.p_points,
                        points_a=self.a_points,
                    )
                }
            )

    def __set_initial_variables(self) -> None:
        """
        Method responsible for setting the initial variables,
        related to a number value added to one bezier point.
        """

        def choose_random_variable(section: int) -> float:
            """
            Method responsible for choosing a ramdom parameter,
            according to the section blade, which is used as the
            initial variable for the optimization.

            :param section: section of the blade
            ...
            :return: a random number used as the initial variable
                for the optimization
            """
            lb, ub = LIMITS_FOR_RANDOM_PROPELLER_SECTION_CHOOSE.get(section)

            return np.random.uniform(low=lb, high=ub)

        def create_initial_geometry(particle: Particle) -> Particle:
            """
            Method responsible for creating the initial blade
            geometry of each particle, considering the control
            variable choosed by an initial random process.

            :param particle: the particle which will be created
                the geometry.
            """
            propeller_splines = list()
            parameters = list()

            for propeller_section in range(7):
                a = self.a_points.copy()

                while True:
                    parameter = choose_random_variable(propeller_section)
                    a[1][3] = self.a_points[1][3] + parameter

                    geometry_management = GeometryManagement()
                    splines = geometry_management.update_airfoil(
                        a_points=a, p_points=self.p_points.copy()
                    )

                    if splines is not None:
                        break

                propeller_splines.append(splines)
                parameters.append(parameter)

            return particle._replace(
                variables=np.array(parameters), splines=propeller_splines
            )

        particles_ids = self.particles.keys()
        for particle in particles_ids:
            self.particles.update(
                {particle: create_initial_geometry(self.particles.get(particle))}
            )

    def __update_geometry(self) -> None:
        """
        Method responsible for updating the geometry
        of each Particle, based on new variable
        values.
        """

        def change_splines(particle: Particle) -> Particle:
            """
            Method responsible for changing the
            spline of the geometry of each
            Particle.

            :param particle: the particle which
                it splines will be updated.
            """
            prop_splines = list()

            for section in range(7):
                a_points = particle.points_a.copy()
                a_points[1][3] = a_points[1][3] + particle.variables[section]

                geometry_manag_instance = GeometryManagement()
                splines = geometry_manag_instance.update_airfoil(
                    a_points=a_points, p_points=particle.points_p
                )

                prop_splines.append(splines)

            return particle._replace(splines=prop_splines)

        particle_ids = self.particles.keys()
        for particle_id in particle_ids:
            self.particles.update(
                {particle_id: change_splines(self.particles.get(particle_id))}
            )

    def __calculate_objective_function(self) -> None:
        """
        Methdod responsible for calculating the objective
        function of each particle.
        """

        def create_airfoil_files(particles: Dict[int, Particle]) -> dict:
            """
            Method responsible for creating the airfoil files
            which will be used by xfoil to calculate the obje-
            ctive funcion.

            :param particles: dict of particles
            ...
            :return:: airfoil files per particle per section
                blade.
            """
            airfoil_file_names = {
                id_particle: {
                    section: AirfoilCreation.create_airfoil_in_xfoil_from_splines(
                        particle.splines[section],
                    )
                    for section in range(len(particle.splines))
                }
                for id_particle, particle in particles.items()
            }

            return airfoil_file_names

        def execute_the_blade_element_theory(
            particle_id: int, airfoil_names: dict
        ) -> None:
            """
            Method responsible for executing the blade element
            theory for obtaining the objective function value
            of each particle.

            :param particle_id: particle id
            :param airfoil_names: airfoil files of each
                particle of each section
            """
            blade_instance = BladeElementTheory(
                uuid=self.uuid,
                airfoils=airfoil_names,
                flight_conditions=self.flight_conditions,
                propeller_geometric_conditions=self.propeller_geometry,
                xfoil_instances=self.xfoil_instances,
            )
            results = blade_instance.calculate_propeller_results()

            self.particles[particle_id] = self.particles[particle_id]._replace(
                objective_function=results.get("efficiency"), results=results
            )

        airfoil_names = create_airfoil_files(self.particles)

        for particle in self.particles:
            execute_the_blade_element_theory(particle, airfoil_names.get(particle))
