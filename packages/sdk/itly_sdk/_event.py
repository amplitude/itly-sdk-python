from abc import ABC
from typing import Optional, Dict

from ._properties import Properties


class EventMetadata(ABC):
    pass


class Event:
    def __init__(self,
                 name: str,
                 properties: Optional[Properties] = None,
                 id_: Optional[str] = None,
                 version: Optional[str] = None,
                 metadata: Optional[Dict[str, EventMetadata]] = None):
        self._name: str = name
        self._properties: Optional[Properties] = properties
        self._id: Optional[str] = id_
        self._version: Optional[str] = version
        self._metadata: Dict[str, EventMetadata] = metadata if metadata is not None else {}

    @property
    def name(self) -> str:
        return self._name

    @property
    def properties(self) -> Optional[Properties]:
        return self._properties

    @property
    def id(self) -> Optional[str]:
        return self._id

    @property
    def version(self) -> Optional[str]:
        return self._version

    @property
    def metadata(self) -> Dict[str, EventMetadata]:
        return self._metadata
