from datetime import timedelta
from typing import Optional, NamedTuple, Callable

from itly.sdk import Plugin, PluginLoadOptions, Properties, Event, Logger
from ._segment_client import SegmentClient, Request


class SegmentOptions(NamedTuple):
    flush_queue_size: int = 10
    flush_interval_ms: int = 1000
    host: Optional[str] = None


class SegmentPlugin(Plugin):
    def __init__(self, write_key: str, options: SegmentOptions) -> None:
        self._write_key: str = write_key
        self._options: SegmentOptions = options
        self._client: Optional[SegmentClient] = None
        self._logger: Logger = Logger.NONE
        self._send_request: Optional[Callable[[Request], None]] = None

    def id(self) -> str:
        return 'segment'

    def load(self, options: PluginLoadOptions) -> None:
        self._client = SegmentClient(write_key=self._write_key, on_error=self._on_error,
                                     flush_queue_size=self._options.flush_queue_size, flush_interval=timedelta(milliseconds=self._options.flush_interval_ms),
                                     host=self._options.host, send_request=self._send_request)
        self._logger = options.logger

    def alias(self, user_id: str, previous_id: str) -> None:
        assert self._client is not None
        self._client.alias(user_id=user_id,
                           previous_id=previous_id)

    def identify(self, user_id: str, properties: Optional[Properties]) -> None:
        assert self._client is not None
        self._client.identify(user_id=user_id,
                              traits=properties.to_json() if properties is not None else None)

    def group(self, user_id: str, group_id: str, properties: Optional[Properties]) -> None:
        assert self._client is not None
        self._client.group(user_id=user_id,
                           group_id=group_id,
                           traits=properties.to_json() if properties is not None else None)

    def page(self, user_id: str, category: Optional[str], name: Optional[str], properties: Optional[Properties]) -> None:
        assert self._client is not None
        self._client.page(user_id=user_id,
                          category=category,
                          name=name,
                          properties=properties.to_json() if properties is not None else None)

    def track(self, user_id: str, event: Event) -> None:
        assert self._client is not None
        self._client.track(user_id=user_id,
                           event=event.name,
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
