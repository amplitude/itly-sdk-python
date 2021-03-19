import atexit
import enum
import queue
import threading
from datetime import datetime, timedelta
from typing import Callable, List, Optional, Any

import requests
from requests import Session

from itly_sdk import Event, Properties, ValidationResponse
from itly_sdk.internal import AsyncConsumer, AsyncConsumerMessage, backoff
from ._retry_options import IterativelyRetryOptions


class TrackType(enum.Enum):
    TRACK = 'track'
    GROUP = 'group'
    IDENTIFY = 'identify'
    PAGE = 'page'


class IterativelyClient:
    def __init__(self,
                 api_endpoint: str,
                 api_key: str,
                 flush_queue_size: int,
                 flush_interval: timedelta,
                 request_timeout: timedelta,
                 omit_values: bool, retry_options: IterativelyRetryOptions,
                 on_error: Callable[[str], None]) -> None:
        self._api_endpoint = api_endpoint
        self._api_key = api_key
        self._request_timeout = request_timeout
        self._omit_values = omit_values
        self._retry_options = retry_options
        self._on_error = on_error
        self._queue: queue.Queue = AsyncConsumer.create_queue()
        self._session = Session()
        self._consumer = AsyncConsumer(self._queue,
                                       do_upload=self._upload_batch,
                                       flush_queue_size=flush_queue_size,
                                       flush_interval=flush_interval)
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

    def _upload_batch(self, batch: List[AsyncConsumerMessage], stop_event: threading.Event) -> None:
        data = {
            'objects': [message.data for message in batch],
        }
        try:
            self._send_request(data, stop_event)
        except Exception as e:
            self._on_error(str(e))

    def _send_request(self, data: Any, stop_event: threading.Event) -> None:
        need_retry = self._post_request(data)
        if not need_retry:
            return
        for delay in backoff(start=self._retry_options.delay_initial.total_seconds(),
                             stop=self._retry_options.delay_maximum.total_seconds(),
                             count=self._retry_options.max_retries - 1,
                             factor=2.0,
                             jitter=1.0):
            if stop_event.wait(delay):
                return

            need_retry = self._post_request(data)
            if not need_retry:
                return
        raise Exception("Failed to upload events. Maximum attempts exceeded.")

    def _post_request(self, data: Any) -> bool:
        try:
            response = self._session.post(self._api_endpoint,
                                          json=data,
                                          headers={'Authorization': 'Bearer ' + self._api_key},
                                          timeout=self._request_timeout.total_seconds())
        except requests.ConnectionError:
            return True
        except requests.Timeout:
            return True
        except Exception as e:
            raise Exception(f"A unhandled exception occurred. ({e}).")

        if 200 <= response.status_code < 300:
            return False
        if 500 <= response.status_code < 600:
            return True
        if response.status_code == 429:
            return True
        raise Exception(f"Upload failed due to unhandled HTTP error ({response.status_code}).")

    def shutdown(self) -> None:
        self._consumer.shutdown()

    def _enqueue(self, message: AsyncConsumerMessage) -> None:
        try:
            self._queue.put(message)
        except queue.Full:
            self._on_error("async queue is full")

    def flush(self) -> None:
        self._consumer.flush()
