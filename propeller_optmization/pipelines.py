import argparse
import uuid
import os
import logging

from .data_reader import DataReader
from .utilities.custom_logger import CustomLogger

class PipelineMethods:
    def __init__(self, parsed_arguments: argparse.Namespace) -> None:
        self.parsed_arguments = parsed_arguments
        
        self.logger = None

        self.uuid = str(uuid.uuid4())
        self.airfoil_coordinates_dir = "processing/airfoils_coordinates"
        self.results_dir = parsed_arguments.output + "/" + self.uuid
        self.data_reader = DataReader(self.parsed_arguments)        

    def create_folders(self):
        os.makedirs(self.airfoil_coordinates_dir, exist_ok=True)
        os.makedirs(self.results_dir, exist_ok=True)

    def create_logger(self):
        self.logger = CustomLogger(
            name=f"Propeller-Optimization {self.uuid}",
            level=logging.INFO
        )
        self.logger.addHandler(logging.StreamHandler())
        self.logger.addHandler(
            logging.FileHandler(self.results_dir + "/" + f"processing_{self.uuid}.log")
        )

    def read_data(self):
        self.data_reader.process_data_reader_pipeline()


        

