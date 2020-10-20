from typing import Optional

from ._properties import Properties


class Event:
    def __init__(self,
                 name: str,
                 properties: Optional[Properties] = None,
                 id_: Optional[str] = None,
                 version: Optional[str] = None):
        self._name: str = name
        self._properties: Optional[Properties] = properties
        self._id: Optional[str] = id_
        self._version: Optional[str] = version

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
