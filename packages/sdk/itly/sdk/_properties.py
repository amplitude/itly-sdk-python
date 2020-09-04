import enum
import json
from typing import Any, Dict, List, Optional


class Properties:
    def __init__(self, **kwargs: Any):
        self._properties = dict(**kwargs)

    def to_json(self) -> Dict[str, Any]:
        return {
            key: value.value if isinstance(value, enum.Enum) else value
            for (key, value)
            in self._properties.items()
        }

    def __str__(self) -> str:
        return json.dumps(self.to_json())

    def __len__(self) -> int:
        return len(self._properties)

    def __contains__(self, item: str) -> bool:
        return item in self._properties

    @staticmethod
    def concat(properties: List[Optional["Properties"]]) -> "Properties":
        result: Dict[str, Any] = {}
        for p in properties:
            if p is not None:
                result.update(p._properties)
        return Properties(**result)
