from datetime import datetime, timedelta
from typing import Callable, Optional

from itly.sdk import Plugin, PluginOptions, Properties, Event
from ._segment_client import SegmentClient, Request


class SegmentOptions(object):
    def __init__(self, flush_at=10, flush_interval=1000, host=None, send_request=None):
        # type: (int, int, Optional[str], Optional[Callable[[Request], None]]) -> None
        self.flush_at = flush_at  # type: int
        self.send_request = send_request  # type: Optional[Callable[[Request], None]]
        self.flush_interval = flush_interval  # type: int
        self.host = host  # type: Optional[str]


class SegmentPlugin(Plugin):
    def __init__(self, write_key, options):
        # type: (str, SegmentOptions) -> None
        self._write_key = write_key  # type: str
        self._options = options  # type: SegmentOptions
        self._client = None  # type: Optional[SegmentClient]

    def id(self):
        # type: () -> str
        return 'segment'

    def load(self, options):
        # type: (PluginOptions) -> None
        self._client = SegmentClient(write_key=self._write_key, on_error=self._on_error,
                                     upload_size=self._options.flush_at, upload_interval=timedelta(milliseconds=self._options.flush_interval),
                                     host=self._options.host, send_request=self._options.send_request)

    def alias(self, user_id, previous_id, timestamp=None):
        # type: (str, str, Optional[datetime]) -> None
        assert self._client is not None
        self._client.alias(user_id=user_id,
                           previous_id=previous_id,
                           timestamp=timestamp)

    def identify(self, user_id, properties, timestamp=None):
        # type: (str, Optional[Properties], Optional[datetime]) -> None
        assert self._client is not None
        self._client.identify(user_id=user_id,
                              traits=properties.to_json() if properties is not None else None,
                              timestamp=timestamp)

    def group(self, user_id, group_id, properties, timestamp=None):
        # type: (str, str, Optional[Properties], Optional[datetime]) -> None
        assert self._client is not None
        self._client.group(user_id=user_id,
                           group_id=group_id,
                           traits=properties.to_json() if properties is not None else None,
                           timestamp=timestamp)

    def page(self, user_id, category, name, properties, timestamp=None):
        # type: (str, Optional[str], Optional[str], Optional[Properties], Optional[datetime]) -> None
        assert self._client is not None
        self._client.page(user_id=user_id,
                          category=category,
                          name=name,
                          properties=properties.to_json() if properties is not None else None,
                          timestamp=timestamp)

    def track(self, user_id, event, timestamp=None):
        # type: (str, Event, Optional[datetime]) -> None
        assert self._client is not None
        self._client.track(user_id=user_id,
                           event=event.name,
                           properties=event.properties.to_json() if event.properties is not None else None,
                           timestamp=timestamp)

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
