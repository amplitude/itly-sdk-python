from typing import Optional

from itly.sdk import Plugin, PluginOptions, Properties, Event, Logger
from ._amplitude_client import AmplitudeClient


class AmplitudeOptions(object):
    def __init__(self, max_queue_size=10000, events_endpoint=None, identification_endpoint=None):
        # type: (int, Optional[str], Optional[str]) -> None
        self.max_queue_size = max_queue_size
        self.events_endpoint = events_endpoint
        self.identification_endpoint = identification_endpoint


class AmplitudePlugin(Plugin):
    def __init__(self, api_key, options):
        # type: (str, AmplitudeOptions) -> None
        self._api_key = api_key
        self._options = options
        self._client = None  # type: Optional[AmplitudeClient]
        self._logger = Logger.NONE  # type: Logger

    def id(self):
        # type: () -> str
        return 'amplitude'

    def load(self, options):
        # type: (PluginOptions) -> None
        self._client = AmplitudeClient(api_key=self._api_key, max_queue_size=self._options.max_queue_size, on_error=self._on_error,
                                       events_endpoint=self._options.events_endpoint, identification_endpoint=self._options.identification_endpoint)
        self._logger = options.logger

    def identify(self, user_id, properties):
        # type: (str, Optional[Properties]) -> None
        assert self._client is not None
        self._client.identify(user_id=user_id,
                              properties=properties.to_json() if properties is not None else None)

    def track(self, user_id, event):
        # type: (str, Event) -> None
        assert self._client is not None
        self._client.track(user_id=user_id,
                           event_name=event.name,
                           properties=event.properties.to_json() if event.properties is not None else None)

    def flush(self):
        # type: () -> None
        assert self._client is not None
        self._client.flush()

    def shutdown(self):
        # type: () -> None
        assert self._client is not None
        self._client.join()

    def _on_error(self, err):
        # type: (str) -> None
        message = "Error. {0}".format(str(err))
        self._logger.error(message)
