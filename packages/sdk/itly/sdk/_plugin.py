from abc import ABC, abstractmethod
from typing import Optional

from ._event import Event
from ._logger import Logger
from ._plugin_options import PluginLoadOptions
from ._properties import Properties
from ._validation_response import ValidationResponse


class Plugin(ABC):
    @abstractmethod
    def id(self) -> str:
        pass

    # Tracking methods

    def load(self, options: PluginLoadOptions) -> None:
        pass

    def alias(self, user_id: str, previous_id: str) -> None:
        pass

    def identify(self, user_id: str, properties: Optional[Properties]) -> None:
        pass

    def group(self, user_id: str, group_id: str, properties: Optional[Properties]) -> None:
        pass

    def page(self, user_id: str, category: Optional[str], name: Optional[str], properties: Optional[Properties]) -> None:
        pass

    def track(self, user_id: str, event: Event) -> None:
        pass

    def flush(self) -> None:
        pass

    def shutdown(self) -> None:
        pass

    # Validation methods

    def validate(self, event: Event) -> ValidationResponse:
        return self._create_valid_response()

    def on_validation_error(self, validation: ValidationResponse, event: Event) -> None:
        pass

    def _create_valid_response(self) -> ValidationResponse:
        return ValidationResponse(valid=True, plugin_id=self.id(), message='')

    def _create_invalid_response(self, message: str) -> ValidationResponse:
        return ValidationResponse(valid=False, plugin_id=self.id(), message=message)


class PluginSafeDecorator(Plugin):
    def __init__(self, plugin: Plugin, logger: Logger) -> None:
        self._plugin = plugin
        self._logger = logger

    def id(self) -> str:
        return self._plugin.id()

    # Tracking methods

    def load(self, options: PluginLoadOptions) -> None:
        self._logger.info('load()')
        try:
            self._plugin.load(options)
        except Exception as e:
            self._logger.error('Error in load(). {0}'.format(e))

    def alias(self, user_id: str, previous_id: str) -> None:
        if self._plugin.__class__.alias != Plugin.alias:
            self._logger.info('alias(user_id={0}, previous_id={1})'.format(user_id, previous_id))
        try:
            self._plugin.alias(user_id, previous_id)
        except Exception as e:
            self._logger.error('Error in alias(). {0}'.format(e))

    def identify(self, user_id: str, properties: Optional[Properties]) -> None:
        if self._plugin.__class__.identify != Plugin.identify:
            self._logger.info('identify(user_id={0}, properties={1})'.format(user_id, properties))
        try:
            self._plugin.identify(user_id, properties)
        except Exception as e:
            self._logger.error('Error in identify(). {0}'.format(e))

    def group(self, user_id: str, group_id: str, properties: Optional[Properties]) -> None:
        if self._plugin.__class__.group != Plugin.group:
            self._logger.info('group(user_id={0}, group_id={1}, properties={2})'.format(user_id, group_id, properties))
        try:
            self._plugin.group(user_id, group_id, properties)
        except Exception as e:
            self._logger.error('Error in group(). {0}'.format(e))

    def page(self, user_id: str, category: Optional[str], name: Optional[str], properties: Optional[Properties]) -> None:
        if self._plugin.__class__.page != Plugin.page:
            self._logger.info('page(user_id={0}, category={1}, name={2}, properties={3})'.format(user_id, category, name, properties))
        try:
            self._plugin.page(user_id, category, name, properties)
        except Exception as e:
            self._logger.error('Error in page(). {0}'.format(e))

    def track(self, user_id: str, event: Event) -> None:
        if self._plugin.__class__.track != Plugin.track:
            self._logger.info('track(user_id={0}, event={1}, properties={2})'.format(user_id, event.name, event.properties))
        try:
            self._plugin.track(user_id, event)
        except Exception as e:
            self._logger.error('Error in track(). {0}'.format(e))

    def flush(self) -> None:
        if self._plugin.__class__.flush != Plugin.flush:
            self._logger.info('flush()')
        try:
            self._plugin.flush()
        except Exception as e:
            self._logger.error('Error in flush(). {0}'.format(e))

    def shutdown(self) -> None:
        if self._plugin.__class__.shutdown != Plugin.shutdown:
            self._logger.info('shutdown()')
        try:
            self._plugin.shutdown()
        except Exception as e:
            self._logger.error('Error in shutdown(). {0}'.format(e))

    # Validation methods

    def validate(self, event: Event) -> ValidationResponse:
        if self._plugin.__class__.validate != Plugin.validate:
            self._logger.info('validate(event={0}, properties={1})'.format(event.name, event.properties))
        try:
            return self._plugin.validate(event)
        except Exception as e:
            self._logger.error('Error in validate(). {0}'.format(e))
            return self._create_invalid_response(message=str(e))

    def on_validation_error(self, validation: ValidationResponse, event: Event) -> None:
        if self._plugin.__class__.on_validation_error != Plugin.on_validation_error:
            self._logger.info("on_validation_error(event={0}, validation='{1}')".format(event.name, validation.message))
        try:
            self._plugin.on_validation_error(validation, event)
        except Exception as e:
            self._logger.error('Error in on_validation_error(). {0}'.format(e))
