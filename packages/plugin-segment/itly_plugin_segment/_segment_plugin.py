from typing import Optional, NamedTuple, Any

import analytics

from itly_sdk import Plugin, PluginLoadOptions, Properties, Event, Logger


# Segment Options
# https://segment.com/docs/connections/sources/catalog/libraries/server/python/#options
# https://github.com/segmentio/analytics-python/blob/master/analytics/client.py#L28-L31
class SegmentOptions(NamedTuple):
    host: Optional[str] = None
    debug: Optional[bool] = False
    max_queue_size: Optional[int] = 10000
    send: Optional[bool] = True
    # on_error: Optional[Callable[error, items], None] = None
    # The following Options will be avaible in analytics-python:1.3.0 (currently beta)
    # flush_at: Optional[int] = 100
    # flush_interval: Optional[float] = 0.5
    # gzip: Optional[bool] = False
    # max_retries: Optional[int] = 3
    # sync_mode: Optional[bool] = False
    # timeout: Optional[int] = 15
    # thread: Optional[int] = 1


class SegmentPlugin(Plugin):
    def __init__(self, write_key: str, options: Optional[SegmentOptions] = None) -> None:
        self._write_key: str = write_key
        self._options: SegmentOptions = options if options is not None else SegmentOptions()
        self._client: Optional[analytics.Client] = None
        self._logger: Logger = Logger.NONE

    def id(self) -> str:
        return 'segment'

    def load(self, options: PluginLoadOptions) -> None:
        self._client = analytics.Client(
            write_key=self._write_key,
            on_error=self._on_error,
            **self._options._asdict()
        )
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
        self._client.join()

    def _on_error(self, e: Exception, _: Any) -> None:
        self._logger.error(f"Error. {e}")
