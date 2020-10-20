import queue
from datetime import datetime, timedelta
from threading import Thread, Event
from typing import Optional, Callable, List, Tuple, NamedTuple, Any


class AsyncConsumerMessage(NamedTuple):
    message_type: str
    data: Any


class AsyncConsumer(Thread):
    @staticmethod
    def create_queue() -> queue.Queue:
        return queue.Queue(maxsize=10000)

    def __init__(self,
                 message_queue: queue.Queue,
                 do_upload: Callable[[List[AsyncConsumerMessage]], None],
                 flush_queue_size: int,
                 flush_interval: timedelta) -> None:
        """Create a consumer thread."""
        Thread.__init__(self)
        # Make consumer a daemon thread so that it doesn't block program exit
        self._daemon = True
        self._do_upload = do_upload
        self._upload_size = flush_queue_size
        self._flush_interval = flush_interval
        self._queue = message_queue
        self._pending_message: Optional[AsyncConsumerMessage] = None
        self._running = True

    def run(self) -> None:
        while self._running:
            self.upload()

    def pause(self) -> None:
        self._running = False

    def upload(self) -> None:
        batch, event = self.next()
        if len(batch) == 0:
            if event is not None:
                event.set()
            return

        try:
            self._do_upload(batch)
        except Exception:
            pass
        finally:
            if event is not None:
                event.set()
            # mark items as acknowledged from queue
            for _ in batch:
                self._queue.task_done()

    def next(self) -> Tuple[List[AsyncConsumerMessage], Optional[Event]]:
        start = datetime.now()
        items: List[AsyncConsumerMessage] = [self._pending_message] if self._pending_message is not None else []
        self._pending_message = None

        now = datetime.now()
        while len(items) < self._upload_size and now - start < self._flush_interval:
            try:
                timeout = (self._flush_interval - (now - start)).total_seconds()
                item = self._queue.get(block=True, timeout=timeout)
                if isinstance(item.data, Event):
                    return items, item.data
                if len(items) > 0 and items[-1].message_type != item.message_type:
                    self._pending_message = item
                    break
                items.append(item)
                now = datetime.now()
            except queue.Empty:
                break

        return items, None

    def flush(self) -> None:
        event = Event()
        self._queue.put(AsyncConsumerMessage(message_type='flush', data=event))
        event.wait()

    def shutdown(self) -> None:
        self.pause()
        try:
            self.join()
        except RuntimeError:
            # consumer thread has not started
            pass
