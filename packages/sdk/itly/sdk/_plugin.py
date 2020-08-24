import abc
from abc import abstractmethod
from typing import Optional

import six

from ._event import Event
from ._logger import Logger
from ._plugin_options import PluginOptions
from ._properties import Properties
from ._validation_response import ValidationResponse


@six.add_metaclass(abc.ABCMeta)
class Plugin(object):
    @abstractmethod
    def id(self):
        # type: () -> str
        pass

    # Tracking methods

    def load(self, options):
        # type: (PluginOptions) -> None
        pass

    def alias(self, user_id, previous_id):
        # type: (str, Optional[str]) -> None
        pass

    def identify(self, user_id, properties):
        # type: (str, Optional[Properties]) -> None
        pass

    def group(self, user_id, group_id, properties):
        # type: (str, str, Optional[Properties]) -> None
        pass

    def page(self, user_id, category, name, properties):
        # type: (str, Optional[str], Optional[str], Optional[Properties]) -> None
        pass

    def track(self, user_id, event):
        # type: (str, Event) -> None
        pass

    # Validation methods

    def validate(self, event):
        # type: (Event) -> ValidationResponse
        return ValidationResponse.ok()

    def validation_error(self, validation, event):
        # type: (ValidationResponse, Event) -> None
        pass

    def flush(self):
        # type: () -> None
        pass

    def shutdown(self):
        # type: () -> None
        pass


class PluginSafeDecorator(Plugin):
    def __init__(self, plugin, logger):
        # type: (Plugin, Logger) -> None
        self._plugin = plugin
        self._logger = logger

    def id(self):
        # type: () -> str
        return self._plugin.id()

    # Tracking methods

    def load(self, options):
        # type: (PluginOptions) -> None
        try:
            self._plugin.load(options)
        except Exception as e:
            self._logger.error('Error in {0}.load(). {1}.'.format(self._plugin.id(), str(e)))

    def alias(self, user_id, previous_id):
        # type: (str, Optional[str]) -> None
        try:
            self._plugin.alias(user_id, previous_id)
        except Exception as e:
            self._logger.error('Error in {0}.alias(). {1}.'.format(self._plugin.id(), str(e)))

    def identify(self, user_id, properties):
        # type: (str, Optional[Properties]) -> None
        try:
            self._plugin.identify(user_id, properties)
        except Exception as e:
            self._logger.error('Error in {0}.identify(). {1}.'.format(self._plugin.id(), str(e)))

    def group(self, user_id, group_id, properties):
        # type: (str, str, Optional[Properties]) -> None
        try:
            self._plugin.group(user_id, group_id, properties)
        except Exception as e:
            self._logger.error('Error in {0}.group(). {1}.'.format(self._plugin.id(), str(e)))

    def page(self, user_id, category, name, properties):
        # type: (str, Optional[str], Optional[str], Optional[Properties]) -> None
        try:
            self._plugin.page(user_id, category, name, properties)
        except Exception as e:
            self._logger.error('Error in {0}.page(). {1}.'.format(self._plugin.id(), str(e)))

    def track(self, user_id, event):
        # type: (str, Event) -> None
        try:
            self._plugin.track(user_id, event)
        except Exception as e:
            self._logger.error('Error in {0}.track(). {1}.'.format(self._plugin.id(), str(e)))

    # Validation methods

    def validate(self, event):
        # type: (Event) -> ValidationResponse
        try:
            return self._plugin.validate(event)
        except Exception as e:
            self._logger.error('Error in {0}.validate(). {1}.'.format(self._plugin.id(), str(e)))
            return ValidationResponse.error(plugin_id=self.id(), message=str(e))

    def validation_error(self, validation, event):
        # type: (ValidationResponse, Event) -> None
        try:
            self._plugin.validation_error(validation, event)
        except Exception as e:
            self._logger.error('Error in {0}.validation_error(). {1}.'.format(self._plugin.id(), str(e)))

    def flush(self):
        # type: () -> None
        try:
            self._plugin.flush()
        except Exception as e:
            self._logger.error('Error in {0}.flush(). {1}.'.format(self._plugin.id(), str(e)))

    def shutdown(self):
        # type: () -> None
        try:
            self._plugin.shutdown()
        except Exception as e:
            self._logger.error('Error in {0}.shutdown(). {1}.'.format(self._plugin.id(), str(e)))
