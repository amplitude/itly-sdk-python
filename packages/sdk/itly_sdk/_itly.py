from typing import Optional, List, Callable

from ._event import Event
from ._logger import Logger, LoggerPrefixSafeDecorator
from ._options import Options
from ._plugin import Plugin, PluginSafeDecorator
from ._plugin_options import PluginLoadOptions
from ._properties import Properties
from ._validation_response import ValidationResponse

LOG_PREFIX = '[itly-core] '


class Itly:
    def __init__(self) -> None:
        self._options: Optional[Options] = None
        self._plugins: List[Plugin] = []
        self._logger: Logger = Logger.NONE
        self._is_shutdown: bool = False
        self._context: Optional[Event] = None

    def load(self, context: Optional[Properties] = None, options: Optional[Options] = Options()) -> None:
        if self._options is not None:
            raise Exception('Itly is already initialized. itly.load() should only be called once.')

        self._options = options
        self._logger = LoggerPrefixSafeDecorator(self._options.logger, LOG_PREFIX)

        if self._options.disabled:
            self._logger.info('disabled = True')
            return

        self._logger.info('load()')

        if context is not None:
            self._context = Event(
                name='context',
                properties=context,
            )

        for plugin in self._options.plugins:
            plugin_logger = LoggerPrefixSafeDecorator(self._options.logger, f'[plugin-{plugin.id()}] ')
            plugin = PluginSafeDecorator(plugin, plugin_logger)
            self._plugins.append(plugin)
            plugin_options = PluginLoadOptions(environment=self._options.environment, logger=plugin_logger)
            plugin.load(plugin_options)

    def alias(self, user_id: str, previous_id: str) -> None:
        if self._disabled():
            return

        self._logger.info(f'alias(user_id={user_id}, previous_id={previous_id})')
        self._run_on_all_plugins(lambda plugin: plugin.alias(user_id=user_id, previous_id=previous_id))
        self._run_on_all_plugins(lambda plugin: plugin.post_alias(user_id=user_id, previous_id=previous_id))

    def identify(self, user_id: str, identify_properties: Optional[Properties] = None) -> None:
        if self._disabled():
            return

        identify_event = Event('identify', identify_properties)
        self._logger.info(f'identify(user_id={user_id}, properties={identify_event.properties})')
        self._validate_and_run_on_all_plugins(
            identify_event,
            False,
            lambda plugin, event: plugin.identify(user_id, event.properties),
            lambda plugin, event, validation_results: plugin.post_identify(user_id,
                                                                           event.properties,
                                                                           validation_results),
        )

    def group(self, user_id: str, group_id: str, group_properties: Optional[Properties] = None) -> None:
        if self._disabled():
            return

        group_event = Event('group', group_properties)
        self._logger.info(f'group(user_id={user_id}, group_id={group_id}, properties={group_event.properties})')
        self._validate_and_run_on_all_plugins(
            group_event,
            False,
            lambda plugin, event: plugin.group(user_id, group_id, event.properties),
            lambda plugin, event, validation_results: plugin.post_group(user_id,
                                                                        group_id,
                                                                        event.properties,
                                                                        validation_results),
        )

    def page(self,
             user_id: str,
             category: Optional[str],
             name: Optional[str],
             page_properties: Optional[Properties] = None) -> None:
        if self._disabled():
            return

        page_event = Event('page', page_properties)
        self._logger.info(
            f'page(user_id={user_id}, category={category}, name={name}, properties={page_event.properties})'
        )
        self._validate_and_run_on_all_plugins(
            page_event,
            False,
            lambda plugin, event: plugin.page(user_id, category, name, event.properties),
            lambda plugin, event, validation_results: plugin.post_page(user_id,
                                                                       category,
                                                                       name,
                                                                       event.properties,
                                                                       validation_results),
        )

    def track(self, user_id: str, event: Event) -> None:
        if self._disabled():
            return

        self._logger.info(f'track(user_id={user_id}, event={event.name}, properties={event.properties})')
        self._validate_and_run_on_all_plugins(
            event,
            True,
            lambda plugin, ev: plugin.track(user_id, ev),
            lambda plugin, ev, validation_results: plugin.post_track(user_id, ev, validation_results),
        )

    def flush(self) -> None:
        if self._disabled():
            return

        self._logger.info('flush()')
        self._run_on_all_plugins(lambda plugin: plugin.flush())

    def shutdown(self) -> None:
        if self._disabled():
            return

        self._logger.info('shutdown()')
        self._is_shutdown = True
        self._run_on_all_plugins(lambda plugin: plugin.shutdown())

    def _validate(self, event: Event) -> List[ValidationResponse]:
        validation_results: List[ValidationResponse] = []

        assert self._options is not None
        if not self._options.validation.disabled:
            for plugin in self._plugins:
                validation_result = plugin.validate(event)
                # Only add invalid validation responses
                if validation_result is not None and not validation_result.valid:
                    validation_results.append(validation_result)

        return validation_results

    def _validate_and_run_on_all_plugins(self,
                                         event: Event,
                                         include_context: bool,
                                         action: Callable[[Plugin, Event], None],
                                         post_action: Callable[[Plugin, Event, List[ValidationResponse]], None]
                                         ) -> None:
        context_failed_validation_responses = self._validate(
            self._context
        ) if include_context and self._context is not None else []
        is_context_valid = len(context_failed_validation_responses) == 0

        event_failed_validation_responses = self._validate(event)
        is_event_valid = len(event_failed_validation_responses) == 0

        combined_event: Event = event
        if include_context and self._context is not None:
            combined_event = Event(
                name=event.name,
                properties=Properties.concat([self._context.properties, event.properties]),
                id_=event.id,
                version=event.version,
            )

        assert self._options is not None
        if (is_context_valid and is_event_valid) or self._options.validation.track_invalid:
            self._run_on_all_plugins(lambda plugin: action(plugin, combined_event))

        combined_failed_validation_responses = context_failed_validation_responses + event_failed_validation_responses
        self._run_on_all_plugins(lambda plugin: post_action(plugin,
                                                            combined_event,
                                                            combined_failed_validation_responses))

        if (not is_context_valid or not is_event_valid) and self._options.validation.error_on_invalid:
            raise ValueError(combined_failed_validation_responses[0].message)

    def _run_on_all_plugins(self, action: Callable[[Plugin], None]) -> None:
        for plugin in self._plugins:
            action(plugin)

    def _disabled(self) -> bool:
        if self._is_shutdown:
            raise Exception('Itly is shutdown. No more requests are possible.')
        if self._options is None:
            raise Exception('Itly is not yet initialized. Have you called `itly.load()` on app start?')

        return self._options.disabled
