from abc import ABC, abstractmethod
import sys


class Logger(ABC):
    STD_OUT_AND_ERR: "Logger" = None  # type: ignore
    NONE: "Logger" = None  # type: ignore

    @abstractmethod
    def debug(self, message: str) -> None:
        pass

    @abstractmethod
    def info(self, message: str) -> None:
        pass

    @abstractmethod
    def warn(self, message: str) -> None:
        pass

    @abstractmethod
    def error(self, message: str) -> None:
        pass


class StdOutAndErrLogger(Logger):
    def debug(self, message: str) -> None:
        print(message)

    def info(self, message: str) -> None:
        print(message)

    def warn(self, message: str) -> None:
        print(message)

    def error(self, message: str) -> None:
        print(message, file=sys.stderr)


class NoneLogger(Logger):
    def debug(self, message: str) -> None:
        pass

    def info(self, message: str) -> None:
        pass

    def warn(self, message: str) -> None:
        pass

    def error(self, message: str) -> None:
        pass


Logger.STD_OUT_AND_ERR = StdOutAndErrLogger()
Logger.NONE = NoneLogger()


class LoggerPrefixSafeDecorator(Logger):
    def __init__(self, logger: Logger, prefix: str, fallback_logger: Logger = Logger.STD_OUT_AND_ERR):
        self._logger = logger
        self._prefix = prefix
        self._fallback_logger = fallback_logger

    def debug(self, message: str) -> None:
        try:
            self._logger.debug(self._prefix + message)
        except Exception as e:
            self._fallback_logger.debug(self._prefix + message)
            self._fallback_logger.error(self._prefix + f'Error in logger.debug(). {e}')

    def info(self, message: str) -> None:
        try:
            self._logger.info(self._prefix + message)
        except Exception as e:
            self._fallback_logger.info(self._prefix + message)
            self._fallback_logger.error(self._prefix + f'Error in logger.info(). {e}')

    def warn(self, message: str) -> None:
        try:
            self._logger.warn(self._prefix + message)
        except Exception as e:
            self._fallback_logger.warn(self._prefix + message)
            self._fallback_logger.error(self._prefix + f'Error in logger.warn(). {e}')

    def error(self, message: str) -> None:
        try:
            self._logger.error(self._prefix + message)
        except Exception as e:
            self._fallback_logger.error(self._prefix + message)
            self._fallback_logger.error(self._prefix + f'Error in logger.error(). {e}')
