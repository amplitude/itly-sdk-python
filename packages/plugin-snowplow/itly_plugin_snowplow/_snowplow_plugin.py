from typing import Optional, NamedTuple, Any

from snowplow_tracker import Subject, Tracker, AsyncEmitter, SelfDescribingJson

from itly_sdk import Plugin, PluginLoadOptions, Properties, Event, Logger


class SnowplowOptions(NamedTuple):
    pass


class SnowplowPlugin(Plugin):
    def __init__(self, vendor: str, url: str, options: Optional[SnowplowOptions] = None) -> None:
        self._protocol: Optional[str] = None
        if url.startswith("http://"):
            self._protocol = "http"
        elif url.startswith("https://"):
            self._protocol = "https"

        self._endpoint: str = (url[len(self._protocol + "://"):] if self._protocol is not None else url).rstrip("/")
        self._vendor = vendor
        self._options: SnowplowOptions = options if options is not None else SnowplowOptions()
        self._tracker: Optional[Tracker] = None
        self._logger: Logger = Logger.NONE

    def id(self) -> str:
        return 'snowplow'

    def load(self, options: PluginLoadOptions) -> None:
        self._logger = options.logger
        emitter = AsyncEmitter(self._endpoint, protocol=self._protocol, method="post", on_failure=self._on_failure)
        self._tracker = Tracker(emitter)

    def page(self, user_id: str, category: Optional[str], name: Optional[str], properties: Optional[Properties]) -> None:
        assert self._tracker is not None
        subject = Subject()
        subject.set_user_id(user_id)
        prev_subject = self._tracker.subject
        try:
            self._tracker.set_subject(subject)
            self._tracker.track_screen_view(name=name)
        finally:
            self._tracker.set_subject(prev_subject)

    def track(self, user_id: str, event: Event) -> None:
        assert self._tracker is not None
        subject = Subject()
        subject.set_user_id(user_id)
        prev_subject = self._tracker.subject
        try:
            self._tracker.set_subject(subject)
            schema_version = event.version.replace(".", "-")
            self._tracker.track_self_describing_event(SelfDescribingJson(
                f'iglu:{self._vendor}/{event.id}/jsonschema/{schema_version}',
                event.properties.to_json()
            ))
        finally:
            self._tracker.set_subject(prev_subject)

    def flush(self) -> None:
        assert self._tracker is not None
        self._tracker.flush()

    def _on_failure(self, sent_count: int, unsent: Any) -> None:
        self._logger.error("Error. Can't send events")
