import atexit
import json
import queue
import time
from datetime import timedelta
from typing import Dict, Callable, List, Optional, NamedTuple, Any

from requests import Session

from itly_plugin_amplitude._amplitude_metadata import AmplitudeMetadata
from itly_sdk.internal import AsyncConsumer, AsyncConsumerMessage


class Endpoint(NamedTuple):
    url: str
    is_json: bool


class Request(NamedTuple):
    url: str
    is_json: bool
    data: Any


class AmplitudeClient:
    def __init__(self,
                 api_key: str,
                 on_error: Callable[[str], None],
                 flush_queue_size: int,
                 flush_interval: timedelta,
                 request_timeout: timedelta,
                 min_id_length: Optional[int],
                 events_endpoint: Optional[str],
                 identification_endpoint: Optional[str]) -> None:
        self._api_key = api_key
        self._request_timeout = request_timeout
        self._min_id_length = min_id_length
        self._on_error = on_error
        self._queue: queue.Queue = AsyncConsumer.create_queue()
        self._endpoints = {
            "events": Endpoint(url=events_endpoint or "https://api.amplitude.com/2/httpapi", is_json=True),
            "identification": Endpoint(url=identification_endpoint or "https://api.amplitude.com/identify",
                                       is_json=False),
        }
        self._session = Session()
        self._consumer = AsyncConsumer(message_queue=self._queue,
                                       do_upload=self._upload_batch,
                                       flush_queue_size=flush_queue_size,
                                       flush_interval=flush_interval)
        atexit.register(self.shutdown)
        self._consumer.start()

    def track(self, user_id: str, event_name: str, properties: Dict[str, Any], metadata: Optional[AmplitudeMetadata]) -> None:
        data = {k: v for (k, v) in vars(metadata).items() if v is not None} if metadata is not None else {}
        data["user_id"] = user_id
        data["event_type"] = event_name
        data["event_properties"] = properties if properties is not None else {}
        if "time" not in data:
            data["time"] = int(time.time() * 1000)
        self._enqueue(AsyncConsumerMessage("events", data))

    def identify(self, user_id: str, properties: Dict[str, Any], metadata: Optional[AmplitudeMetadata]) -> None:
        data = {k: v for (k, v) in vars(metadata).items() if v is not None} if metadata is not None else {}
        data["user_id"] = user_id
        data["user_properties"] = properties if properties is not None else {}
        self._enqueue(AsyncConsumerMessage("identification", data))

    def _upload_batch(self, batch: List[AsyncConsumerMessage]) -> None:
        message_type = batch[0].message_type
        endpoint_url, is_json = self._endpoints[message_type]
        try:
            if message_type == "events":
                data = {
                    "events": [message.data for message in batch],
                    "api_key": self._api_key,
                }
                if self._min_id_length is not None:
                    data["options"] = {"min_id_length": self._min_id_length}
            else:
                data = {
                    "identification": json.dumps([message.data for message in batch]),
                    "api_key": self._api_key
                }
            self._send_request(Request(url=endpoint_url, is_json=is_json, data=data))
        except Exception as e:
            self._on_error(str(e))

    def _send_request(self, request: Request) -> None:
        if request.is_json:
            response = self._session.post(request.url, json=request.data, timeout=self._request_timeout.total_seconds())
        else:
            response = self._session.post(request.url, data=request.data, timeout=self._request_timeout.total_seconds())
        if response.status_code >= 300:
            self._on_error(f'Unexpected status code for {request.url}: {response.status_code}')

    def shutdown(self) -> None:
        self._consumer.shutdown()

    def _enqueue(self, message: AsyncConsumerMessage) -> None:
        try:
            self._queue.put(message)
        except queue.Full:
            self._on_error("async queue is full")

    def flush(self) -> None:
        self._consumer.flush()
