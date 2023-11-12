from genericpath import isfile

import json
import argparse

from .exceptions import *
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
        Calling DataReader pipeline methods.
        """
        self._pre_reading_validation()
        self._read_data()
        self._post_reading_validation()
        self._instantiate_variables()

    def _pre_reading_validation(self):
        """
        Method responsible for validating the existance
        and the extennsion of the input file
        """
        self.validator.check_file_existance(self.argument_parser.file)
        self.validator.check_file_extension(self.argument_parser.file)
    
    def _read_data(self):
        """
        Method responsible for reading the json input
        file.
        """
        with open(self.argument_parser.file) as file:
            self.input_data = json.load(file)

    def _post_reading_validation(self):
        """
        Method responsible for validating post reading
        data.
        """
        self.validator.check_json_keys(self.input_data)
        self.validator.check_data_dtypes(self.input_data)

    def _instantiate_variables(self):
        """
        Method responsible for instantiating the main variables
        to the software.
        """
        self.optimization_data = self.input_data.get("optimization")
        self.flight_conditions = self.input_data.get("flightConditions")
        self.propeller_geometric_conditions = self.input_data.get("propellerGeometricConditions")
    