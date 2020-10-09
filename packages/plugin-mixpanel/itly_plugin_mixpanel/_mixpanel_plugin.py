from datetime import timedelta
from typing import Optional, NamedTuple

from mixpanel import Mixpanel, BufferedConsumer

from itly_sdk import Plugin, PluginLoadOptions, Properties, Event, Logger


class MixpanelOptions(NamedTuple):
    api_host: Optional[str] = None
    flush_queue_size: int = 10
    request_timeout: timedelta = timedelta(seconds=15)


class MixpanelPlugin(Plugin):
    def __init__(self, api_key: str, options: Optional[MixpanelOptions] = None) -> None:
        self._api_key: str = api_key
        self._options: MixpanelOptions = options if options is not None else MixpanelOptions()
        self._client: Optional[Mixpanel] = None
        self._consumer: Optional[BufferedConsumer] = None
        self._logger: Logger = Logger.NONE

    def id(self) -> str:
        return 'mixpanel'

    def load(self, options: PluginLoadOptions) -> None:
        self._consumer = BufferedConsumer(
            max_size=self._options.flush_queue_size,
            request_timeout=int(self._options.request_timeout.total_seconds()),
            events_url=None if self._options.api_host is None else f'{self._options.api_host}/track',
            people_url=None if self._options.api_host is None else f'{self._options.api_host}/engage',
        )
        self._client = Mixpanel(
            token=self._api_key,
            consumer=self._consumer,
        )
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
        assert self._consumer is not None
        self._consumer.flush()

    def shutdown(self) -> None:
        assert self._consumer is not None
        self._consumer.flush()

    def _on_error(self, err: str) -> None:
        self._logger.error(f"Error. {err}")
