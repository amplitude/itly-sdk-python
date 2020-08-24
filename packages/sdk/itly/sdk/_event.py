from typing import Optional

from ._properties import Properties


class Event:
    def __init__(self, name, properties=None, event_id=None, version=None):
        # type: (str, Optional[Properties], Optional[str], Optional[str]) -> None
        self.name = name  # type: str
        self.properties = properties  # type: Optional[Properties]
        self.id = event_id  # type: Optional[str]
        self.version = version  # type: Optional[str]
