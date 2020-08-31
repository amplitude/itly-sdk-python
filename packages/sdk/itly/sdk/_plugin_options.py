from typing import NamedTuple

from ._environment import Environment
from ._logger import Logger


PluginOptions = NamedTuple('PluginOptions', [('environment', Environment), ('logger', Logger)])
