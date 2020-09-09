import atexit
import queue
from datetime import timedelta
from typing import Callable, Optional, NamedTuple, Any, List

import analytics
from analytics.request import post

from itly.sdk import AsyncConsumer, AsyncConsumerMessage


class Request(NamedTuple):
    data: Any


class SegmentClient(analytics.Client):
    def __init__(self, write_key: str, on_error: Callable[[str], None], flush_queue_size: int, flush_interval: timedelta,
                 host: Optional[str], send_request: Optional[Callable[[Request], None]]) -> None:
        super().__init__(write_key=write_key, host=host, send=False, on_error=lambda e, _: on_error(e))
        self._host = host
        self.queue: queue.Queue = AsyncConsumer.create_queue()
        self._send_request: Callable[[Request], None] = send_request if send_request is not None else self._send_request_default
        self.consumer = AsyncConsumer(message_queue=self.queue, do_upload=self._upload_batch, flush_queue_size=flush_queue_size, flush_interval=flush_interval)
        atexit.register(self.shutdown)
        self.consumer.start()

    def _upload_batch(self, batch: List[AsyncConsumerMessage]) -> None:
        try:
            self._send_request(Request(data=[message.data for message in batch]))
        except Exception as e:
            self.on_error(str(e))

    def _send_request_default(self, request: Request) -> None:
        post(self.write_key, self._host, batch=request.data)

    def flush(self) -> None:
        self.consumer.flush()

    def shutdown(self) -> None:
        self.consumer.shutdown()

    def _enqueue(self, msg: Any) -> None:
        _, msg = super()._enqueue(msg)
        try:
            self.queue.put(AsyncConsumerMessage(message_type='', data=msg))
        except queue.Full:
            self.on_error("async queue is full")
