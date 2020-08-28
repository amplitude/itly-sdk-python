import atexit
import enum
import queue
from datetime import datetime, timedelta
from typing import Callable, List, Optional, NamedTuple, Any

import requests

from itly.sdk import AsyncConsumer, AsyncConsumerMessage, Event, Properties, ValidationResponse

Request = NamedTuple('Request', [('data', Any)])


class TrackType(enum.Enum):
    TRACK = 'track'
    GROUP = 'group'
    IDENTIFY = 'identify'
    PAGE = 'page'


class IterativelyClient(object):
    def __init__(self, api_endpoint, api_key, flush_queue_size, flush_interval, omit_values, on_error, send_request):
        # type: (str, str, int, timedelta, bool, Callable[[str], None], Optional[Callable[[Request], None]]) -> None
        self.api_endpoint = api_endpoint
        self.api_key = api_key
        self._omit_values = omit_values
        self.on_error = on_error
        self._queue = AsyncConsumer.create_queue()  # type: queue.Queue
        self._send_request = send_request if send_request is not None else self._send_request_default  # type: Callable[[Request], None]
        self._consumer = AsyncConsumer(self._queue, do_upload=self._upload_batch, flush_queue_size=flush_queue_size, flush_interval=flush_interval)
        atexit.register(self.shutdown)
        self._consumer.start()

    def track(self, track_type, event=None, properties=None, validation=None, timestamp=None):
        # type: (TrackType, Optional[Event], Optional[Properties], Optional[ValidationResponse], Optional[datetime]) -> None
        if timestamp is None:
            timestamp = datetime.utcnow()
        model = {
            "type": track_type.value,
            "dateSent": timestamp.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + "Z",
            "properties": {},
            "valid": True,
            "validation": {
                "details": "",
            },
        }

        if event is not None:
            model['eventName'] = event.name
            if event.id is not None:
                model['eventId'] = event.id
            if event.version is not None:
                model['eventSchemaVersion'] = event.version

        if properties is not None:
            if self._omit_values:
                model['properties'] = {k: None for k in properties.to_json()}
            else:
                model['properties'] = properties.to_json()

        if validation is not None:
            model['valid'] = validation.valid
            if not self._omit_values and validation.message is not None:
                model['validation']['details'] = validation.message

        self._enqueue(AsyncConsumerMessage("events", model))

    def _upload_batch(self, batch):
        # type: (List[AsyncConsumerMessage]) -> None
        data = {
            'objects': [message.data for message in batch],
        }
        try:
            self._send_request(Request(data=data))
        except Exception as e:
            self.on_error(str(e))

    def _send_request_default(self, request):
        # type: (Request) -> None
        try:
            response = requests.post(self.api_endpoint, json=request.data, headers={'Authorization': 'Bearer ' + self.api_key})
        except Exception as e:
            raise Exception("A unhandled exception occurred. ({0}).".format(e))
        if response.status_code < 300:
            return
        if 500 <= response.status_code <= 599:
            raise Exception("Upload received error response from server ({0}).".format(response.status_code))
        if response.status_code == 429:
            raise Exception("Upload rejected due to rate limiting ({0}).".format(response.status_code))
        raise Exception("Upload failed due to unhandled HTTP error ({0}).".format(response.status_code))

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
