from typing import Optional, List, NamedTuple

from ._environment import Environment
from ._logger import Logger
from ._plugin import Plugin
from ._validation_options import ValidationOptions


class Options:
    def __init__(self,
                 environment: Environment = Environment.DEVELOPMENT,
                 disabled: bool = False,
                 plugins: Optional[List[Plugin]] = None,
                 validation: Optional[ValidationOptions] = None,
                 logger: Logger = Logger.NONE
                 ):
        self._environment: Environment = environment
        self._disabled: bool = disabled
        self._plugins: List[Plugin] = plugins if plugins is not None else []
        self._validation = validation if validation is not None else ValidationOptions(
            track_invalid=environment == Environment.PRODUCTION,
            error_on_invalid=environment != Environment.PRODUCTION,
        )
        self._logger: Logger = logger

    @property
    def environment(self) -> Environment:
        return self._environment

    @property
    def disabled(self) -> bool:
        return self._disabled

    @property
    def plugins(self) -> List[Plugin]:
        return self._plugins

    @property
    def validation(self) -> ValidationOptions:
        return self._validation

    @property
    def logger(self) -> Logger:
        return self._logger

    def with_overrides(self,
                       environment: Optional[Environment] = None,
                       disabled: Optional[bool] = None,
                       plugins: Optional[List[Plugin]] = None,
                       validation: Optional[ValidationOptions] = None,
                       logger: Logger = None
                       ) -> "Options":
        return Options(
            environment if environment is not None else self._environment,
            disabled if disabled is not None else self._disabled,
            plugins if plugins is not None else self._plugins,
            validation if validation is not None else self._validation,
            logger if logger is not None else self._logger,
        )
