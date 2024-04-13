import logging
from time import time


class CustomLogger(logging.Logger):
    def __init__(self, name: str, level: int, file_dir: str):
        super().__init__(name, level)

        self.addHandler(logging.StreamHandler())
        self.addHandler(logging.FileHandler(file_dir))

    def start(self, info: str) -> None:
        """
        Method responsible to write a beggining information
        in the log and print the message along the execution.
        """
        _time = time()
        _info = info.lower()

        try:
            self.timed_infos  # type_ignore
        except AttributeError:
            self.timed_infos = dict()

        self.timed_infos[_info] = _time

        complete_message = f"Beggining {_info}"
        self.info(complete_message)

    def info_msg(self, info: str) -> None:
        """
        Method responsible to write an information message
        in the log and print the message along the execution.
        """
        self.info(info.lower())

    def end(self, info: str) -> None:
        """
        Method responsible to write an end information message
        in the log and print It along the execution.
        """
        _info = info.lower()
        _total_time = time() - self.timed_infos.get(_info)

        complete_message = f">>> Executed {_info} in {_total_time} s"
        self.info(complete_message)

        del self.timed_infos[_info]
