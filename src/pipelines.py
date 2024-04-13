import argparse
import uuid
import os
import logging
import shutil

from .data_modules.data_reader import DataReader
from .utilities.custom_logger import CustomLogger
from .optimizer import PSO
from .output_process import OutputProcess


class PipelineMethods:
    def __init__(self, parsed_arguments: argparse.Namespace) -> None:
        self.parsed_arguments = parsed_arguments
        self.uuid = str(uuid.uuid4())
        self.results_dir = os.path.join(parsed_arguments.output, self.uuid)
        self.data_reader = DataReader(self.parsed_arguments)

        self.__clean_old_data()
        self.__create_folders()
        self.__create_logger()

    def __clean_old_data(self):
        """
        Method responsible for cleaning purge
        data.
        """
        for file in os.listdir("processing/execution_steps"):
            if file == ".gitkeep":
                continue

            os.remove(os.path.join("processing", "execution_steps", file))

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
        self.logger.start("Read data")

        self.data_reader.process_data_reader_pipeline()

        self.logger.end("Read data")

    def create_xfoil_instances(self) -> None:
        """
        Method responsible for creating new
        instances of xfoil.
        """
        self.logger.start("Create xfoil instances")

        dir_base = os.path.join(
            os.getcwd(),
            "processing",
            "xfoil_instances",
        )
        xfoil_base = os.path.join(
            dir_base,
            "xfoil.exe",
        )
        quantity_of_instances = self.data_reader.optimization_data.get("xfoilInstances")

        for i in range(quantity_of_instances):
            shutil.copy(xfoil_base, os.path.join(dir_base, f"xfoil_{i}.exe"))

        self.logger.end("Create xfoil instances")

    def optimize(self):
        """
        Method responsible to start the optimization
        of the propeller.
        """
        self.logger.start("Optimization")

        optimization_instance = PSO(
            data_reader=self.data_reader,
            uuid=self.uuid,
            results_dir=self.results_dir,
        )
        optimization_instance.set_initial_conditions()
        optimization_instance.iterate()

        self.opt_inst = optimization_instance

        self.logger.end("Optimization")

    def obtain_results(self):
        """
        Method responsible for making the plots of
        the results.
        """
        self.logger.start("Making results")

        output_instance = OutputProcess(
            self.uuid, self.opt_inst, self.results_dir, self.data_reader
        )
        output_instance.process_outputs()

        self.logger.end("Making results")
