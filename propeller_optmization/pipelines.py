import argparse
import uuid
import os
import logging

from .data_reader import DataReader
from .utilities.custom_logger import CustomLogger
from .optimizer import PSO


class PipelineMethods:
    def __init__(self, parsed_arguments: argparse.Namespace) -> None:
        self.parsed_arguments = parsed_arguments
        self.uuid = str(uuid.uuid4())
        self.results_dir = os.path.join(parsed_arguments.output, self.uuid)
        self.data_reader = DataReader(self.parsed_arguments)

        self.__create_folders()
        self.__create_logger()

    def __create_folders(self) -> None:
        """
        Method responsible for creating the
        output folder of the input.
        """
        os.makedirs(self.results_dir, exist_ok=True)

    def __create_logger(self) -> None:
        """
        Method responsible for creating the
        logger object.
        """
        self.logger = CustomLogger(
            name=f"Propeller-Optimization {self.uuid}",
            level=logging.INFO,
            file_dir=os.path.join(self.results_dir, f"processing_{self.uuid}.log"),
        )

    def read_data(self) -> None:
        """
        Method responsible for reading the
        input file.
        """
        self.data_reader.process_data_reader_pipeline()

    def optimize(self):
        """
        Method responsible to start the optimization
        of the propeller.
        """
        optimization_instance = PSO(
            data_reader=self.data_reader,
            results_dir=self.results_dir,
        )
