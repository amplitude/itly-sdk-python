import enum
from typing import Optional, Any, Dict


class Event:
    def __init__(self, name: str, properties: Optional[Dict[str, Any]] = None, id: Optional[str] = None, version: Optional[str] = None):
        self._name: str = name
        self._properties: Optional[Dict[str, Any]] = None if properties is None \
            else {
            key: value.value if isinstance(value, enum.Enum) else value
            for key, value in properties.items()
            if value is not None
        }
        self._id: Optional[str] = id
        self._version: Optional[str] = version

    @property
    def name(self) -> str:
        return self._name

    @property
    def properties(self) -> Optional[Dict[str, Any]]:
        return self._properties

    @property
    def id(self) -> Optional[str]:
        return self._id

    @property
    def version(self) -> Optional[str]:
        return self._version
