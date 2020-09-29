from typing import NamedTuple


class ValidationResponse(NamedTuple):
    valid: bool
    plugin_id: str
    message: str
