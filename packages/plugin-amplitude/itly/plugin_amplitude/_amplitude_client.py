import atexit
from datetime import timedelta, datetime
from typing import Dict, Callable, List, Optional, NamedTuple, Any
import json
import queue
import time

from requests import Session

from itly.sdk import AsyncConsumer, AsyncConsumerMessage

Endpoint = NamedTuple("Endpoint", [("url", str), ("is_json", bool)])
Request = NamedTuple("Request", [("url", str), ("is_json", bool), ("data", Any)])


class AmplitudeClient(object):
    def __init__(self, api_key, on_error, flush_queue_size, flush_interval, events_endpoint, identification_endpoint, send_request):
        # type: (str, Callable[[str], None], int, timedelta, Optional[str], Optional[str], Optional[Callable[[Request], None]]) -> None
        self.api_key = api_key
        self.on_error = on_error
        self._queue = AsyncConsumer.create_queue()  # type: queue.Queue
        self._endpoints = {
            "events": Endpoint(url=events_endpoint or "https://api.amplitude.com/2/httpapi", is_json=True),
            "identification": Endpoint(url=identification_endpoint or "https://api.amplitude.com/identify", is_json=False),
        }
        self._send_request = send_request if send_request is not None else self._send_request_default  # type: Callable[[Request], None]
        self._session = Session()
        self._consumer = AsyncConsumer(message_queue=self._queue, do_upload=self._upload_batch, flush_queue_size=flush_queue_size, flush_interval=flush_interval)
        atexit.register(self.shutdown)
        self._consumer.start()

    def track(self, user_id, event_name, properties, timestamp):
        # type: (str, str, Dict, datetime) -> None
        data = {
            "user_id": user_id,
            "event_type": event_name,
            "time": int(time.mktime(timestamp.timetuple()) * 1000),
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

    def _upload_batch(self, batch):
        # type: (List[AsyncConsumerMessage]) -> None
        message_type = batch[0].message_type
        endpoint_url, is_json = self._endpoints[message_type]
        try:
            if is_json:
                data = {
                    message_type: [message.data for message in batch],
                    "api_key": self.api_key
                }
            else:
                data = {
                    message_type: json.dumps([message.data for message in batch]),
                    "api_key": self.api_key
                }
            self._send_request(Request(url=endpoint_url, is_json=is_json, data=data))
        except Exception as e:
            self.on_error(str(e))

    def _send_request_default(self, request):
        # type: (Request) -> None
        if request.is_json:
            response = self._session.post(request.url, json=request.data)
        else:
            response = self._session.post(request.url, data=request.data)
        if response.status_code >= 300:
            self.on_error('Unexpected status code for {0}: {1}'.format(request.url, response.status_code))

    def shutdown(self):
        # type: () -> None
        self._consumer.shutdown()

    def _enqueue(self, message):
        # type: (AsyncConsumerMessage) -> None
        try:
            self._queue.put(message)
        except queue.Full:
            self.on_error("async queue is full")

    def flush(self):
        # type: () -> None
        self._consumer.flush()
