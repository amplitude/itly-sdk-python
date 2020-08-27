from datetime import timedelta, datetime
from typing import Optional

from itly.sdk import Plugin, PluginOptions, Properties, Event, Environment, ValidationResponse
from ._iteratively_client import IterativelyClient, TrackType


class IterativelyOptions(object):
    def __init__(self, url, environment, omit_values=False, flush_at=10, flush_interval=1000, disabled=None):
        # type: (str, Environment, bool, int, int, Optional[bool]) -> None
        self.url = url  # type: str
        self.environment = environment  # type: Environment
        self.omit_values = omit_values  # type: bool
        self.flush_at = flush_at  # type: int
        self.flush_interval = flush_interval  # type: int
        self.disabled = disabled if disabled is not None else environment == Environment.PRODUCTION  # type: bool


class IterativelyPlugin(Plugin):
    def __init__(self, api_key, options):
        # type: (str, IterativelyOptions) -> None
        self._api_key = api_key
        self._options = options
        self._client = None  # type: Optional[IterativelyClient]

    def id(self):
        # type: () -> str
        return 'segment'

    def load(self, options):
        # type: (PluginOptions) -> None
        self._client = IterativelyClient(api_endpoint=self._options.url, api_key=self._api_key,
                                         upload_size=self._options.flush_at, upload_interval=timedelta(milliseconds=self._options.flush_interval),
                                         omit_values=self._options.omit_values, on_error=self._on_error)

    def identify(self, user_id, properties, timestamp=None):
        # type: (str, Optional[Properties], Optional[datetime]) -> None
        assert self._client is not None
        self._client.track(track_type=TrackType.IDENTIFY,
                           properties=properties)

    def group(self, user_id, group_id, properties, timestamp=None):
        # type: (str, str, Optional[Properties], Optional[datetime]) -> None
        assert self._client is not None
        self._client.track(track_type=TrackType.GROUP,
                           properties=properties)

    def page(self, user_id, category, name, properties, timestamp=None):
        # type: (str, Optional[str], Optional[str], Optional[Properties], Optional[datetime]) -> None
        assert self._client is not None
        self._client.track(track_type=TrackType.PAGE,
                           properties=properties)

    def track(self, user_id, event, timestamp=None):
        # type: (str, Event, Optional[datetime]) -> None
        assert self._client is not None
        self._client.track(track_type=TrackType.TRACK,
                           event=event,
                           properties=event.properties)

    def flush(self):
        # type: () -> None
        assert self._client is not None
        self._client.flush()

    def shutdown(self):
        # type: () -> None
        assert self._client is not None
        self._client.shutdown()

    def on_validation_error(self, validation, event):
        # type: (ValidationResponse, Event) -> None
        assert self._client is not None
        if event.name in (TrackType.GROUP.value, TrackType.IDENTIFY.value, TrackType.PAGE.value):
            self._client.track(TrackType[event.name], properties=event.properties, validation=validation)
        else:
            self._client.track(TrackType.TRACK, event=event, properties=event.properties, validation=validation)

    def _on_error(self, err):
        # type: (str) -> None
        message = "Error. {0}".format(err)
        self._logger.error(message)
