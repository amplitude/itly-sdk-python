from typing import Optional

from ._properties import Properties


class Event:
    def __init__(self, name: str, properties: Optional[Properties] = None, event_id: Optional[str] = None, version: Optional[str] = None):
        self.name: str = name
        self.properties: Optional[Properties] = properties
        self.id: Optional[str] = event_id
        self.version: Optional[str] = version
