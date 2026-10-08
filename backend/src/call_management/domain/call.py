"""Call aggregate root."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from src.call_management.domain.events import (
    CallAnswered,
    CallClassified,
    CallCompleted,
    CallReceived,
    CallStarted,
    CallSummaryGenerated,
    CallTransferred,
    MessageTaken,
)
from src.shared.domain.errors import InvalidStateTransitionError, ValidationError
from src.shared.domain.events import DomainEvent
from src.shared.domain.value_objects import (
    TERMINAL_CALL_STATUSES,
    CallId,
    CallIntent,
    CallPriority,
    CallStatus,
    ContactId,
    ConversationId,
    Language,
    PhoneNumber,
)

_ALLOWED: dict[CallStatus, frozenset[CallStatus]] = {
    CallStatus.RINGING: frozenset(
        {
            CallStatus.CONNECTED,
            CallStatus.MISSED,
            CallStatus.ABANDONED,
            CallStatus.FAILED,
        }
    ),
    CallStatus.CONNECTED: frozenset(
        {
            CallStatus.IN_PROGRESS,
            CallStatus.FAILED,
            CallStatus.ABANDONED,
        }
    ),
    CallStatus.IN_PROGRESS: frozenset(
        {
            CallStatus.TRANSFERRED,
            CallStatus.COMPLETED,
            CallStatus.FAILED,
            CallStatus.ABANDONED,
        }
    ),
    CallStatus.TRANSFERRED: frozenset({CallStatus.COMPLETED, CallStatus.FAILED}),
}


@dataclass(slots=True)
class CallClassification:
    intent: CallIntent = CallIntent.UNKNOWN
    priority: CallPriority = CallPriority.MEDIUM
    spam_score: float = 0.0
    reasons: list[str] = field(default_factory=list)


@dataclass(slots=True)
class CallOutcome:
    message_taken: bool = False
    message_text: str | None = None
    callback_requested: bool = False
    callback_note: str | None = None
    appointment_requested: bool = False
    transferred: bool = False
    transfer_destination: str | None = None
    follow_up_required: bool = False


@dataclass(slots=True)
class CallSummary:
    caller_name: str | None = None
    phone_number: str = ""
    intent: CallIntent = CallIntent.UNKNOWN
    priority: CallPriority = CallPriority.MEDIUM
    summary: str = ""
    requested_action: str | None = None
    callback_requested: bool = False
    appointment_requested: bool = False
    transferred: bool = False
    follow_up_required: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "caller_name": self.caller_name,
            "phone_number": self.phone_number,
            "intent": self.intent.value,
            "priority": self.priority.value,
            "summary": self.summary,
            "requested_action": self.requested_action,
            "callback_requested": self.callback_requested,
            "appointment_requested": self.appointment_requested,
            "transferred": self.transferred,
            "follow_up_required": self.follow_up_required,
        }


@dataclass(slots=True)
class Call:
    """Aggregate root for an inbound/outbound call session."""

    id: CallId
    caller_phone: PhoneNumber
    status: CallStatus
    provider_call_id: str
    created_at: datetime
    updated_at: datetime
    contact_id: ContactId | None = None
    caller_name: str | None = None
    conversation_id: ConversationId | None = None
    language: Language = Language.AUTO
    classification: CallClassification = field(default_factory=CallClassification)
    outcome: CallOutcome = field(default_factory=CallOutcome)
    summary: CallSummary | None = None
    transcript: str | None = None
    answered_at: datetime | None = None
    ended_at: datetime | None = None
    _events: list[DomainEvent] = field(default_factory=list, repr=False)

    @classmethod
    def receive(
        cls,
        *,
        caller_phone: PhoneNumber,
        provider_call_id: str,
        call_id: CallId | None = None,
    ) -> Call:
        if not provider_call_id.strip():
            raise ValidationError("provider_call_id is required")
        now = datetime.now(UTC)
        cid = call_id or CallId.generate()
        call = cls(
            id=cid,
            caller_phone=caller_phone,
            status=CallStatus.RINGING,
            provider_call_id=provider_call_id.strip(),
            created_at=now,
            updated_at=now,
        )
        call._record(
            CallReceived(
                aggregate_id=str(cid),
                phone_number=str(caller_phone),
                provider_call_id=provider_call_id.strip(),
            )
        )
        return call

    def answer(self) -> None:
        self._transition(CallStatus.CONNECTED)
        self.answered_at = datetime.now(UTC)
        self._record(CallAnswered(aggregate_id=str(self.id)))

    def start_conversation(self, conversation_id: ConversationId) -> None:
        self._transition(CallStatus.IN_PROGRESS)
        self.conversation_id = conversation_id
        self._record(
            CallStarted(aggregate_id=str(self.id), conversation_id=str(conversation_id))
        )

    def identify_caller(self, *, contact_id: ContactId, name: str | None) -> None:
        self.contact_id = contact_id
        if name:
            self.caller_name = name

    def classify(self, classification: CallClassification) -> None:
        self._ensure_active()
        if classification.spam_score < 0 or classification.spam_score > 1:
            raise ValidationError("spam_score must be between 0 and 1")
        self.classification = classification
        self.updated_at = datetime.now(UTC)
        self._record(
            CallClassified(
                aggregate_id=str(self.id),
                intent=classification.intent,
                priority=classification.priority,
            )
        )

    def take_message(self, message: str) -> None:
        self._ensure_active()
        text = message.strip()
        if not text:
            raise ValidationError("Message cannot be empty")
        self.outcome.message_taken = True
        self.outcome.message_text = text
        self.outcome.follow_up_required = True
        self.updated_at = datetime.now(UTC)
        preview = text if len(text) <= 120 else text[:117] + "..."
        self._record(MessageTaken(aggregate_id=str(self.id), message_preview=preview))

    def request_callback(self, note: str) -> None:
        self._ensure_active()
        self.outcome.callback_requested = True
        self.outcome.callback_note = note.strip() or None
        self.outcome.follow_up_required = True
        self.updated_at = datetime.now(UTC)

    def mark_transferred(self, destination: str) -> None:
        dest = destination.strip()
        if not dest:
            raise ValidationError("Transfer destination is required")
        self._transition(CallStatus.TRANSFERRED)
        self.outcome.transferred = True
        self.outcome.transfer_destination = dest
        self._record(CallTransferred(aggregate_id=str(self.id), destination=dest))

    def complete(self, *, failed: bool = False) -> None:
        if self.status in TERMINAL_CALL_STATUSES and self.status != CallStatus.TRANSFERRED:
            raise InvalidStateTransitionError(
                f"Call {self.id} already terminal: {self.status}"
            )
        target = CallStatus.FAILED if failed else CallStatus.COMPLETED
        if self.status == CallStatus.TRANSFERRED:
            # Allow transferred → completed/failed
            self.status = target
        else:
            self._transition(target)
        self.ended_at = datetime.now(UTC)
        self.updated_at = self.ended_at
        self._record(
            CallCompleted(
                aggregate_id=str(self.id),
                duration_seconds=self.duration_seconds,
            )
        )

    def attach_summary(self, summary: CallSummary) -> None:
        if self.status not in {
            CallStatus.COMPLETED,
            CallStatus.TRANSFERRED,
            CallStatus.FAILED,
        }:
            raise InvalidStateTransitionError("Summary only after call end path")
        summary.phone_number = str(self.caller_phone)
        if summary.caller_name is None:
            summary.caller_name = self.caller_name
        summary.intent = self.classification.intent
        summary.priority = self.classification.priority
        summary.callback_requested = self.outcome.callback_requested
        summary.appointment_requested = self.outcome.appointment_requested
        summary.transferred = self.outcome.transferred
        summary.follow_up_required = self.outcome.follow_up_required
        self.summary = summary
        self.updated_at = datetime.now(UTC)
        self._record(
            CallSummaryGenerated(
                aggregate_id=str(self.id),
                priority=summary.priority,
                intent=summary.intent,
            )
        )

    def attach_transcript(self, transcript: str) -> None:
        self.transcript = transcript
        self.updated_at = datetime.now(UTC)

    @property
    def duration_seconds(self) -> int:
        if self.answered_at is None:
            return 0
        end = self.ended_at or datetime.now(UTC)
        return max(0, int((end - self.answered_at).total_seconds()))

    def collect_events(self) -> list[DomainEvent]:
        events = list(self._events)
        self._events.clear()
        return events

    def _ensure_active(self) -> None:
        if self.status not in {CallStatus.CONNECTED, CallStatus.IN_PROGRESS}:
            raise InvalidStateTransitionError(
                f"Call {self.id} is not active (status={self.status})"
            )

    def _transition(self, new_status: CallStatus) -> None:
        if self.status in TERMINAL_CALL_STATUSES and self.status != CallStatus.TRANSFERRED:
            raise InvalidStateTransitionError(
                f"Cannot transition from terminal status {self.status} to {new_status}"
            )
        allowed = _ALLOWED.get(self.status, frozenset())
        if new_status not in allowed:
            raise InvalidStateTransitionError(
                f"Invalid call transition {self.status} → {new_status}"
            )
        self.status = new_status
        self.updated_at = datetime.now(UTC)

    def _record(self, event: DomainEvent) -> None:
        self._events.append(event)
