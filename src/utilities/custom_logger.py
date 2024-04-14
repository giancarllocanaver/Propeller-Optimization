import logging
from time import time


class CustomLogger(logging.Logger):
    def __init__(self, name: str, level: int, file_dir: str):
        super().__init__(name, level)

        self.addHandler(logging.StreamHandler())
        self.addHandler(logging.FileHandler(file_dir))

    def start(self, info: str) -> None:
        """
        Method responsible for writing a beggining information
        in the log and print the message along the execution.

        :param info: message to be streamed
        """
        _time = time()
        _info = info.lower()

        try:
            self.timed_infos  # type_ignore
        except AttributeError:
            self.timed_infos = dict()

        self.timed_infos[_info] = _time

        complete_message = f"Starting {_info}"
        self.info(complete_message)

    def info_msg(self, info: str) -> None:
        """
        Method responsible for writing an information message
        in the log and print the message along the execution.

        :param info: information message to be written
        """
        self.info(info.lower())

    def end(self, info: str) -> None:
        """
        Method responsible for writing an end information message
        in the log and print it along the execution.

        :param info: information message to be written
        """
        _info = info.lower()
        _total_time = time() - self.timed_infos.get(_info)

        complete_message = f">>> Executed {_info} in {_total_time} s\n\n"
        self.info(complete_message)

        del self.timed_infos[_info]
