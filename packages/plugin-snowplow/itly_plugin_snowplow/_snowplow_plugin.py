from typing import Optional, NamedTuple, Any, Callable

from snowplow_tracker import Subject, Tracker, AsyncEmitter, SelfDescribingJson

from itly_sdk import Plugin, PluginLoadOptions, Properties, Event, Logger


class SnowplowOptions(NamedTuple):
    """
    Snowplow Options

    Based on Snowplow AsyncEmitter options
    https://github.com/snowplow/snowplow-python-tracker/blob/master/snowplow_tracker/emitters.py#L62

    :param protocol:    The protocol to use - http or https. Defaults to http.
    :param port:        The collector port to connect to
    :param method:      The HTTP request method
    :param buffer_size: The maximum number of queued events before the buffer is flushed. Default is 10.
    :param on_success:  Callback executed after every HTTP request in a flush has status code 200
                        Gets passed the number of events flushed.
    :param on_failure:  Callback executed if at least one HTTP request in a flush has status code other than 200
                        Gets passed two arguments:
                        1) The number of events which were successfully sent
                        2) If method is "post": The unsent data in string form;
                           If method is "get":  An array of dictionaries corresponding to the unsent events' payloads
    :param byte_limit:  The size event list after reaching which queued events will be flushed
    """

    endpoint: str
    protocol: str = "http"
    port: Optional[int] = None
    method: str = "post"
    buffer_size: Optional[int] = None
    on_success: Optional[Callable[[int], None]] = None
    on_failure: Optional[Callable[[int, Any], None]] = None
    thread_count: int = 1
    byte_limit: Optional[int] = None


class SnowplowPlugin(Plugin):
    def __init__(self, vendor: str, options: SnowplowOptions) -> None:
        self._vendor = vendor
        if options.on_failure is None:
            options = options._replace(on_failure=self._on_failure)
        self._options: SnowplowOptions = options
        self._tracker: Optional[Tracker] = None
        self._logger: Logger = Logger.NONE

    def id(self) -> str:
        return 'snowplow'

    def load(self, options: PluginLoadOptions) -> None:
        self._logger = options.logger
        emitter = AsyncEmitter(
            **self._options._asdict(),
        )
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

    def shutdown(self) -> None:
        self.flush()

    def _on_failure(self, sent_count: int, unsent: Any) -> None:
        self._logger.error("Error. Can't send events")
