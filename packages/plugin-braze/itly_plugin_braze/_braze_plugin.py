from datetime import timedelta
from typing import NamedTuple, Optional

from itly_sdk import Plugin, Properties, Event, PluginLoadOptions, Logger
from ._braze_client import BrazeClient

# https://www.braze.com/docs/api/basics/#api-limits
MAX_QUEUE_SIZE = 75


class BrazeOptions(NamedTuple):
    base_url: str
    flush_queue_size: int = 25
    flush_interval: timedelta = timedelta(seconds=1)
    request_timeout: timedelta = timedelta(seconds=15)


class BrazePlugin(Plugin):
    def __init__(self, api_key: str, options: BrazeOptions) -> None:
        self._api_key: str = api_key
        self._client: Optional[BrazeClient] = None
        self._logger: Logger = Logger.NONE

        self._options: BrazeOptions = options
        if self._options.flush_queue_size > MAX_QUEUE_SIZE:
            self._options = self._options._replace(flush_queue_size=MAX_QUEUE_SIZE)

    def id(self) -> str:
        return 'braze'

    def load(self, options: PluginLoadOptions) -> None:
        self._client = BrazeClient(
            base_url=self._options.base_url,
            api_key=self._api_key,
            flush_queue_size=self._options.flush_queue_size,
            flush_interval=self._options.flush_interval,
            request_timeout=self._options.request_timeout,
            logger=options.logger,
        )
        self._logger = options.logger

    def identify(self, user_id: str, properties: Optional[Properties]) -> None:
        assert self._client is not None
        identify_properties = properties.to_json() if properties is not None else None
        self._logger.info(f"identify: user_id={user_id} properties={identify_properties}")
        self._client.identify(
            user_id=user_id,
            properties=identify_properties,
        )

    def track(self, user_id: str, event: Event) -> None:
        assert self._client is not None
        event_name = event.name
        event_properties = event.properties.to_json() if event.properties is not None else None
        self._logger.info(f"track: user_id={user_id} event={event_name} properties={event_properties}")
        self._client.track(
            user_id=user_id,
            event_name=event_name,
            properties=event_properties,
        )

    def flush(self) -> None:
        assert self._client is not None
        self._client.flush()

    def shutdown(self) -> None:
        assert self._client is not None
        self._client.shutdown()

