import time
from datetime import datetime, timedelta
from typing import Optional, Callable

from itly.sdk import Plugin, PluginLoadOptions, Properties, Event, Logger
from ._mixpanel_client import MixpanelClient
from ._mixpanel_consumer import Request


class MixpanelOptions(object):
    def __init__(self, api_host=None, flush_queue_size=10, flush_interval_ms=1000):
        # type: (Optional[str], int, int) -> None
        self.api_host = api_host  # type: Optional[str]
        self.flush_queue_size = flush_queue_size  # type: int
        self.flush_interval_ms = flush_interval_ms  # type: int


class MixpanelPlugin(Plugin):
    def __init__(self, api_key, options):
        # type: (str, MixpanelOptions) -> None
        self._api_key = api_key  # type: str
        self._options = options  # type: MixpanelOptions
        self._client = None  # type: Optional[MixpanelClient]
        self._logger = Logger.NONE  # type: Logger
        self._send_request = None  # type: Optional[Callable[[Request], None]]

    def id(self):
        # type: () -> str
        return 'mixpanel'

    def load(self, options):
        # type: (PluginLoadOptions) -> None
        self._client = MixpanelClient(api_key=self._api_key, on_error=self._on_error,
                                      flush_queue_size=self._options.flush_queue_size, flush_interval=timedelta(milliseconds=self._options.flush_interval_ms),
                                      api_host=self._options.api_host, send_request=self._send_request)
        self._logger = options.logger

    def alias(self, user_id, previous_id, timestamp=None):
        # type: (str, str, Optional[datetime]) -> None
        assert self._client is not None
        self._client.alias(
            original=user_id,
            alias_id=previous_id)

    def identify(self, user_id, properties, timestamp=None):
        # type: (str, Optional[Properties], Optional[datetime]) -> None
        assert self._client is not None
        if timestamp is None:
            timestamp = datetime.utcnow()
        self._client.people_update({
            '$distinct_id': user_id,
            '$time': int(time.mktime(timestamp.timetuple())),
            '$set': properties.to_json() if properties is not None else {},
        })

    def track(self, user_id, event, timestamp=None):
        # type: (str, Event, Optional[datetime]) -> None
        assert self._client is not None

        if timestamp is None:
            timestamp = datetime.utcnow()
        json_properties = {"time": int(time.mktime(timestamp.timetuple()))}
        if event.properties is not None:
            json_properties.update(event.properties.to_json())
        self._client.track(
            distinct_id=user_id,
            event_name=event.name,
            properties=json_properties)

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
