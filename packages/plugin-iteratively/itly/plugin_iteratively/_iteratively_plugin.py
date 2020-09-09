from datetime import timedelta
from typing import Optional, Callable, NamedTuple

from itly.sdk import Plugin, PluginLoadOptions, Properties, Event, Environment, ValidationResponse, Logger
from ._iteratively_client import IterativelyClient, TrackType, Request


class IterativelyOptions(NamedTuple):
    url: Optional[str] = None
    environment: Environment = Environment.DEVELOPMENT
    omit_values: bool = False
    flush_queue_size: int = 10
    flush_interval_ms: int = 1000
    disabled: Optional[bool] = None


class IterativelyPlugin(Plugin):
    def __init__(self, api_key: str, options: IterativelyOptions) -> None:
        self._api_key: str = api_key
        self._options: IterativelyOptions = options._replace(
            disabled=options.disabled if options.disabled is not None else options.environment == Environment.PRODUCTION
        )
        self._client: Optional[IterativelyClient] = None
        self._logger: Logger = Logger.NONE
        self._send_request: Optional[Callable[[Request], None]] = None

    def id(self) -> str:
        return 'iteratively'

    def load(self, options: PluginLoadOptions) -> None:
        if self._options.disabled:
            options.logger.info("disabled")
            return

        assert self._options.url is not None
        self._client = IterativelyClient(api_endpoint=self._options.url, api_key=self._api_key,
                                         flush_queue_size=self._options.flush_queue_size, flush_interval=timedelta(milliseconds=self._options.flush_interval_ms),
                                         omit_values=self._options.omit_values, on_error=self._on_error, send_request=self._send_request)
        self._logger = options.logger

    def identify(self, user_id: str, properties: Optional[Properties]) -> None:
        if self._options.disabled:
            return

        assert self._client is not None
        self._client.track(track_type=TrackType.IDENTIFY,
                           properties=properties)

    def group(self, user_id: str, group_id: str, properties: Optional[Properties]) -> None:
        if self._options.disabled:
            return

        assert self._client is not None
        self._client.track(track_type=TrackType.GROUP,
                           properties=properties)

    def page(self, user_id: str, category: Optional[str], name: Optional[str], properties: Optional[Properties]) -> None:
        if self._options.disabled:
            return

        assert self._client is not None
        self._client.track(track_type=TrackType.PAGE,
                           properties=properties)

    def track(self, user_id: str, event: Event) -> None:
        if self._options.disabled:
            return

        assert self._client is not None
        self._client.track(track_type=TrackType.TRACK,
                           event=event,
                           properties=event.properties)

    def flush(self) -> None:
        if self._options.disabled:
            return

        assert self._client is not None
        self._client.flush()

    def shutdown(self) -> None:
        if self._options.disabled:
            return

        assert self._client is not None
        self._client.shutdown()

    def on_validation_error(self, validation: ValidationResponse, event: Event) -> None:
        if self._options.disabled:
            return

        assert self._client is not None
        if event.name in (TrackType.GROUP.value, TrackType.IDENTIFY.value, TrackType.PAGE.value):
            self._client.track(TrackType[event.name],
                               properties=event.properties,
                               validation=validation)
        else:
            self._client.track(TrackType.TRACK,
                               event=event,
                               properties=event.properties,
                               validation=validation)

    def _on_error(self, err: str) -> None:
        message = "Error. {0}".format(err)
        self._logger.error(message)
