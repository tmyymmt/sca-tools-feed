from dataclasses import dataclass, asdict
from typing import Literal

Category = Literal["feature", "pricing", "security", "bugfix", "announcement", "other"]


@dataclass
class ReleaseEntry:
    tool_id: str
    tool_name: str
    version: str
    published_at: str  # ISO 8601 (e.g. "2024-01-15T10:00:00Z")
    url: str
    summary: str
    body: str
    category: Category

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "ReleaseEntry":
        return cls(**d)
