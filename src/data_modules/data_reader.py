import json
import argparse

from ..utilities.exceptions import *
from .data_validation import DataValidation


class DataReader:
    def __init__(self, arguments_parsed: argparse.Namespace) -> None:
        self.argument_parser = arguments_parsed

        self.input_data = dict()
        self.optimization_data = dict()
        self.flight_conditions = dict()
        self.propeller_geometric_conditions = dict()

        self.validator = DataValidation()

    def process_data_reader_pipeline(self):
        """
        Method responsible for calling the DataReader
        pipeline methods.
        """
        self.__pre_reading_validation()
        self.__read_data()
        self.__post_reading_validation()
        self.__instantiate_variables()
        self.__airfoil_shape_validation()

    def __pre_reading_validation(self):
        """
        Method responsible for validating the existance
        and the extennsion of the input file.
        """
        self.validator.check_file_existance(self.argument_parser.file)
        self.validator.check_file_extension(self.argument_parser.file)

    def __read_data(self):
        """
        Method responsible for reading the json input
        file.
        """
        with open(self.argument_parser.file) as file:
            self.input_data = json.load(file)

    def __post_reading_validation(self):
        """
        Method responsible for validating post reading
        data.
        """
        self.validator.check_json_keys(self.input_data)
        self.validator.check_data_dtypes(self.input_data)

    def __instantiate_variables(self):
        """
        Method responsible for instantiating the main variables
        to the software.
        """
        self.optimization_data = self.input_data.get("optimization")
        self.flight_conditions = self.input_data.get("flightConditions")
        self.propeller_geometric_conditions = self.input_data.get(
            "propellerGeometricConditions"
        )
        self.airfoil_geometry = self.input_data.get("airfoilGeometry", None)

    def __airfoil_shape_validation(self):
        """
        Method responsible for validating the
        airfoil shape, if passed in the input
        variables.
        """
        self.validator.check_airfoil_shape(self.airfoil_geometry)
