"""Domain event base type."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4


@dataclass(frozen=True, kw_only=True, slots=True)
class DomainEvent:
    """Immutable domain event. Handlers live outside the domain."""

    event_id: str = field(default_factory=lambda: str(uuid4()))
    occurred_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    aggregate_id: str = ""
    event_type: str = ""

    def __post_init__(self) -> None:
        if not self.event_type:
            object.__setattr__(self, "event_type", type(self).__name__)

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "aggregate_id": self.aggregate_id,
            "occurred_at": self.occurred_at.isoformat(),
        }
