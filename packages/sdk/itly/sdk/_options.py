from typing import Optional, List

from ._environment import Environment
from ._logger import Logger
from ._plugin import Plugin
from ._properties import Properties
from ._validation_options import ValidationOptions


class Options(object):
    def __init__(
            self,
            environment=Environment.DEVELOPMENT,
            disabled=False,
            plugins=None,
            context=None,
            validation=None,
            logger=Logger.NONE
    ):
        # type: (Environment, bool, Optional[List[Plugin]], Optional[Properties], Optional[ValidationOptions], Logger) -> None
        """Itly Options

        :param environment: The current environment (development or production). Default is development.
        :param disabled: Whether calls to the Itly SDK should be no-ops. Default is false.
        :param plugins: Extend the itly sdk by adding plugins for common analytics trackers, validation and more.
        :param context: Additional context properties to add to all events. Default is none.
        :param validation: Configure validation handling
        :param logger: Logger. Default is no logging.
        """

        self.environment = environment  # type: Environment
        self.disabled = disabled  # type: bool
        self.plugins = plugins if plugins is not None else []  # type: List[Plugin]
        self.context = context  # type: Optional[Properties]
        self.validation = validation  # type: Optional[ValidationOptions]
        self.logger = logger  # type: Logger
