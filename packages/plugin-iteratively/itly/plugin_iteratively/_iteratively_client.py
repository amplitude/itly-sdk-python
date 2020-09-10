import atexit
import enum
import queue
from datetime import datetime, timedelta
from typing import Callable, List, Optional, NamedTuple, Any

from requests import Session

from itly.sdk import AsyncConsumer, AsyncConsumerMessage, Event, Properties, ValidationResponse


class Request(NamedTuple):
    data: Any


class TrackType(enum.Enum):
    TRACK = 'track'
    GROUP = 'group'
    IDENTIFY = 'identify'
    PAGE = 'page'


class IterativelyClient:
    def __init__(self, api_endpoint: str, api_key: str, flush_queue_size: int, flush_interval: timedelta, omit_values: bool,
                 on_error: Callable[[str], None], send_request: Optional[Callable[[Request], None]]) -> None:
        self.api_endpoint = api_endpoint
        self.api_key = api_key
        self._omit_values = omit_values
        self.on_error = on_error
        self._queue: queue.Queue = AsyncConsumer.create_queue()
        self._send_request: Callable[[Request], None] = send_request if send_request is not None else self._send_request_default
        self._session = Session()
        self._consumer = AsyncConsumer(self._queue, do_upload=self._upload_batch, flush_queue_size=flush_queue_size, flush_interval=flush_interval)
        atexit.register(self.shutdown)
        self._consumer.start()

    def track(self, track_type: TrackType, event: Optional[Event] = None, properties: Optional[Properties] = None,
              validation: Optional[ValidationResponse] = None) -> None:
        date_sent = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + "Z"
        model = {
            "type": track_type.value,
            "dateSent": date_sent,
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

    def _upload_batch(self, batch: List[AsyncConsumerMessage]) -> None:
        data = {
            'objects': [message.data for message in batch],
        }
        try:
            self._send_request(Request(data=data))
        except Exception as e:
            self.on_error(str(e))

    def _send_request_default(self, request: Request) -> None:
        try:
            response = self._session.post(self.api_endpoint, json=request.data, headers={'Authorization': 'Bearer ' + self.api_key})
        except Exception as e:
            raise Exception(f"A unhandled exception occurred. ({e}).")
        if response.status_code < 300:
            return
        if 500 <= response.status_code <= 599:
            raise Exception(f"Upload received error response from server ({response.status_code}).")
        if response.status_code == 429:
            raise Exception(f"Upload rejected due to rate limiting ({response.status_code}).")
        raise Exception(f"Upload failed due to unhandled HTTP error ({response.status_code}).")

    def shutdown(self) -> None:
        self._consumer.shutdown()

    def _enqueue(self, message: AsyncConsumerMessage) -> None:
        try:
            self._queue.put(message)
        except queue.Full:
            self.on_error("async queue is full")

    def flush(self) -> None:
        self._consumer.flush()
