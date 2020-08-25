from collections import namedtuple
from threading import Thread
from typing import Optional, Callable, List
import queue

AsyncConsumerMessage = namedtuple("AsyncConsumerMessage", ["message_type", "data"])


class AsyncConsumer(Thread):
    def __init__(self, queue, do_request, on_error, upload_size=10):
        # type: (queue.Queue, Callable[[List[AsyncConsumerMessage]], None], Callable[[str], None], int) -> None
        """Create a consumer thread."""
        Thread.__init__(self)
        # Make consumer a daemon thread so that it doesn't block program exit
        self._daemon = True
        self._do_request = do_request
        self._upload_size = upload_size
        self._on_error = on_error
        self._queue = queue
        self._pending_message = None  # type:  Optional[AsyncConsumerMessage]
        self._running = True

    def run(self):
        # type: () -> None
        while self._running:
            self.upload()

    def pause(self):
        # type: () -> None
        self._running = False

    def upload(self):
        # type: () -> None
        batch = self.next()
        if len(batch) == 0:
            return

        try:
            self._do_request(batch)
        except Exception as e:
            self._on_error(str(e))
        finally:
            # mark items as acknowledged from queue
            for _ in batch:
                self._queue.task_done()

    def next(self):
        # type: () -> List[AsyncConsumerMessage]
        items = [self._pending_message] if self._pending_message is not None else []  # type: List[AsyncConsumerMessage]
        self._pending_message = None

        while len(items) < self._upload_size:
            try:
                item = self._queue.get(block=True, timeout=1)
                if len(items) > 0 and items[-1].message_type != item.message_type:
                    self._pending_message = item
                    break
                items.append(item)
            except queue.Empty:
                break

        return items
