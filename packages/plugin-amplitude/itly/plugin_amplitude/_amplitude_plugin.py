from datetime import timedelta, datetime
from typing import Optional, Callable, NamedTuple

from itly.sdk import Plugin, PluginLoadOptions, Properties, Event, Logger
from ._amplitude_client import AmplitudeClient, Request


class AmplitudeOptions(NamedTuple):
    flush_queue_size: int = 10
    flush_interval_ms: int = 1000
    events_endpoint: Optional[str] = None
    identification_endpoint: Optional[str] = None


class AmplitudePlugin(Plugin):
    def __init__(self, api_key: str, options: AmplitudeOptions) -> None:
        self._api_key: str = api_key
        self._options: AmplitudeOptions = options
        self._client: Optional[AmplitudeClient] = None
        self._logger: Logger = Logger.NONE
        self._send_request: Optional[Callable[[Request], None]] = None

    def id(self) -> str:
        return 'amplitude'

    def load(self, options: PluginLoadOptions) -> None:
        self._client = AmplitudeClient(api_key=self._api_key, on_error=self._on_error,
                                       flush_queue_size=self._options.flush_queue_size, flush_interval=timedelta(milliseconds=self._options.flush_interval_ms),
                                       events_endpoint=self._options.events_endpoint, identification_endpoint=self._options.identification_endpoint,
                                       send_request=self._send_request)
        self._logger = options.logger

    def identify(self, user_id: str, properties: Optional[Properties], timestamp: Optional[datetime] = None) -> None:
        assert self._client is not None
        self._client.identify(user_id=user_id,
                              properties=properties.to_json() if properties is not None else None)

    def track(self, user_id: str, event: Event, timestamp: Optional[datetime] = None) -> None:
        assert self._client is not None
        self._client.track(user_id=user_id,
                           event_name=event.name,
                           properties=event.properties.to_json() if event.properties is not None else None,
                           timestamp=timestamp if timestamp is not None else datetime.utcnow())

    def flush(self) -> None:
        assert self._client is not None
        self._client.flush()

    def shutdown(self) -> None:
        assert self._client is not None
        self._client.shutdown()

    def _on_error(self, err: str) -> None:
        message = "Error. {0}".format(err)
        self._logger.error(message)
