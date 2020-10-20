from abc import ABC, abstractmethod
from typing import Optional, List

from ._event import Event
from ._logger import Logger
from ._plugin_options import PluginLoadOptions
from ._properties import Properties
from ._validation_response import ValidationResponse


class Plugin(ABC):
    # Plugin methods

    @abstractmethod
    def id(self) -> str:
        pass

    def load(self, options: PluginLoadOptions) -> None:
        pass

    # Validation methods

    def validate(self, event: Event) -> Optional[ValidationResponse]:
        return None

    # Tracking methods

    def alias(self, user_id: str, previous_id: str) -> None:
        pass

    def post_alias(self, user_id: str, previous_id: str) -> None:
        pass

    def identify(self, user_id: str, properties: Optional[Properties]) -> None:
        pass

    def post_identify(self,
                      user_id: str,
                      properties: Optional[Properties],
                      validation_results: List[ValidationResponse]) -> None:
        pass

    def group(self, user_id: str, group_id: str, properties: Optional[Properties]) -> None:
        pass

    def post_group(self,
                   user_id: str,
                   group_id: str,
                   properties: Optional[Properties],
                   validation_results: List[ValidationResponse]) -> None:
        pass

    def page(self,
             user_id: str,
             category: Optional[str],
             name: Optional[str],
             properties: Optional[Properties]) -> None:
        pass

    def post_page(self,
                  user_id: str,
                  category: Optional[str],
                  name: Optional[str],
                  properties: Optional[Properties],
                  validation_results: List[ValidationResponse]) -> None:
        pass

    def track(self, user_id: str, event: Event) -> None:
        pass

    def post_track(self, user_id: str, event: Event, validation_results: List[ValidationResponse]) -> None:
        pass

    def flush(self) -> None:
        pass

    def shutdown(self) -> None:
        pass

    # Helper methods

    def _create_valid_response(self) -> ValidationResponse:
        return ValidationResponse(valid=True, plugin_id=self.id(), message='')

    def _create_invalid_response(self, message: str) -> ValidationResponse:
        return ValidationResponse(valid=False, plugin_id=self.id(), message=message)


