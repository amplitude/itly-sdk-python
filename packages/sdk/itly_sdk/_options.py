from typing import Optional, List

from .internal import Options as ItlyOptions
from ._environment import Environment
from ._logger import Logger
from ._plugin import Plugin
from ._properties import Properties
from ._validation_options import ValidationOptions


class Options(ItlyOptions):
    def __init__(self,
                 context: Optional[Properties] = None,
                 environment: Environment = Environment.DEVELOPMENT,
                 disabled: bool = False,
                 plugins: Optional[List[Plugin]] = None,
                 validation: Optional[ValidationOptions] = None,
                 logger: Logger = Logger.NONE
                 ):
        super().__init__(
            environment=environment,
            disabled=disabled,
            plugins=plugins,
            validation=validation,
            logger=logger,
        )
        self._context: Optional[Properties] = context

    @property
    def context(self) -> Optional[Properties]:
        return self._context
