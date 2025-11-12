from __future__ import annotations
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import ClassVar, Dict

# Unique ID Generator

class IDGenerator:
    """Global incremental ID generator (resets each runtime)."""

    _counter: ClassVar[int] = 0

    @classmethod
    def get(cls, prefix: str = "id") -> str:
        """Generate new unique ID."""
        cls._counter += 1
        return f"{prefix}_{cls._counter:04d}"


# Base Entity Class


@dataclass
class BaseEntity:
    """Base class for all data entities with ID and timestamps."""

    id: str
    created_at: str
    updated_at: str

    def __init__(self, prefix: str = "entity"):
        self.id = IDGenerator.get(prefix)
        now = datetime.now().isoformat()
        self.created_at = now
        self.updated_at = now

    # Utility Methods


    def update_timestamp(self) -> None:
        """Refresh update timestamp."""
        self.updated_at = datetime.now().isoformat()

    def to_dict(self) -> Dict:
        """Convert dataclass to dictionary (safe for JSON)."""
        base = asdict(self) if hasattr(self, "__dataclass_fields__") else {}
        base.update({
            "id": self.id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        })
        return base

    @classmethod
    def from_dict(cls, data: Dict) -> "BaseEntity":
        """Recreate object from dictionary."""
        obj = cls(prefix=data.get("id", "entity"))
        obj.id = data.get("id", obj.id)
        obj.created_at = data.get("created_at", datetime.now().isoformat())
        obj.updated_at = data.get("updated_at", datetime.now().isoformat())
        return obj