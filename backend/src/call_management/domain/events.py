"""Call management domain events."""

from __future__ import annotations

from dataclasses import dataclass

from src.shared.domain.events import DomainEvent
from src.shared.domain.value_objects import CallIntent, CallPriority


@dataclass(frozen=True, kw_only=True, slots=True)
class CallReceived(DomainEvent):
    phone_number: str = ""
    provider_call_id: str = ""


@dataclass(frozen=True, kw_only=True, slots=True)
class CallAnswered(DomainEvent):
    pass


@dataclass(frozen=True, kw_only=True, slots=True)
class CallStarted(DomainEvent):
    conversation_id: str = ""


@dataclass(frozen=True, kw_only=True, slots=True)
class CallCompleted(DomainEvent):
    duration_seconds: int = 0


@dataclass(frozen=True, kw_only=True, slots=True)
class CallTransferred(DomainEvent):
    destination: str = ""


@dataclass(frozen=True, kw_only=True, slots=True)
class CallClassified(DomainEvent):
    intent: CallIntent = CallIntent.UNKNOWN
    priority: CallPriority = CallPriority.MEDIUM


@dataclass(frozen=True, kw_only=True, slots=True)
class MessageTaken(DomainEvent):
    message_preview: str = ""


@dataclass(frozen=True, kw_only=True, slots=True)
class CallSummaryGenerated(DomainEvent):
    priority: CallPriority = CallPriority.MEDIUM
    intent: CallIntent = CallIntent.UNKNOWN


@dataclass(frozen=True, kw_only=True, slots=True)
class CallbackRequested(DomainEvent):
    preferred_time_note: str = ""


@dataclass(frozen=True, kw_only=True, slots=True)
class ImportantCallDetected(DomainEvent):
    reason: str = ""
