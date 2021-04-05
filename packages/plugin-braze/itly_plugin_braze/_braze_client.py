import atexit
import json
import queue
from datetime import timedelta, datetime
from threading import Event
from typing import Dict, List, Optional, Any

from requests import Session

from itly_sdk import Logger
from itly_sdk.internal import AsyncConsumer, AsyncConsumerMessage


class BrazeClient:
    def __init__(self,
                 base_url: str,
                 api_key: str,
                 flush_queue_size: int,
                 flush_interval: timedelta,
                 request_timeout: timedelta,
                 logger: Logger,
                 ) -> None:
        self._api_key = api_key
        self._request_timeout = request_timeout
        self._queue: queue.Queue = AsyncConsumer.create_queue()
        base_url = base_url.rstrip("/")
        self._user_track_url = f'{base_url}/users/track'
        self._session = Session()
        self._logger = logger
        self._consumer = AsyncConsumer(message_queue=self._queue,
                                       do_upload=self._upload_batch,
                                       flush_queue_size=flush_queue_size,
                                       flush_interval=flush_interval)
        atexit.register(self.shutdown)
        self._consumer.start()

    def identify(self, user_id: str, properties: Optional[Dict[str, Any]]) -> None:
        data = self._to_braze_properties(properties)
        data["external_id"] = user_id
        self._enqueue(AsyncConsumerMessage("", {"attributes": data}))

    def track(self, user_id: str, event_name: str, properties: Optional[Dict[str, Any]]) -> None:
        data = {
            "external_id": user_id,
            "name": event_name,
            "time": datetime.now().isoformat(),
            "properties": self._to_braze_properties(properties),
        }
        self._enqueue(AsyncConsumerMessage("", {"events": data}))

    def _upload_batch(self, batch: List[AsyncConsumerMessage], stop_event: Event) -> None:
        body = {}
        count = 0
        for event in batch:
            for key, value in event.data.items():
                if key not in body:
                    body[key] = []
                count += 1
                body[key].append(value)

        self._logger.info(f"uploading {count} items")
        try:
            response = self._session.post(
                self._user_track_url,
                headers={'Authorization': f'Bearer {self._api_key}'},
                json=body,
                timeout=self._request_timeout.total_seconds(),
            )
            if response.status_code >= 300:
                self._logger.error(f'unexpected response status: {response.status_code}')
            else:
                self._logger.info(f'response status: {response.status_code}')
        except Exception as e:
            self._logger.error(str(e))

    def flush(self) -> None:
        self._consumer.flush()

    def shutdown(self) -> None:
        self._consumer.shutdown()

    def _enqueue(self, message: AsyncConsumerMessage) -> None:
        try:
            self._queue.put(message)
        except queue.Full:
            self._logger.error("async queue is full")

    @staticmethod
    def _to_braze_properties(properties: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        if properties is None:
            return None
        return {key: BrazeClient._value_for_api(value) for key, value in properties.items()}

    @staticmethod
    def _value_for_api(value: Any) -> Any:
        # https://www.braze.com/docs/api/objects_filters/user_attributes_object/
        # https://www.braze.com/docs/api/objects_filters/event_object/
        # API doesn't support objects and (non-string) arrays.
        return json.dumps(value) if isinstance(value, (list, dict)) else value
