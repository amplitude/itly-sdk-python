import time
from typing import Optional

from itly.sdk import Plugin, PluginOptions, Properties, Event, Logger
from ._mixpanel_client import MixpanelClient
from ._mixpanel_consumer import MixpanelConsumer


class MixpanelOptions(object):
    def __init__(self, api_host=None):
        # type: (Optional[str]) -> None
        self.api_host = api_host  # type: Optional[str]


class MixpanelPlugin(Plugin):
    def __init__(self, api_key, options):
        # type: (str, MixpanelOptions) -> None
        self._api_key = api_key  # type: str
        self._options = options  # type: MixpanelOptions
        self._client = None  # type: Optional[MixpanelClient]
        self._consumer = None  # type: Optional[MixpanelConsumer]
        self._logger = Logger.NONE  # type: Logger

    def id(self):
        # type: () -> str
        return 'mixpanel'

    def load(self, options):
        # type: (PluginOptions) -> None
        self._consumer = MixpanelConsumer(api_key=self._api_key, on_error=self._on_error, api_host=self._options.api_host)
        self._client = MixpanelClient(token=self._api_key, consumer=self._consumer)
        self._logger = options.logger

    def alias(self, user_id, previous_id):
        # type: (str, str) -> None
        assert self._client is not None
        self._client.alias(
            original=user_id,
            alias_id=previous_id)

    def identify(self, user_id, properties):
        # type: (str, Optional[Properties]) -> None
        assert self._client is not None
        self._client.people_set(
            distinct_id=user_id,
            properties=properties.to_json() if properties is not None else {})

    def track(self, user_id, event):
        # type: (str, Event) -> None
        assert self._client is not None
        json_properties = {"time": int(time.time())}
        if event.properties is not None:
            json_properties.update(event.properties.to_json())
        self._client.track(
            distinct_id=user_id,
            event_name=event.name,
            properties=json_properties)

    def flush(self):
        # type: () -> None
        assert self._consumer is not None
        self._consumer.flush()

    def shutdown(self):
        # type: () -> None
        assert self._consumer is not None
        self._consumer.join()

    def _on_error(self, err):
        # type: (str) -> None
        message = "Error. {0}".format(err)
        self._logger.error(message)
