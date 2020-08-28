from datetime import timedelta, datetime
from typing import Optional, Callable

from itly.sdk import Plugin, PluginOptions, Properties, Event, Logger
from ._amplitude_client import AmplitudeClient, Request


class AmplitudeOptions(object):
    def __init__(self, flush_queue_size=10, flush_interval_ms=1000, events_endpoint=None, identification_endpoint=None):
        # type: (int, int, Optional[str], Optional[str]) -> None
        self.flush_queue_size = flush_queue_size  # type: int
        self.flush_interval_ms = flush_interval_ms  # type: int
        self.events_endpoint = events_endpoint  # type: Optional[str]
        self.identification_endpoint = identification_endpoint  # type: Optional[str]


class AmplitudePlugin(Plugin):
    def __init__(self, api_key, options):
        # type: (str, AmplitudeOptions) -> None
        self._api_key = api_key  # type: str
        self._options = options  # type: AmplitudeOptions
        self._client = None  # type: Optional[AmplitudeClient]
        self._logger = Logger.NONE  # type: Logger
        self._send_request = None  # type: Optional[Callable[[Request], None]]

    def id(self):
        # type: () -> str
        return 'amplitude'

    def load(self, options):
        # type: (PluginOptions) -> None
        self._client = AmplitudeClient(api_key=self._api_key, on_error=self._on_error,
                                       flush_queue_size=self._options.flush_queue_size, flush_interval=timedelta(milliseconds=self._options.flush_interval_ms),
                                       events_endpoint=self._options.events_endpoint, identification_endpoint=self._options.identification_endpoint,
                                       send_request=self._send_request)
        self._logger = options.logger

    def identify(self, user_id, properties, timestamp=None):
        # type: (str, Optional[Properties], Optional[datetime]) -> None
        assert self._client is not None
        self._client.identify(user_id=user_id,
                              properties=properties.to_json() if properties is not None else None)

    def track(self, user_id, event, timestamp=None):
        # type: (str, Event, Optional[datetime]) -> None
        assert self._client is not None
        self._client.track(user_id=user_id,
                           event_name=event.name,
                           properties=event.properties.to_json() if event.properties is not None else None,
                           timestamp=timestamp if timestamp is not None else datetime.utcnow())

    def flush(self):
        # type: () -> None
        assert self._client is not None
        self._client.flush()

    def shutdown(self):
        # type: () -> None
        assert self._client is not None
        self._client.shutdown()

    def _on_error(self, err):
        # type: (str) -> None
        message = "Error. {0}".format(err)
        self._logger.error(message)
