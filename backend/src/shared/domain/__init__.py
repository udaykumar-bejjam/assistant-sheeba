"""Shared domain primitives."""

from src.shared.domain.errors import (
    DomainError,
    UnauthorizedToolError,
    ValidationError,
)
from src.shared.domain.events import DomainEvent
from src.shared.domain.value_objects import (
    CallId,
    CallIntent,
    CallPriority,
    CallStatus,
    ContactId,
    ConversationId,
    EmailAddress,
    Language,
    PhoneNumber,
    TimeRange,
)

__all__ = [
    "CallId",
    "CallIntent",
    "CallPriority",
    "CallStatus",
    "ContactId",
    "ConversationId",
    "DomainError",
    "DomainEvent",
    "EmailAddress",
    "Language",
    "PhoneNumber",
    "TimeRange",
    "UnauthorizedToolError",
    "ValidationError",
]
