import atexit
import enum
import queue
from datetime import datetime, timedelta
from typing import Callable, List, Optional

import requests

from itly.sdk import AsyncConsumer, AsyncConsumerMessage, Event, Properties, ValidationResponse


class TrackType(enum.Enum):
    TRACK = 'track',
    GROUP = 'group',
    IDENTIFY = 'identify',
    PAGE = 'page',


class IterativelyClient(object):
    def __init__(self, api_endpoint, api_key, upload_size, upload_interval, omit_values, on_error):
        # type: (str, str, int, timedelta, bool, Callable[[str], None]) -> None
        self.api_endpoint = api_endpoint
        self.api_key = api_key
        self._omit_values = omit_values
        self.on_error = on_error
        self._queue = AsyncConsumer.create_queue()  # type: queue.Queue
        self._consumer = AsyncConsumer(self._queue, do_upload=self._send, upload_size=upload_size, upload_interval=upload_interval)
        atexit.register(self.join)
        self._consumer.start()

    def track(self, track_type, event=None, properties=None, validation=None):
        # type: (TrackType, Optional[Event], Optional[Properties], Optional[ValidationResponse]) -> None
        model = {
            "type": track_type.value,
            "dateSent": datetime.utcnow().isoformat() + "Z",
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

    def _send(self, batch):
        # type: (List[AsyncConsumerMessage]) -> None
        data = {
            'objects': batch,
        }
        response = requests.post(self.api_endpoint, json=data, headers={'Authorization': 'Bearer ' + self.api_key})
        if response.status_code >= 300:
            self.on_error('Unexpected status code {0}'.format(response.status_code))

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
        self._consumer.flush()
