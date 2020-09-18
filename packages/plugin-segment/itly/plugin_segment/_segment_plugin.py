from typing import Optional, NamedTuple, Any

import analytics

from itly.sdk import Plugin, PluginLoadOptions, Properties, Event, Logger


class SegmentOptions(NamedTuple):
    host: Optional[str] = None


class SegmentPlugin(Plugin):
    def __init__(self, write_key: str, options: Optional[SegmentOptions] = None) -> None:
        self._write_key: str = write_key
        self._options: SegmentOptions = options if options is not None else SegmentOptions()
        self._client: Optional[analytics.Client] = None
        self._logger: Logger = Logger.NONE

    def id(self) -> str:
        return 'segment'

    def load(self, options: PluginLoadOptions) -> None:
        self._client = analytics.Client(write_key=self._write_key, on_error=self._on_error, host=self._options.host)
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
