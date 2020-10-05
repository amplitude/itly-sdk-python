import random
from typing import Optional, Iterator


def backoff(start: float, stop: float, count: int, factor: float = 2.0, jitter: Optional[float] = 1.0) -> Iterator[float]:
    start = float(start)
    stop = float(stop)
    factor = float(factor)
    if jitter:
        jitter = float(jitter)

    if start < 0:
        start = 0.0
    if stop < start:
        stop = start

    current = start
    for i in range(count):
        yield current - (current * jitter * random.random()) if jitter else current

        if current == 0:
            current = 1
        elif current < stop:
            current *= factor

        if current > stop:
            current = stop
