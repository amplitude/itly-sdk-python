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
        # type: (str, str) -> None
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

    def flush(self):
        # type: () -> None
        pass

    def shutdown(self):
        # type: () -> None
        pass

    # Validation methods

    def validate(self, event):
        # type: (Event) -> ValidationResponse
        return self._create_valid_response()

    def on_validation_error(self, validation, event):
        # type: (ValidationResponse, Event) -> None
        pass

    def _create_valid_response(self):
        # type: () -> ValidationResponse
        return ValidationResponse(valid=True, plugin_id=self.id(), message='')

    def _create_invalid_response(self, message):
        # type: (str) -> ValidationResponse
        return ValidationResponse(valid=False, plugin_id=self.id(), message=message)


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
        self._logger.info('load()')
        try:
            self._plugin.load(options)
        except Exception as e:
            self._logger.error('Error in load(). {0}.'.format(str(e)))

    def alias(self, user_id, previous_id):
        # type: (str, str) -> None
        self._logger.info('alias(user_id={0}, previous_id={1})'.format(user_id, previous_id))
        try:
            self._plugin.alias(user_id, previous_id)
        except Exception as e:
            self._logger.error('Error in alias(). {0}.'.format(str(e)))

    def identify(self, user_id, properties):
        # type: (str, Optional[Properties]) -> None
        self._logger.info('identify(user_id={0}, properties={1})'.format(user_id, properties))
        try:
            self._plugin.identify(user_id, properties)
        except Exception as e:
            self._logger.error('Error in identify(). {0}.'.format(str(e)))

    def group(self, user_id, group_id, properties):
        # type: (str, str, Optional[Properties]) -> None
        self._logger.info('group(user_id={0}, group_id={1}, properties={2})'.format(user_id, group_id, properties))
        try:
            self._plugin.group(user_id, group_id, properties)
        except Exception as e:
            self._logger.error('Error in group(). {0}.'.format(str(e)))

    def page(self, user_id, category, name, properties):
        # type: (str, Optional[str], Optional[str], Optional[Properties]) -> None
        self._logger.info('page(user_id={0}, category={1}, name={2}, properties={3})'.format(user_id, category, name, properties))
        try:
            self._plugin.page(user_id, category, name, properties)
        except Exception as e:
            self._logger.error('Error in page(). {0}.'.format(str(e)))

    def track(self, user_id, event):
        # type: (str, Event) -> None
        self._logger.info('track(user_id={0}, event={1}, properties={2})'.format(user_id, event.name, event.properties))
        try:
            self._plugin.track(user_id, event)
        except Exception as e:
            self._logger.error('Error in track(). {0}.'.format(str(e)))

    def flush(self):
        # type: () -> None
        self._logger.info('flush()')
        try:
            self._plugin.flush()
        except Exception as e:
            self._logger.error('Error in flush(). {0}.'.format(str(e)))

    def shutdown(self):
        # type: () -> None
        self._logger.info('shutdown()')
        try:
            self._plugin.shutdown()
        except Exception as e:
            self._logger.error('Error in shutdown(). {0}.'.format(str(e)))

    # Validation methods

    def validate(self, event):
        # type: (Event) -> ValidationResponse
        self._logger.info('validate(event={0}, properties={1})'.format(event.name, event.properties))
        try:
            return self._plugin.validate(event)
        except Exception as e:
            self._logger.error('Error in validate(). {0}.'.format(str(e)))
            return self._create_invalid_response(message=str(e))

    def on_validation_error(self, validation, event):
        # type: (ValidationResponse, Event) -> None
        try:
            self._plugin.on_validation_error(validation, event)
        except Exception as e:
            self._logger.error('Error in on_validation_error(). {0}.'.format(str(e)))
