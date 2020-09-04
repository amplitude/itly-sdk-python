from typing import NamedTuple


class ValidationOptions(NamedTuple):
    disabled: bool = False
    track_invalid: bool = False
    error_on_invalid: bool = False
