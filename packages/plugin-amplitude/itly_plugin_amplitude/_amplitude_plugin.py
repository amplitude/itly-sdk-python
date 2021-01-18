from datetime import timedelta
from typing import Optional, NamedTuple, cast

from itly_sdk import Plugin, PluginLoadOptions, Properties, Event, Logger
from ._amplitude_client import AmplitudeClient
from itly_plugin_amplitude._amplitude_metadata import AmplitudeMetadata


class AmplitudeOptions(NamedTuple):
    flush_queue_size: int = 10
    flush_interval: timedelta = timedelta(seconds=1)
    events_endpoint: Optional[str] = None
    identification_endpoint: Optional[str] = None
    request_timeout: timedelta = timedelta(seconds=15)
    min_id_length: Optional[int] = None
    metadata: Optional[AmplitudeMetadata] = None


class AmplitudePlugin(Plugin):
    def __init__(self, api_key: str, options: Optional[AmplitudeOptions] = None) -> None:
        self._api_key: str = api_key
        self._options: AmplitudeOptions = options if options is not None else AmplitudeOptions()
        self._client: Optional[AmplitudeClient] = None
        self._logger: Logger = Logger.NONE

    def id(self) -> str:
        return 'amplitude'

    def load(self, options: PluginLoadOptions) -> None:
        self._client = AmplitudeClient(api_key=self._api_key,
                                       on_error=self._on_error,
                                       flush_queue_size=self._options.flush_queue_size,
                                       flush_interval=self._options.flush_interval,
                                       request_timeout=self._options.request_timeout,
                                       min_id_length=self._options.min_id_length,
                                       events_endpoint=self._options.events_endpoint,
                                       identification_endpoint=self._options.identification_endpoint)
        self._logger = options.logger

    def identify(self, user_id: str, properties: Optional[Properties]) -> None:
        assert self._client is not None
        self._client.identify(user_id=user_id,
                              properties=properties.to_json() if properties is not None else None,
                              metadata=self._options.metadata)

    def track(self, user_id: str, event: Event) -> None:
        assert self._client is not None
        event_metadata = cast(Optional[AmplitudeMetadata], event.metadata.get(self.id()))
        metadata = AmplitudeMetadata.merge(self._options.metadata, event_metadata)
        self._client.track(user_id=user_id,
                           event_name=event.name,
                           properties=event.properties.to_json() if event.properties is not None else None,
                           metadata=metadata)

    def flush(self) -> None:
        assert self._client is not None
        self._client.flush()

    def shutdown(self) -> None:
        assert self._client is not None
        self._client.shutdown()

    def _on_error(self, err: str) -> None:
        self._logger.error(f"Error. {err}")
