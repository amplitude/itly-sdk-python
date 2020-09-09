from datetime import timedelta
from typing import Dict, Optional, Callable

from mixpanel import Mixpanel, json_dumps

from ._mixpanel_consumer import MixpanelConsumer, Request


class MixpanelClient(Mixpanel):
    def __init__(self, api_key: str, on_error: Callable[[str], None], flush_queue_size: int, flush_interval: timedelta,
                 api_host: Optional[str], send_request: Optional[Callable[[Request], None]]) -> None:
        consumer = MixpanelConsumer(api_key=api_key, on_error=on_error, api_host=api_host,
                                    flush_queue_size=flush_queue_size, flush_interval=flush_interval,
                                    send_request=send_request)
        super().__init__(token=api_key, consumer=consumer)

    def alias(self, alias_id: str, original: str, meta: Optional[Dict] = None) -> None:
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

    def flush(self) -> None:
        self._consumer.flush()

    def shutdown(self) -> None:
        self._consumer.shutdown()
