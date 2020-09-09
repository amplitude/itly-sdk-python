from datetime import timedelta
from typing import Optional, Callable, NamedTuple

from itly.sdk import Plugin, PluginLoadOptions, Properties, Event, Logger
from ._mixpanel_client import MixpanelClient
from ._mixpanel_consumer import Request


class MixpanelOptions(NamedTuple):
    api_host: Optional[str] = None
    flush_queue_size: int = 10
    flush_interval_ms: int = 1000


class MixpanelPlugin(Plugin):
    def __init__(self, api_key: str, options: MixpanelOptions) -> None:
        self._api_key: str = api_key
        self._options: MixpanelOptions = options
        self._client: Optional[MixpanelClient] = None
        self._logger: Logger = Logger.NONE
        self._send_request: Optional[Callable[[Request], None]] = None

    def id(self) -> str:
        return 'mixpanel'

    def load(self, options: PluginLoadOptions) -> None:
        self._client = MixpanelClient(api_key=self._api_key, on_error=self._on_error,
                                      flush_queue_size=self._options.flush_queue_size, flush_interval=timedelta(milliseconds=self._options.flush_interval_ms),
                                      api_host=self._options.api_host, send_request=self._send_request)
        self._logger = options.logger

    def alias(self, user_id: str, previous_id: str) -> None:
        assert self._client is not None
        self._client.alias(
            original=user_id,
            alias_id=previous_id)

    def identify(self, user_id: str, properties: Optional[Properties]) -> None:
        assert self._client is not None
        self._client.people_update({
            '$distinct_id': user_id,
            '$set': properties.to_json() if properties is not None else {},
        })

    def track(self, user_id: str, event: Event) -> None:
        assert self._client is not None
        self._client.track(
            distinct_id=user_id,
            event_name=event.name,
            properties=event.properties.to_json() if event.properties is not None else None)

    def flush(self) -> None:
        assert self._client is not None
        self._client.flush()

    def shutdown(self) -> None:
        assert self._client is not None
        self._client.shutdown()

    def _on_error(self, err: str) -> None:
        message = "Error. {0}".format(err)
        self._logger.error(message)
