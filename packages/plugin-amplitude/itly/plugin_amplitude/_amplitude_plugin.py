from datetime import timedelta
from typing import Optional, NamedTuple, Dict, Any

from itly.sdk import Plugin, PluginLoadOptions, Event, Logger
from ._amplitude_client import AmplitudeClient


class AmplitudeOptions(NamedTuple):
    flush_queue_size: int = 10
    flush_interval: timedelta = timedelta(seconds=1)
    events_endpoint: Optional[str] = None
    identification_endpoint: Optional[str] = None


class AmplitudePlugin(Plugin):
    def __init__(self, api_key: str, options: Optional[AmplitudeOptions] = None) -> None:
        self._api_key: str = api_key
        self._options: AmplitudeOptions = options if options is not None else AmplitudeOptions()
        self._client: Optional[AmplitudeClient] = None
        self._logger: Logger = Logger.NONE

    def id(self) -> str:
        return 'amplitude'

    def load(self, options: PluginLoadOptions) -> None:
        self._client = AmplitudeClient(api_key=self._api_key, on_error=self._on_error,
                                       flush_queue_size=self._options.flush_queue_size, flush_interval=self._options.flush_interval,
                                       events_endpoint=self._options.events_endpoint, identification_endpoint=self._options.identification_endpoint)
        self._logger = options.logger

    def identify(self, user_id: str, properties: Optional[Dict[str, Any]]) -> None:
        assert self._client is not None
        self._client.identify(user_id=user_id,
                              properties=properties.copy() if properties is not None else None)

    def track(self, user_id: str, event: Event) -> None:
        assert self._client is not None
        self._client.track(user_id=user_id,
                           event_name=event.name,
                           properties=event.properties.copy() if event.properties is not None else None)

    def flush(self) -> None:
        assert self._client is not None
        self._client.flush()

    def shutdown(self) -> None:
        assert self._client is not None
        self._client.shutdown()

    def _on_error(self, err: str) -> None:
        self._logger.error(f"Error. {err}")
