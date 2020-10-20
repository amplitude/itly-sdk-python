from datetime import timedelta
from typing import Optional, NamedTuple, List

from itly_sdk import Plugin, PluginLoadOptions, Properties, Event, Environment, ValidationResponse, Logger
from ._iteratively_client import IterativelyClient, TrackType
from ._retry_options import IterativelyRetryOptions


class IterativelyOptions(NamedTuple):
    omit_values: bool = False
    flush_queue_size: int = 10
    flush_interval: timedelta = timedelta(seconds=1)
    disabled: Optional[bool] = None
    retry_options: IterativelyRetryOptions = IterativelyRetryOptions()
    request_timeout: timedelta = timedelta(seconds=15)


class IterativelyPlugin(Plugin):
    def __init__(self, api_key: str, url: str, options: IterativelyOptions) -> None:
        self._api_key: str = api_key
        self._url: str = url
        self._options: IterativelyOptions = options
        self._disabled: Optional[bool] = options.disabled
        self._client: Optional[IterativelyClient] = None
        self._logger: Logger = Logger.NONE

    def id(self) -> str:
        return 'iteratively'

    def load(self, options: PluginLoadOptions) -> None:
        if self._disabled is None:
            self._disabled = options.environment == Environment.PRODUCTION

        if self._disabled:
            options.logger.info("disabled")
            return

        self._client = IterativelyClient(api_endpoint=self._url,
                                         api_key=self._api_key,
                                         flush_queue_size=self._options.flush_queue_size,
                                         flush_interval=self._options.flush_interval,
                                         request_timeout=self._options.request_timeout,
                                         retry_options=self._options.retry_options,
                                         omit_values=self._options.omit_values,
                                         on_error=self._on_error)
        self._logger = options.logger

    def post_identify(self,
                      user_id: str,
                      properties: Optional[Properties],
                      validation_results: List[ValidationResponse]) -> None:
        if self._disabled:
            return

        assert self._client is not None
        self._client.track(track_type=TrackType.IDENTIFY,
                           properties=properties,
                           validation=self._first_failed_validation(validation_results))

    def post_group(self,
                   user_id: str,
                   group_id: str,
                   properties: Optional[Properties],
                   validation_results: List[ValidationResponse]) -> None:
        if self._disabled:
            return

        assert self._client is not None
        self._client.track(track_type=TrackType.GROUP,
                           properties=properties,
                           validation=self._first_failed_validation(validation_results))

    def post_page(self,
                  user_id: str,
                  category: Optional[str],
                  name: Optional[str],
                  properties: Optional[Properties],
                  validation_results: List[ValidationResponse]) -> None:
        if self._disabled:
            return

        assert self._client is not None
        self._client.track(track_type=TrackType.PAGE,
                           properties=properties,
                           validation=self._first_failed_validation(validation_results))

    def post_track(self, user_id: str, event: Event, validation_results: List[ValidationResponse]) -> None:
        if self._disabled:
            return

        assert self._client is not None
        self._client.track(track_type=TrackType.TRACK,
                           event=event,
                           properties=event.properties,
                           validation=self._first_failed_validation(validation_results))

    def flush(self) -> None:
        if self._disabled:
            return

        assert self._client is not None
        self._client.flush()

    def shutdown(self) -> None:
        if self._disabled:
            return

        assert self._client is not None
        self._client.shutdown()

    def _on_error(self, err: str) -> None:
        self._logger.error(f"Error. {err}")

    @staticmethod
    def _first_failed_validation(validation_results: List[ValidationResponse]) -> Optional[ValidationResponse]:
        for result in validation_results:
            if not result.valid:
                return result
        return None
