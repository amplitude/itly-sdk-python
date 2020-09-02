from datetime import datetime, timedelta
from typing import Callable, Optional

from itly.sdk import Plugin, PluginLoadOptions, Properties, Event, Logger
from ._segment_client import SegmentClient, Request


class SegmentOptions(object):
    def __init__(self, flush_queue_size=10, flush_interval_ms=1000, host=None):
        # type: (int, int, Optional[str]) -> None
        self.flush_queue_size = flush_queue_size  # type: int
        self.flush_interval_ms = flush_interval_ms  # type: int
        self.host = host  # type: Optional[str]


class SegmentPlugin(Plugin):
    def __init__(self, write_key, options):
        # type: (str, SegmentOptions) -> None
        self._write_key = write_key  # type: str
        self._options = options  # type: SegmentOptions
        self._client = None  # type: Optional[SegmentClient]
        self._logger = Logger.NONE  # type: Logger
        self._send_request = None  # type : Optional[Callable[[Request], None]]

    def id(self):
        # type: () -> str
        return 'segment'

    def load(self, options):
        # type: (PluginLoadOptions) -> None
        self._client = SegmentClient(write_key=self._write_key, on_error=self._on_error,
                                     flush_queue_size=self._options.flush_queue_size, flush_interval=timedelta(milliseconds=self._options.flush_interval_ms),
                                     host=self._options.host, send_request=self._send_request)
        self._logger = options.logger

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