class PluginSafeDecorator(Plugin):
    def __init__(self, plugin: Plugin, logger: Logger) -> None:
        self._plugin = plugin
        self._logger = logger

    # Plugin methods

    def id(self) -> str:
        return self._plugin.id()

    def load(self, options: PluginLoadOptions) -> None:
        self._logger.info('load()')
        try:
            self._plugin.load(options)
        except Exception as e:
            self._logger.error(f'Error in load(). {e}')

    # Validation methods

    def validate(self, event: Event) -> Optional[ValidationResponse]:
        if self._plugin.__class__.validate != Plugin.validate:
            self._logger.info(f'validate(event={event.name}, properties={event.properties})')
        try:
            return self._plugin.validate(event)
        except Exception as e:
            self._logger.error(f'Error in validate(). {e}')
            return self._create_invalid_response(message=str(e))

    # Tracking methods

    def alias(self, user_id: str, previous_id: str) -> None:
        if self._plugin.__class__.alias != Plugin.alias:
            self._logger.info(f'alias(user_id={user_id}, previous_id={previous_id})')
        try:
            self._plugin.alias(user_id, previous_id)
        except Exception as e:
            self._logger.error(f'Error in alias(). {e}')

    def post_alias(self, user_id: str, previous_id: str) -> None:
        if self._plugin.__class__.post_alias != Plugin.post_alias:
            self._logger.info(f'post_alias(user_id={user_id}, previous_id={previous_id})')
        try:
            self._plugin.post_alias(user_id, previous_id)
        except Exception as e:
            self._logger.error(f'Error in post_alias(). {e}')

    def identify(self, user_id: str, properties: Optional[Properties]) -> None:
        if self._plugin.__class__.identify != Plugin.identify:
            self._logger.info(f'identify(user_id={user_id}, properties={properties})')
        try:
            self._plugin.identify(user_id, properties)
        except Exception as e:
            self._logger.error(f'Error in identify(). {e}')

    def post_identify(self,
                      user_id: str,
                      properties: Optional[Properties],
                      validation_results: List[ValidationResponse]) -> None:
        if self._plugin.__class__.post_identify != Plugin.post_identify:
            self._logger.info(
                f'post_identify(user_id={user_id}, properties={properties}, validation_results={validation_results})')
        try:
            self._plugin.post_identify(user_id, properties, validation_results)
        except Exception as e:
            self._logger.error(f'Error in post_identify(). {e}')

    def group(self, user_id: str, group_id: str, properties: Optional[Properties]) -> None:
        if self._plugin.__class__.group != Plugin.group:
            self._logger.info(f'group(user_id={user_id}, group_id={group_id}, properties={properties})')
        try:
            self._plugin.group(user_id, group_id, properties)
        except Exception as e:
            self._logger.error(f'Error in group(). {e}')

    def post_group(self,
                   user_id: str,
                   group_id: str,
                   properties: Optional[Properties],
                   validation_results: List[ValidationResponse]) -> None:
        if self._plugin.__class__.post_group != Plugin.post_group:
            self._logger.info(
                f'post_group(user_id={user_id}, group_id={group_id}, properties={properties}, '
                f'validation_results={validation_results})'
            )
        try:
            self._plugin.post_group(user_id, group_id, properties, validation_results)
        except Exception as e:
            self._logger.error(f'Error in post_group(). {e}')

    def page(self,
             user_id: str,
             category: Optional[str],
             name: Optional[str],
             properties: Optional[Properties]) -> None:
        if self._plugin.__class__.page != Plugin.page:
            self._logger.info(f'page(user_id={user_id}, category={category}, name={name}, properties={properties})')
        try:
            self._plugin.page(user_id, category, name, properties)
        except Exception as e:
            self._logger.error(f'Error in page(). {e}')

    def post_page(self,
                  user_id: str,
                  category: Optional[str],
                  name: Optional[str],
                  properties: Optional[Properties],
                  validation_results: List[ValidationResponse]) -> None:
        if self._plugin.__class__.post_page != Plugin.post_page:
            self._logger.info(f'post_page(user_id={user_id}, category={category}, name={name}, properties={properties}, '
                              f'validation_results={validation_results})')
        try:
            self._plugin.post_page(user_id, category, name, properties, validation_results)
        except Exception as e:
            self._logger.error(f'Error in post_page(). {e}')

    def track(self, user_id: str, event: Event) -> None:
        if self._plugin.__class__.track != Plugin.track:
            self._logger.info(f'track(user_id={user_id}, event={event.name}, properties={event.properties})')
        try:
            self._plugin.track(user_id, event)
        except Exception as e:
            self._logger.error(f'Error in track(). {e}')

    def post_track(self, user_id: str, event: Event, validation_results: List[ValidationResponse]) -> None:
        if self._plugin.__class__.post_track != Plugin.post_track:
            self._logger.info(f'post_track(user_id={user_id}, event={event.name}, properties={event.properties}, '
                              f'validation_results={validation_results})')
        try:
            self._plugin.post_track(user_id, event, validation_results)
        except Exception as e:
            self._logger.error(f'Error in post_track(). {e}')

    def flush(self) -> None:
        if self._plugin.__class__.flush != Plugin.flush:
            self._logger.info('flush()')
        try:
            self._plugin.flush()
        except Exception as e:
            self._logger.error(f'Error in flush(). {e}')

    def shutdown(self) -> None:
        if self._plugin.__class__.shutdown != Plugin.shutdown:
            self._logger.info('shutdown()')
        try:
            self._plugin.shutdown()
        except Exception as e:
            self._logger.error(f'Error in shutdown(). {e}')
