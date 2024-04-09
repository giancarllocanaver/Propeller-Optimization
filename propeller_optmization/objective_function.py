from typing import Dict

import numpy as np

from .utilities.geometry_management import GeometryManagement
from .data_structures import Particle
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

    def set_initial_conditions(self):
        self.__create_bezier_initial_points()
        self.__set_initial_variables()
        self.__calculate_objective_function()

    def __create_bezier_initial_points(self):
        self.p_points = self.geometry_management.create_base_airfoil(self.airfoil_name)
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

    def __set_initial_variables(self):
        def choose_random_parameter(section: int):
            lb, ub = LIMITS_FOR_RANDOM_PROPELLER_SECTION_CHOOSE.get(section)

            return np.random.uniform(low=lb, high=ub)

        def create_initial_variables(particle: Particle):
            propeller_splines = list()
            parameters = list()

            for propeller_section in range(7):
                a = self.a_points.copy()

                while True:
                    parameter = choose_random_parameter(propeller_section)
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
                {particle: create_initial_variables(self.particles.get(particle))}
            )

    def __calculate_objective_function(self):
        def create_airfoil_files(particles: Dict[int, Particle]):
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
        
        def execute_the_blade_element_theory(particle_id: int, airfoil_names: dict):
            blade_instance = BladeElementTheory(
                uuid=self.uuid,
                airfoils=airfoil_names,
                flight_conditions=self.flight_conditions,
                propeller_geometric_conditions=self.propeller_geometry,
                xfoil_instances=self.xfoil_instances,
            )
            results = blade_instance.calculate_propeller_results()

            self.particles[particle_id] = self.particles[particle_id]._replace(
                objective_function=results.get("efficiency"),
                results=results
            )

        airfoil_names = create_airfoil_files(self.particles)

        for particle in self.particles:
            execute_the_blade_element_theory(particle, airfoil_names.get(particle))
