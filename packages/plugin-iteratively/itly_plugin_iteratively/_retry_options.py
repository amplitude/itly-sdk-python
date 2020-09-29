from datetime import timedelta
from typing import NamedTuple


class IterativelyRetryOptions(NamedTuple):
    max_retries: int = 25  # ~1 day
    delay_initial: timedelta = timedelta(seconds=10)
    delay_maximum: timedelta = timedelta(hours=1)
