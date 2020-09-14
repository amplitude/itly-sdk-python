import time
from datetime import timedelta

from itly.sdk.consumers import AsyncConsumer, AsyncConsumerMessage


def test_consumer():
    batches = []

    q = AsyncConsumer.create_queue()
    consumer = AsyncConsumer(
        message_queue=q,
        do_upload=lambda batch: batches.append([msg.data for msg in batch]),
        flush_queue_size=3,
        flush_interval=timedelta(seconds=1)
    )
    try:
        consumer.start()

        q.put(AsyncConsumerMessage(message_type='data', data='1'))
        q.put(AsyncConsumerMessage(message_type='data', data='2'))

        time.sleep(0.1)
        assert batches == []

        q.put(AsyncConsumerMessage(message_type='data', data='3'))
        time.sleep(0.1)

        assert batches == [["1", "2", "3"]]

        q.put(AsyncConsumerMessage(message_type='data', data='4'))

        time.sleep(0.1)
        assert batches == [["1", "2", "3"]]

        consumer.flush()

        time.sleep(0.1)
        assert batches == [["1", "2", "3"], ["4"]]

        consumer.flush()
        consumer.flush()

        q.put(AsyncConsumerMessage(message_type='data', data='5'))
        q.put(AsyncConsumerMessage(message_type='data', data='6'))

        time.sleep(0.1)
        assert batches == [["1", "2", "3"], ["4"]]

        time.sleep(1)
        assert batches == [["1", "2", "3"], ["4"], ["5", "6"]]

        q.put(AsyncConsumerMessage(message_type='message', data='7'))
        q.put(AsyncConsumerMessage(message_type='data', data='8'))

        time.sleep(0.1)
        assert batches == [["1", "2", "3"], ["4"], ["5", "6"], ["7"]]

        consumer.flush()

        time.sleep(0.1)
        assert batches == [["1", "2", "3"], ["4"], ["5", "6"], ["7"], ["8"]]

        q.put(AsyncConsumerMessage(message_type='data', data='9'))
        q.put(AsyncConsumerMessage(message_type='data', data='10'))
    finally:
        consumer.shutdown()

        time.sleep(0.1)
        assert batches == [["1", "2", "3"], ["4"], ["5", "6"], ["7"], ["8"], ["9", "10"]]
