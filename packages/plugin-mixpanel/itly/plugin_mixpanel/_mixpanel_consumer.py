import atexit
import queue
from datetime import timedelta
from typing import Callable, Optional, List, NamedTuple

from mixpanel import Consumer

from itly.sdk import AsyncConsumer, AsyncConsumerMessage


Request = NamedTuple("Request", [("endpoint", str), ("data", str)])


class MixpanelConsumer(object):
    def __init__(self, api_key, flush_queue_size, flush_interval, on_error, api_host=None, send_request=None):
        # type: (str, int, timedelta, Callable[[str], None], Optional[str], Optional[Callable[[Request], None]]) -> None
        self.api_key = api_key
        self.on_error = on_error
        self._consumer = Consumer(api_host=api_host) if api_host else Consumer()
        self._consumer._endpoints["alias"] = self._consumer._endpoints["events"]
        self._queue = AsyncConsumer.create_queue()  # type: queue.Queue
        self._async_consumer = AsyncConsumer(message_queue=self._queue, do_upload=self._upload_batch, flush_queue_size=flush_queue_size, flush_interval=flush_interval)
        self._send_request = send_request if send_request is not None else self._send_request_default  # type: Callable[[Request], None]
        atexit.register(self.shutdown)
        self._async_consumer.start()

    def send(self, endpoint, json_message, api_key=None):
        # type: (str, str, Optional[str]) -> None
        try:
            self._queue.put(AsyncConsumerMessage(endpoint, json_message))
        except queue.Full:
            self.on_error("async queue is full")

    def _upload_batch(self, batch):
        # type: (List[AsyncConsumerMessage]) -> None
        endpoint = batch[0].message_type
        batch_json = '[{0}]'.format(','.join(message.data for message in batch))
        try:
            self._send_request(Request(endpoint=endpoint, data=batch_json))
        except Exception as e:
            self.on_error(str(e))

    def _send_request_default(self, request):
        # type: (Request) -> None
        self._consumer.send(request.endpoint, request.data, self.api_key)

    def shutdown(self):
        # type: () -> None
        self._async_consumer.shutdown()

    def flush(self):
        # type: () -> None
        self._async_consumer.flush()
