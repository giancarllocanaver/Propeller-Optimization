import argparse
import os
from argparse import ArgumentParser

from src.pipelines import PipelineMethods


def define_parser() -> dict:
    """
    Method responsible for creating the parser arguments
    for the main function.

    :return: argument parser
    """
    parser = ArgumentParser(
        prog="main.py",
        description="Propeller Optimization input and output arguments",
        usage="%(prog)s [-f] <file> [-o]",
    )

    parser.add_argument(
        "-f",
        "--file",
        type=str,
        help="Complete '.json' file directory containing the parameters of the optimizer in the processing folder ('processing/inputs')",
        required=True,
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        help="output directory for the output files",
        required=False,
        default=os.path.join(os.getcwd(), "processing", "outputs"),
    )

    return parser.parse_args()


def main(arguments_parsed: argparse.Namespace) -> None:
    """
    Main funtion of the propeller optimizer.

    :param arguments_parsed: arguments for
        starting the optimization.
    """
    pipeline = PipelineMethods(arguments_parsed)
    logger = pipeline.logger

    try:
        pipeline.read_data()
        pipeline.create_xfoil_instances()
        pipeline.optimize()
        pipeline.obtain_results()
    except Exception as e:
        logger.exception(e, stack_info=True)

        raise e


if __name__ == "__main__":
    arguments_parsed = define_parser()
    main(arguments_parsed)