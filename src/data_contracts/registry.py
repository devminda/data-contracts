from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class SchemaVersion:
    name: str
    version: str
    fields: dict[str, type]
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "version": self.version,
            "fields": {k: v.__name__ for k, v in self.fields.items()},
            "timestamp": self.timestamp.isoformat(),
        }


class SchemaRegistry:
    _store: dict[str, list[SchemaVersion]] = {}

    @classmethod
    def register(cls, version: SchemaVersion) -> None:
        if version.name not in cls._store:
            cls._store[version.name] = []
        cls._store[version.name].append(version)

    @classmethod
    def get_latest(cls, name: str) -> SchemaVersion | None:
        versions = cls._store.get(name, [])
        return versions[-1] if versions else None

    @classmethod
    def get_history(cls, name: str) -> list[SchemaVersion]:
        return cls._store.get(name, [])

    @classmethod
    def list_schemas(cls) -> list[str]:
        return list(cls._store.keys())

    @classmethod
    def clear(cls) -> None:
        cls._store.clear()
