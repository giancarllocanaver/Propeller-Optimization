import numpy as np
from propeller_optmization.utilities import geometry_management

from propeller_optmization.utilities.geometry_management import GeometryManagement
from propeller_optmization.data_structures import Particle
from propeller_optmization.utilities.constants import LIMITS_FOR_RANDOM_PROPELLER_SECTION_CHOOSE


class ObjectiveFunction:
    def __init__(self, airfoil_name: str, particles: dict, conditions: dict):
        self.airfoil_name = airfoil_name
        self.particles = particles
        self.conditions = conditions

        self.geometry_management = GeometryManagement()
        self.p_points = None

    def set_initial_conditions(self):
        self._create_bezier_initial_points()
        self._set_initial_variables()
        self._calculate_objective_function()

    def _create_bezier_initial_points(self):
        self.p_points = self.geometry_management.create_base_airfoil(self.airfoil_name)
        self.a_points = self.geometry_management.generate_bezier_points()

    def _set_initial_variables(self):
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
                    a[1][3][0] = self.a_points[1][3][0] + parameter

                    geometry_management = GeometryManagement()
                    splines = geometry_management.update_airfoil(
                        a_points=a,
                        p_points=self.p_points.copy()
                    )

                    if splines is not None:
                        break
                
                propeller_splines.append(splines)
                parameters.append(parameter)
            
            return particle._replace(
                variables=np.array(parameters),
                splines=propeller_splines
            )
        
        particles_ids = self.particles.keys()
        for particle in particles_ids:
            self.particles.update(
                {
                    particle: create_initial_variables(
                        self.particles.get(particle)
                    )
                }
            )

    def _calculate_objective_function(self):
        pass