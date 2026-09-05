"""Versioned event contract shared by agents and consumers."""

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Any, Mapping
import json

SCHEMA_VERSION = "1.0"


@dataclass(frozen=True)
class SecurityEvent:
    event: str
    timestamp: str
    source_ip: str
    username: str
    host: str
    schema_version: str = SCHEMA_VERSION

    def __post_init__(self) -> None:
        datetime.fromisoformat(self.timestamp.replace("Z", "+00:00"))
        if not self.event or not self.source_ip or not self.host:
            raise ValueError("event, source_ip, and host are required")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True)

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "SecurityEvent":
        required = {"event", "timestamp", "source_ip", "username", "host"}
        missing = required - value.keys()
        if missing:
            raise ValueError(f"missing event fields: {', '.join(sorted(missing))}")
        return cls(**{key: value[key] for key in required},
                   schema_version=value.get("schema_version", SCHEMA_VERSION))


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
