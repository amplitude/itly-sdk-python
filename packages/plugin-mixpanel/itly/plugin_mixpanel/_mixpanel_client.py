from datetime import timedelta
from typing import Dict, Optional, Callable

from mixpanel import Mixpanel, json_dumps

from ._mixpanel_consumer import MixpanelConsumer, Request


class MixpanelClient(Mixpanel):
    def __init__(self, api_key, on_error, upload_size, upload_interval, api_host, send_request):
        # type: (str, Callable[[str], None], int, timedelta, Optional[str], Optional[Callable[[Request], None]]) -> None
        consumer = MixpanelConsumer(api_key=api_key, on_error=on_error, api_host=api_host,
                                    upload_size=upload_size, upload_interval=upload_interval,
                                    send_request=send_request)
        super(MixpanelClient, self).__init__(token=api_key, consumer=consumer)

    def alias(self, alias_id, original, meta=None):
        # type: (str, str, Optional[Dict]) -> None
        event = {
            'event': '$create_alias',
            'properties': {
                'distinct_id': original,
                'alias': alias_id,
                'token': self._token,
            },
        }
        if meta:
            event.update(meta)
        self._consumer.send('alias', json_dumps(event, cls=self._serializer))

    def flush(self):
        # type: () -> None
        self._consumer.flush()

    def shutdown(self):
        # type: () -> None
        self._consumer.shutdown()
