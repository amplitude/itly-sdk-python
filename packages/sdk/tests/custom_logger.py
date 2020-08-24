from typing import List

from itly.sdk import Logger


class CustomLogger(Logger):
    def __init__(self, log_lines):
        # type: (List[str]) -> None
        self.log_lines = log_lines

    def debug(self, message):
        # type: (str) -> None
        self.log_lines.append(message)

    def info(self, message):
        # type: (str) -> None
        self.log_lines.append(message)

    def warn(self, message):
        # type: (str) -> None
        self.log_lines.append(message)

    def error(self, message):
        # type: (str) -> None
        self.log_lines.append(message)
