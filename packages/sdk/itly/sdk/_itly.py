import copy
from threading import Lock
from typing import Optional, List

from ._environment import Environment
from ._event import Event
from ._logger import Logger, LoggerPrefixSafeDecorator
from ._options import Options
from ._plugin import Plugin, PluginSafeDecorator
from ._plugin_options import PluginOptions
from ._properties import Properties
from ._validation_options import ValidationOptions
from ._validation_response import ValidationResponse

DEFAULT_DEV_VALIDATION_OPTIONS = ValidationOptions(disabled=False, track_invalid=False, error_on_invalid=True)
DEFAULT_PROD_VALIDATION_OPTIONS = ValidationOptions(disabled=False, track_invalid=False, error_on_invalid=False)
LOG_PREFIX = '[itly-core] '


class Itly(object):
    def __init__(self):
        # type: () -> None
        self._options = None  # type: Optional[Options]
        self._plugins = []  # type: List[Plugin]
        self._validationOptions = None  # type: Optional[ValidationOptions]
        self._logger = Logger.NONE  # type: Logger
        self._is_shutdown = False  # type: bool
        self._lock = Lock()

    def load(self, options):
        # type: (Options) -> None
        if self._options is not None:
            raise Exception('Itly is already initialized.')

        self._options = copy.copy(options)
        if self._options.validation is None:
            self._options.validation = copy.copy(DEFAULT_PROD_VALIDATION_OPTIONS
                                                 if self._options.environment == Environment.PRODUCTION
                                                 else DEFAULT_DEV_VALIDATION_OPTIONS)

        if not self._is_initialized_and_enabled():
            return

        self._logger = LoggerPrefixSafeDecorator(self._options.logger, LOG_PREFIX)
        self._plugins = [PluginSafeDecorator(plugin, self._logger) for plugin in self._options.plugins]
        self._validationOptions = self._options.validation

        for plugin in self._plugins:
            plugin_logger = LoggerPrefixSafeDecorator(self._options.logger, '[itly-plugin-{0}] '.format(plugin.id()))
            plugin_options = PluginOptions(environment=self._options.environment, logger=plugin_logger)
            plugin.load(plugin_options)

        context_event = Event(
            name='context',
            properties=options.context if options.context else Properties(),
            event_id='context',
            version='0-0-0',
        )
        self._validate(context_event)

    def alias(self, user_id, previous_id):
        # type: (str, Optional[str]) -> None
        if not self._is_initialized_and_enabled():
            return

        for plugin in self._plugins:
            plugin.alias(user_id=user_id, previous_id=previous_id)

    def identify(self, user_id, identify_properties=None):
        # type: (str, Optional[Properties]) -> None
        if not self._is_initialized_and_enabled():
            return

        identify_event = Event(
            name='identify',
            properties=identify_properties if identify_properties else Properties(),
            event_id='identify',
            version='0-0-0',
        )

        if self._should_be_tracked(identify_event):
            for plugin in self._plugins:
                plugin.identify(user_id=user_id, properties=identify_properties)

    def group(self, user_id, group_id, group_properties=None):
        # type: (str, str, Optional[Properties]) -> None
        if not self._is_initialized_and_enabled():
            return

        group_event = Event(
            name='group',
            properties=group_properties if group_properties else Properties(),
            event_id='group',
            version='0-0-0',
        )

        if self._should_be_tracked(group_event):
            for plugin in self._plugins:
                plugin.group(user_id=user_id, group_id=group_id, properties=group_properties)

    def page(self, user_id, category, name, page_properties=None):
        # type: (str, str, str, Optional[Properties]) -> None
        if not self._is_initialized_and_enabled():
            return

        page_event = Event(
            name='page',
            properties=page_properties if page_properties else Properties(),
            event_id='page',
            version='0-0-0',
        )

        if self._should_be_tracked(page_event):
            for plugin in self._plugins:
                plugin.page(user_id=user_id, category=category, name=name, properties=page_properties)

    def track(self, user_id, event):
        # type: (str, Event) -> None
        if not self._is_initialized_and_enabled():
            return
        if not self._should_be_tracked(event):
            return

        assert self._options is not None

        merged_event = event  # type: Event
        if self._options.context is not None:
            merged_event = copy.copy(event)
            merged_event.properties = Properties.concat([self._options.context, event.properties])

        for plugin in self._plugins:
            plugin.track(user_id=user_id, event=merged_event)

    def flush(self):
        # type: () -> None
        if not self._is_initialized_and_enabled():
            return

        for plugin in self._plugins:
            plugin.flush()

    def shutdown(self):
        # type: () -> None
        if not self._is_initialized_and_enabled():
            return

        with self._lock:
            self._is_shutdown = True

        for plugin in self._plugins:
            plugin.shutdown()

    def get_plugin(self, plugin_id):
        # type: (str) -> Optional[Plugin]
        for plugin in self._plugins:
            if plugin.id() == plugin_id:
                return plugin
        return None

    def _validate(self, event):
        # type: (Event) -> bool
        failed_validations = []  # type: List[ValidationResponse]

        # Loop over plugins and stop if valid === false
        for plugin in self._plugins:
            validation = plugin.validate(event)
            if not validation.valid:
                failed_validations.append(validation)

        if len(failed_validations) == 0:
            return True

        # If validation failed call validationError hook
        for plugin in self._plugins:
            for validation in failed_validations:
                plugin.validation_error(validation, event)

        assert self._validationOptions is not None
        if self._validationOptions.error_on_invalid:
            raise Exception('Validation Error: {0}'.format(failed_validations[0].message))

        return False

    def _is_initialized_and_enabled(self):
        # type: () -> bool
        with self._lock:
            if self._is_shutdown:
                raise Exception('Itly is shutdown. No more requests are possible.')
        if self._options is None:
            raise Exception('Itly is not yet initialized. Have you called `itly.load()` on app start?')

        return not self._options.disabled

    def _should_be_tracked(self, event):
        # type: (Event) -> bool
        assert self._validationOptions is not None

        if self._validationOptions.disabled:
            return True
        should_track = self._validate(event)
        if self._validationOptions.track_invalid:
            should_track = True
        return should_track
