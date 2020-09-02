from typing import NamedTuple

from ._environment import Environment
from ._logger import Logger


PluginLoadOptions = NamedTuple('PluginLoadOptions', [('environment', Environment), ('logger', Logger)])
