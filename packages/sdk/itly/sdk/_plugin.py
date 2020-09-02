import abc
from abc import abstractmethod
from datetime import datetime
from typing import Optional

import six

from ._event import Event
from ._logger import Logger
from ._plugin_options import PluginLoadOptions
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
        # type: (PluginLoadOptions) -> None
        pass

    def alias(self, user_id, previous_id, timestamp=None):
        # type: (str, str, Optional[datetime]) -> None
        pass

    def identify(self, user_id, properties, timestamp=None):
        # type: (str, Optional[Properties], Optional[datetime]) -> None
        pass

    def group(self, user_id, group_id, properties, timestamp=None):
        # type: (str, str, Optional[Properties], Optional[datetime]) -> None
        pass

    def page(self, user_id, category, name, properties, timestamp=None):
        # type: (str, Optional[str], Optional[str], Optional[Properties], Optional[datetime]) -> None
        pass

    def track(self, user_id, event, timestamp=None):
        # type: (str, Event, Optional[datetime]) -> None
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

    def on_validation_error(self, validation, event, timestamp=None):
        # type: (ValidationResponse, Event, Optional[datetime]) -> None
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
        # type: (PluginLoadOptions) -> None
        self._logger.info('load()')
        try:
            self._plugin.load(options)
        except Exception as e:
            self._logger.error('Error in load(). {0}.'.format(e))

    def alias(self, user_id, previous_id, timestamp=None):
        # type: (str, str, Optional[datetime]) -> None
        if self._plugin.__class__.alias != Plugin.alias:
            self._logger.info('alias(user_id={0}, previous_id={1})'.format(user_id, previous_id))
        try:
            self._plugin.alias(user_id, previous_id, timestamp)
        except Exception as e:
            self._logger.error('Error in alias(). {0}.'.format(e))

    def identify(self, user_id, properties, timestamp=None):
        # type: (str, Optional[Properties], Optional[datetime]) -> None
        if self._plugin.__class__.identify != Plugin.identify:
            self._logger.info('identify(user_id={0}, properties={1})'.format(user_id, properties))
        try:
            self._plugin.identify(user_id, properties, timestamp)
        except Exception as e:
            self._logger.error('Error in identify(). {0}.'.format(e))

    def group(self, user_id, group_id, properties, timestamp=None):
        # type: (str, str, Optional[Properties], Optional[datetime]) -> None
        if self._plugin.__class__.group != Plugin.group:
            self._logger.info('group(user_id={0}, group_id={1}, properties={2})'.format(user_id, group_id, properties))
        try:
            self._plugin.group(user_id, group_id, properties, timestamp)
        except Exception as e:
            self._logger.error('Error in group(). {0}.'.format(e))

    def page(self, user_id, category, name, properties, timestamp=None):
        # type: (str, Optional[str], Optional[str], Optional[Properties], Optional[datetime]) -> None
        if self._plugin.__class__.page != Plugin.page:
            self._logger.info('page(user_id={0}, category={1}, name={2}, properties={3})'.format(user_id, category, name, properties))
        try:
            self._plugin.page(user_id, category, name, properties, timestamp)
        except Exception as e:
            self._logger.error('Error in page(). {0}.'.format(e))

    def track(self, user_id, event, timestamp=None):
        # type: (str, Event, Optional[datetime]) -> None
        if self._plugin.__class__.track != Plugin.track:
            self._logger.info('track(user_id={0}, event={1}, properties={2})'.format(user_id, event.name, event.properties))
        try:
            self._plugin.track(user_id, event, timestamp)
        except Exception as e:
            self._logger.error('Error in track(). {0}.'.format(e))

    def flush(self):
        # type: () -> None
        if self._plugin.__class__.flush != Plugin.flush:
            self._logger.info('flush()')
        try:
            self._plugin.flush()
        except Exception as e:
            self._logger.error('Error in flush(). {0}.'.format(e))

    def shutdown(self):
        # type: () -> None
        if self._plugin.__class__.shutdown != Plugin.shutdown:
            self._logger.info('shutdown()')
        try:
            self._plugin.shutdown()
        except Exception as e:
            self._logger.error('Error in shutdown(). {0}.'.format(e))

    # Validation methods

    def validate(self, event):
        # type: (Event) -> ValidationResponse
        if self._plugin.__class__.validate != Plugin.validate:
            self._logger.info('validate(event={0}, properties={1})'.format(event.name, event.properties))
        try:
            return self._plugin.validate(event)
        except Exception as e:
            self._logger.error('Error in validate(). {0}.'.format(e))
            return self._create_invalid_response(message=str(e))

    def on_validation_error(self, validation, event, timestamp=None):
        # type: (ValidationResponse, Event, Optional[datetime]) -> None
        if self._plugin.__class__.on_validation_error != Plugin.on_validation_error:
            self._logger.info("on_validation_error(event={0}, validation='{1}')".format(event.name, validation.message))
        try:
            self._plugin.on_validation_error(validation, event, timestamp)
        except Exception as e:
            self._logger.error('Error in on_validation_error(). {0}.'.format(e))
