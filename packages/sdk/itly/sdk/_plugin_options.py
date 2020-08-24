from ._environment import Environment
from ._logger import Logger


class PluginOptions(object):
    def __init__(
            self,
            environment,
            logger=Logger.NONE
    ):
        # type: (Environment, Logger) -> None
        self.environment = environment  # type: Environment
        self.logger = logger  # type: Logger
