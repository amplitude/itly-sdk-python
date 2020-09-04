from typing import Optional, List, NamedTuple

from ._environment import Environment
from ._logger import Logger
from ._plugin import Plugin
from ._properties import Properties
from ._validation_options import ValidationOptions


class Options(NamedTuple):
    environment: Environment = Environment.DEVELOPMENT
    disabled: bool = False
    plugins: List[Plugin] = []
    context: Optional[Properties] = None
    validation: Optional[ValidationOptions] = None
    logger: Logger = Logger.NONE
