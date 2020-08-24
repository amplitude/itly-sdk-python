from __future__ import print_function
from abc import abstractmethod, ABCMeta
import sys

import six


@six.add_metaclass(ABCMeta)
class Logger(object):
    STD_OUT_AND_ERR = None  # type: Logger
    NONE = None  # type: Logger

    @abstractmethod
    def debug(self, message):
        # type: (str) -> None
        pass

    @abstractmethod
    def info(self, message):
        # type: (str) -> None
        pass

    @abstractmethod
    def warn(self, message):
        # type: (str) -> None
        pass

    @abstractmethod
    def error(self, message):
        # type: (str) -> None
        pass


class StdOutAndErrLogger(Logger):
    def debug(self, message):
        # type: (str) -> None
        print(message)

    def info(self, message):
        # type: (str) -> None
        print(message)

    def warn(self, message):
        # type: (str) -> None
        print(message)

    def error(self, message):
        # type: (str) -> None
        print(message, file=sys.stderr)


class NoneLogger(Logger):
    def debug(self, message):
        # type: (str) -> None
        pass

    def info(self, message):
        # type: (str) -> None
        pass

    def warn(self, message):
        # type: (str) -> None
        pass

    def error(self, message):
        # type: (str) -> None
        pass


Logger.STD_OUT_AND_ERR = StdOutAndErrLogger()
Logger.NONE = NoneLogger()


class LoggerPrefixSafeDecorator(Logger):
    def __init__(self, logger, prefix):
        # type: (Logger, str) -> None
        self._logger = logger
        self._prefix = prefix

    def debug(self, message):
        # type: (str) -> None
        try:
            self._logger.debug(self._prefix + message)
        except Exception as e:
            print(self._prefix + 'Error in logger.debug(). {0}.'.format(str(e)), file=sys.stderr)

    def info(self, message):
        # type: (str) -> None
        try:
            self._logger.info(self._prefix + message)
        except Exception as e:
            print(self._prefix + 'Error in logger.info(). {0}.'.format(str(e)), file=sys.stderr)

    def warn(self, message):
        # type: (str) -> None
        try:
            self._logger.warn(self._prefix + message)
        except Exception as e:
            print(self._prefix + 'Error in logger.warn(). {0}.'.format(str(e)), file=sys.stderr)

    def error(self, message):
        # type: (str) -> None
        try:
            self._logger.error(self._prefix + message)
        except Exception as e:
            print(self._prefix + 'Error in logger.error(). {0}.'.format(str(e)), file=sys.stderr)
