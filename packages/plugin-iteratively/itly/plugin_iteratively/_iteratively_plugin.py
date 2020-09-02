from datetime import timedelta, datetime
from typing import Optional, Callable

from itly.sdk import Plugin, PluginLoadOptions, Properties, Event, Environment, ValidationResponse
from ._iteratively_client import IterativelyClient, TrackType, Request


class IterativelyOptions(object):
    def __init__(self, url=None, environment=Environment.DEVELOPMENT, omit_values=False, flush_queue_size=10, flush_interval_ms=1000, disabled=None):
        # type: (Optional[str], Environment, bool, int, int, Optional[bool]) -> None
        self.url = url  # type: Optional[str]
        self.environment = environment  # type: Environment
        self.omit_values = omit_values  # type: bool
        self.flush_queue_size = flush_queue_size  # type: int
        self.flush_interval_ms = flush_interval_ms  # type: int
        self.disabled = disabled if disabled is not None else environment == Environment.PRODUCTION  # type: bool


class IterativelyPlugin(Plugin):
    def __init__(self, api_key, options):
        # type: (str, IterativelyOptions) -> None
        self._api_key = api_key
        self._options = options
        self._client = None  # type: Optional[IterativelyClient]
        self._send_request = None  # type: Optional[Callable[[Request], None]]

    def id(self):
        # type: () -> str
        return 'iteratively'

    def load(self, options):
        # type: (PluginLoadOptions) -> None
        if self._options.disabled:
            options.logger.info("disabled")
            return

        assert self._options.url is not None
        self._client = IterativelyClient(api_endpoint=self._options.url, api_key=self._api_key,
                                         flush_queue_size=self._options.flush_queue_size, flush_interval=timedelta(milliseconds=self._options.flush_interval_ms),
                                         omit_values=self._options.omit_values, on_error=self._on_error, send_request=self._send_request)

    def identify(self, user_id, properties, timestamp=None):
        # type: (str, Optional[Properties], Optional[datetime]) -> None
        if self._options.disabled:
            return

        assert self._client is not None
        self._client.track(track_type=TrackType.IDENTIFY,
                           properties=properties,
                           timestamp=timestamp)

    def group(self, user_id, group_id, properties, timestamp=None):
        # type: (str, str, Optional[Properties], Optional[datetime]) -> None
        if self._options.disabled:
            return

        assert self._client is not None
        self._client.track(track_type=TrackType.GROUP,
                           properties=properties,
                           timestamp=timestamp)

    def page(self, user_id, category, name, properties, timestamp=None):
        # type: (str, Optional[str], Optional[str], Optional[Properties], Optional[datetime]) -> None
        if self._options.disabled:
            return

        assert self._client is not None
        self._client.track(track_type=TrackType.PAGE,
                           properties=properties,
                           timestamp=timestamp)

    def track(self, user_id, event, timestamp=None):
        # type: (str, Event, Optional[datetime]) -> None
        if self._options.disabled:
            return

        assert self._client is not None
        self._client.track(track_type=TrackType.TRACK,
                           event=event,
                           properties=event.properties,
                           timestamp=timestamp)

    def flush(self):
        # type: () -> None
        if self._options.disabled:
            return

        assert self._client is not None
        self._client.flush()

    def shutdown(self):
        # type: () -> None
        if self._options.disabled:
            return

        assert self._client is not None
        self._client.shutdown()

    def on_validation_error(self, validation, event, timestamp=None):
        # type: (ValidationResponse, Event, Optional[datetime]) -> None
        if self._options.disabled:
            return

        assert self._client is not None
        if event.name in (TrackType.GROUP.value, TrackType.IDENTIFY.value, TrackType.PAGE.value):
            self._client.track(TrackType[event.name],
                               properties=event.properties,
                               validation=validation,
                               timestamp=timestamp)
        else:
            self._client.track(TrackType.TRACK,
                               event=event,
                               properties=event.properties,
                               validation=validation,
                               timestamp=timestamp)

    def _on_error(self, err):
        # type: (str) -> None
        message = "Error. {0}".format(err)
        self._logger.error(message)
