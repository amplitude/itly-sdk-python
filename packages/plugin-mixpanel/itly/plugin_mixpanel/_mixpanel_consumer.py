import atexit
import queue
from typing import Callable, Optional, List

from mixpanel import Consumer

from itly.sdk import AsyncConsumer, AsyncConsumerMessage


class MixpanelConsumer(object):
    def __init__(self, api_key, on_error, api_host=None):
        # type: (str, Callable[[str], None], Optional[str]) -> None
        self.api_key = api_key
        self.on_error = on_error
        self._consumer = Consumer(api_host=api_host)
        self._consumer._endpoints["alias"] = self._consumer._endpoints["events"]
        self._queue = AsyncConsumer.create_queue()  # type: queue.Queue
        self._async_consumer = AsyncConsumer(self._queue, self._send)
        atexit.register(self.join)
        self._async_consumer.start()

    def send(self, endpoint, json_message, api_key=None):
        # type: (str, str, Optional[str]) -> None
        try:
            self._queue.put(AsyncConsumerMessage(endpoint, json_message))
        except queue.Full:
            self.on_error("async queue is full")

    def _send(self, batch):
        # type: (List[AsyncConsumerMessage]) -> None
        endpoint = batch[0].message_type
        batch_json = '[{0}]'.format(','.join(message.data for message in batch))
        self._consumer.send(endpoint, batch_json, self.api_key)

    def join(self):
        # type: () -> None
        self._async_consumer.pause()
        try:
            self._async_consumer.join()
        except RuntimeError:
            # consumer thread has not started
            pass

    def flush(self):
        # type: () -> None
        self._async_consumer.flush()
