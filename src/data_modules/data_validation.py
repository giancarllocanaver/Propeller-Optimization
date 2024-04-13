import os
from typing import Union

from ..utilities.exceptions import *
from ..utilities.constants import *


class DataValidation:
    def __init__(self) -> None:
        pass

    def check_file_existance(self, directory: str) -> None:
        """
        Method responsible for checking the file existance.
        If the file is not found, an error will be raised.

        :param directory: complete file directory
        """
        if not os.path.isfile(directory):
            raise FileNotFound(
                "There is no file or directory with the current name: {file}".format(
                    file=directory
                )
            )

    def check_file_extension(self, file: str) -> None:
        """
        Method responsible for checking the file extension.
        If the extension is not valid, an error will be raised.

        :param file: file name with its extension
        """
        extension = file.split(".")[-1]

        if not extension == "json":
            raise FileExtensionError(
                "The file in the directory {file} must be a json file!".format(
                    file=file
                )
            )

    def check_json_keys(self, data: dict) -> None:
        """
        Method responsible for checking the json keys of the
        file, if the keys are matched with the expected.

        If any key which is not matched is found, an error
        will be raised.

        :param data: input data
        """
        primary_keys = [key for key in INPUT_SCHEMA if key not in data]
        if primary_keys:
            raise MissingKeysError(
                "Missing the current keys in the input file:\n"
                + ", ".join(primary_keys)
            )

        secondary_keys = [
            second_key
            for first_key in INPUT_SCHEMA
            for second_key in INPUT_SCHEMA.get(first_key)
            if second_key not in data.get(first_key)
        ]
        if secondary_keys:
            raise MissingKeysError(
                "Missing the current keys in the input file:\n"
                + ", ".join(primary_keys)
            )

    def check_data_dtypes(self, data: dict) -> None:
        """
        Method responsible for checking the data dtypes.
        If a not matched datatype is found, an error will be raised.

        :param data: input data
        """
        error_data_types = [
            second_key
            for first_key in INPUT_SCHEMA
            for second_key in INPUT_SCHEMA.get(first_key)
            if type(data.get(first_key).get(second_key))
            != INPUT_SCHEMA.get(first_key).get(second_key)
        ]
        if error_data_types:
            ErrorDtypeKeys(
                "Error in dtype format with the current keys:\n"
                + ", ".join(error_data_types)
            )

    def check_airfoil_shape(self, data: Union[dict, None]) -> None:
        """
        Method responsible for checking if the airfoil data shape
        agrees.

        :param data: P points of the airfoil passed in the input.
        """
        if data is None:
            return

        if not "xPoints" in data:
            raise MissingKeysError("There is no key called 'xPoints'")

        if not "yPoints" in data:
            raise MissingKeysError("There is no key called 'yPoints'")

        if (len(data.get("xPoints")) != 5) or (len(data.get("yPoints")) != 5):
            raise ErrorAirfoilShape("The lenght of the airfoil shape is not 5!")
