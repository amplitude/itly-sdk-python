import atexit
import queue
from datetime import timedelta
from typing import Callable, Optional, NamedTuple, Any, List

import analytics
from analytics.request import post

from itly.sdk import AsyncConsumer, AsyncConsumerMessage

Request = NamedTuple('Request', [('data', Any)])


class SegmentClient(analytics.Client):
    def __init__(self, write_key, on_error, upload_size, upload_interval, host, send_request):
        # type: (str, Callable[[str], None], int, timedelta, Optional[str], Optional[Callable[[Request], None]]) -> None
        super(SegmentClient, self).__init__(write_key=write_key, host=host, send=False, on_error=lambda e, _: on_error(e))
        self._host = host
        self.queue = AsyncConsumer.create_queue()  # type: queue.Queue
        self._send_request = send_request if send_request is not None else self._send_request_default  # type: Callable[[Request], None]
        self.consumer = AsyncConsumer(message_queue=self.queue, do_upload=self._upload_batch, upload_size=upload_size, upload_interval=upload_interval)
        atexit.register(self.shutdown)
        self.consumer.start()

    def _upload_batch(self, batch):
        # type: (List[AsyncConsumerMessage]) -> None
        try:
            self._send_request(Request(data=[message.data for message in batch]))
        except Exception as e:
            self.on_error(str(e))

    def _send_request_default(self, request):
        # type: (Request) -> None
        post(self.write_key, self._host, batch=request.data)

    def flush(self):
        # type: () -> None
        self.consumer.flush()

    def shutdown(self):
        # type: () -> None
        self.consumer.shutdown()

    def _enqueue(self, msg):
        # type: (Any) -> None
        _, msg = super(SegmentClient, self)._enqueue(msg)
        try:
            self.queue.put(AsyncConsumerMessage(message_type='', data=msg))
        except queue.Full:
            self.on_error("async queue is full")
