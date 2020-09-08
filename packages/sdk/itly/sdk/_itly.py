import copy
from typing import Optional, List

from ._environment import Environment
from ._event import Event
from ._logger import Logger, LoggerPrefixSafeDecorator
from ._options import Options
from ._plugin import Plugin, PluginSafeDecorator
from ._plugin_options import PluginLoadOptions
from ._properties import Properties
from ._validation_options import ValidationOptions
from ._validation_response import ValidationResponse

DEFAULT_DEV_VALIDATION_OPTIONS = ValidationOptions(disabled=False, track_invalid=False, error_on_invalid=True)
DEFAULT_PROD_VALIDATION_OPTIONS = ValidationOptions(disabled=False, track_invalid=False, error_on_invalid=False)
LOG_PREFIX = '[itly-core] '


class Itly:
    def __init__(self) -> None:
        self._options: Optional[Options] = None
        self._plugins: List[Plugin] = []
        self._validationOptions: Optional[ValidationOptions] = None
        self._logger: Logger = Logger.NONE
        self._is_shutdown: bool = False

    def load(self, options: Options) -> None:
        if self._options is not None:
            raise Exception('Itly is already initialized. itly.load() should only be called once.')

        self._options = options
        if self._options.validation is None:
            self._options = self._options._replace(
                validation=DEFAULT_PROD_VALIDATION_OPTIONS if self._options.environment == Environment.PRODUCTION else DEFAULT_DEV_VALIDATION_OPTIONS
            )

        self._logger = LoggerPrefixSafeDecorator(self._options.logger, LOG_PREFIX)

        if self._options.disabled:
            self._logger.info('disabled = True')
            return

        self._validationOptions = self._options.validation

        self._logger.info('load()')

        for plugin in self._options.plugins:
            plugin_logger = LoggerPrefixSafeDecorator(self._options.logger, '[plugin-{0}] '.format(plugin.id()))
            plugin = PluginSafeDecorator(plugin, plugin_logger)
            self._plugins.append(plugin)
            plugin_options = PluginLoadOptions(environment=self._options.environment, logger=plugin_logger)
            plugin.load(plugin_options)

        context_event = Event(
            name='context',
            properties=options.context,
        )
        self._validate(context_event)

    def alias(self, user_id: str, previous_id: str) -> None:
        if self._disabled():
            return

        self._logger.info('alias(user_id={0}, previous_id={1})'.format(user_id, previous_id))
        for plugin in self._plugins:
            plugin.alias(user_id=user_id, previous_id=previous_id)

    def identify(self, user_id: str, identify_properties: Optional[Properties] = None) -> None:
        if self._disabled():
            return

        self._logger.info('identify(user_id={0}, properties={1})'.format(user_id, identify_properties))

        identify_event = Event(
            name='identify',
            properties=identify_properties,
        )
        if self._should_be_tracked(identify_event):
            for plugin in self._plugins:
                plugin.identify(user_id=user_id, properties=identify_properties)

    def group(self, user_id: str, group_id: str, group_properties: Optional[Properties] = None) -> None:
        if self._disabled():
            return

        self._logger.info('group(user_id={0}, group_id={1}, properties={2})'.format(user_id, group_id, group_properties))

        group_event = Event(
            name='group',
            properties=group_properties,
        )
        if self._should_be_tracked(group_event):
            for plugin in self._plugins:
                plugin.group(user_id=user_id, group_id=group_id, properties=group_properties)

    def page(self, user_id: str, category: Optional[str], name: Optional[str], page_properties: Optional[Properties] = None) -> None:
        if self._disabled():
            return

        self._logger.info('page(user_id={0}, category={1}, name={2}, properties={3})'.format(user_id, category, name, page_properties))

        page_event = Event(
            name='page',
            properties=page_properties,
        )
        if self._should_be_tracked(page_event):
            for plugin in self._plugins:
                plugin.page(user_id=user_id, category=category, name=name, properties=page_properties)

    def track(self, user_id: str, event: Event) -> None:
        if self._disabled():
            return

        merged_event: Event = event
        if self._options.context is not None:
            merged_event = copy.copy(event)
            merged_event.properties = Properties.concat([self._options.context, event.properties])

        self._logger.info('track(user_id={0}, event={1}, properties={2})'.format(user_id, merged_event.name, merged_event.properties))

        if not self._should_be_tracked(event):
            return

        assert self._options is not None

        for plugin in self._plugins:
            plugin.track(user_id=user_id, event=merged_event)

    def flush(self) -> None:
        if self._disabled():
            return

        self._logger.info('flush()')
        for plugin in self._plugins:
            plugin.flush()

    def shutdown(self) -> None:
        if self._disabled():
            return

        self._logger.info('shutdown()')

        self._is_shutdown = True
        for plugin in self._plugins:
            plugin.shutdown()

    def _validate(self, event: Event) -> bool:
        failed_validations: List[ValidationResponse] = []

        for plugin in self._plugins:
            validation = plugin.validate(event)
            if not validation.valid:
                failed_validations.append(validation)

        if len(failed_validations) == 0:
            return True

        # If validation failed call validationError hook
        for plugin in self._plugins:
            for validation in failed_validations:
                plugin.on_validation_error(validation, event)

        assert self._validationOptions is not None
        if self._validationOptions.error_on_invalid:
            raise ValueError('Validation Error: {0}'.format(failed_validations[0].message))

        return False

    def _disabled(self) -> bool:
        if self._is_shutdown:
            raise Exception('Itly is shutdown. No more requests are possible.')
        if self._options is None:
            raise Exception('Itly is not yet initialized. Have you called `itly.load()` on app start?')

        return self._options.disabled

    def _should_be_tracked(self, event: Event) -> bool:
        assert self._validationOptions is not None

        if self._validationOptions.disabled:
            return True
        should_track = self._validate(event)
        if self._validationOptions.track_invalid:
            should_track = True
        return should_track
