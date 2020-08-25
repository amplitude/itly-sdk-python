import atexit
from collections import namedtuple
from typing import Dict, Callable, List, Optional
import json
import queue
import time

import requests

from itly.sdk import AsyncConsumer, AsyncConsumerMessage

Endpoint = namedtuple("Endpoint", ["url", "is_json"])


class AmplitudeClient(object):
    def __init__(self, api_key, max_queue_size, on_error, events_endpoint=None, identification_endpoint=None):
        # type: (str, int, Callable[[str], None], Optional[str], Optional[str]) -> None
        self.api_key = api_key
        self.on_error = on_error
        self._queue = queue.Queue(maxsize=max_queue_size)  # type: queue.Queue
        self._endpoints = {
            "events": Endpoint(url=events_endpoint or "https://api.amplitude.com/2/httpapi", is_json=True),
            "identification": Endpoint(url=identification_endpoint or "https://api.amplitude.com/identify", is_json=False),
        }
        self._consumer = AsyncConsumer(self._queue, self._send, on_error)
        atexit.register(self.join)
        self._consumer.start()

    def track(self, user_id, event_name, properties):
        # type: (str, str, Dict) -> None
        data = {
            "user_id": user_id,
            "event_type": event_name,
            "time": int(time.time() * 1000),
            "event_properties": properties if properties is not None else {}
        }
        self._enqueue(AsyncConsumerMessage("events", data))

    def identify(self, user_id, properties):
        # type: (str, Dict) -> None
        data = {
            "user_id": user_id,
            "user_properties": properties if properties is not None else {}
        }
        self._enqueue(AsyncConsumerMessage("identification", data))

    def _send(self, batch):
        # type: (List[AsyncConsumerMessage]) -> None
        message_type = batch[0].message_type
        endpoint_url, is_json = self._endpoints[message_type]
        if is_json:
            data = {
                message_type: [message.data for message in batch],
                "api_key": self.api_key
            }
            response = requests.post(endpoint_url, json=data)
        else:
            data = {
                message_type: json.dumps([message.data for message in batch]),
                "api_key": self.api_key
            }
            response = requests.post(endpoint_url, data=data)
        if response.status_code >= 300:
            self.on_error('(Itly) Unexpected status code for {0}: {1}'.format(endpoint_url, response.status_code))

    def join(self):
        # type: () -> None
        self._consumer.pause()
        try:
            self._consumer.join()
        except RuntimeError:
            # consumer thread has not started
            pass

    def _enqueue(self, message):
        # type: (AsyncConsumerMessage) -> None
        try:
            self._queue.put(message)
        except queue.Full:
            self.on_error("async queue is full")

    def flush(self):
        # type: () -> None
        self._queue.join()
