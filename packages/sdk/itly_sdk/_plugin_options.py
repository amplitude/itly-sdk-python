from typing import NamedTuple

from ._environment import Environment
from ._logger import Logger


class PluginLoadOptions(NamedTuple):
    environment: Environment
    logger: Logger
