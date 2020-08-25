from typing import Callable, Optional

import analytics

from itly.sdk import Plugin, PluginOptions, Properties, Event


class SegmentOptions(object):
    def __init__(self, host=None, debug=False, max_queue_size=10000, send=True, on_error=None):
        # type: (str, bool, int, bool, Callable) -> None
        self.host = host
        self.debug = debug
        self.max_queue_size = max_queue_size
        self.send = send
        self.on_error = on_error


class SegmentPlugin(Plugin):
    def __init__(self, write_key, options):
        # type: (str, SegmentOptions) -> None
        self._write_key = write_key
        self._options = options
        self._client = None  # type: Optional[analytics.Client]

    def id(self):
        # type: () -> str
        return 'segment'

    def load(self, options):
        # type: (PluginOptions) -> None
        self._client = analytics.Client(write_key=self._write_key, host=self._options.host, debug=self._options.debug,
                                        max_queue_size=self._options.max_queue_size, send=self._options.send, on_error=self._options.on_error)

    def alias(self, user_id, previous_id):
        # type: (str, str) -> None
        assert self._client is not None
        self._client.alias(user_id=user_id,
                           previous_id=previous_id)

    def identify(self, user_id, properties):
        # type: (str, Optional[Properties]) -> None
        assert self._client is not None
        self._client.identify(user_id=user_id,
                              traits=properties.to_json() if properties is not None else None)

    def group(self, user_id, group_id, properties):
        # type: (str, str, Optional[Properties]) -> None
        assert self._client is not None
        self._client.group(user_id=user_id,
                           group_id=group_id,
                           traits=properties.to_json() if properties is not None else None)

    def page(self, user_id, category, name, properties):
        # type: (str, Optional[str], Optional[str], Optional[Properties]) -> None
        assert self._client is not None
        self._client.page(user_id=user_id,
                          category=category,
                          name=name,
                          properties=properties.to_json() if properties is not None else None)

    def track(self, user_id, event):
        # type: (str, Event) -> None
        assert self._client is not None
        self._client.track(user_id=user_id,
                           event=event.name,
                           properties=event.properties.to_json() if event.properties is not None else None)

    def flush(self):
        # type: () -> None
        assert self._client is not None
        self._client.flush()

    def shutdown(self):
        # type: () -> None
        assert self._client is not None
        self._client.join()
