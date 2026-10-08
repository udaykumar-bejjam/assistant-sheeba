"""Call aggregate invariant tests."""

from __future__ import annotations

import pytest
from src.call_management.domain.call import Call, CallClassification, CallSummary
from src.shared.domain.errors import InvalidStateTransitionError, ValidationError
from src.shared.domain.value_objects import (
    CallIntent,
    CallPriority,
    CallStatus,
    ConversationId,
    PhoneNumber,
)


def test_receive_starts_ringing() -> None:
    call = Call.receive(caller_phone=PhoneNumber("+14155552671"), provider_call_id="twilio-1")
    assert call.status == CallStatus.RINGING
    events = call.collect_events()
    assert any(e.event_type == "CallReceived" for e in events)


def test_happy_path_to_completed() -> None:
    call = Call.receive(caller_phone=PhoneNumber("+14155552671"), provider_call_id="p1")
    call.answer()
    call.start_conversation(ConversationId.generate())
    call.classify(
        CallClassification(intent=CallIntent.BUSINESS, priority=CallPriority.MEDIUM)
    )
    call.take_message("Please call back about the project")
    call.complete()
    assert call.status == CallStatus.COMPLETED
    call.attach_summary(CallSummary(summary="Business enquiry about project"))
    assert call.summary is not None
    assert call.summary.callback_requested is False
    assert call.summary.follow_up_required is True


def test_cannot_reopen_completed_call() -> None:
    call = Call.receive(caller_phone=PhoneNumber("+14155552671"), provider_call_id="p2")
    call.answer()
    call.start_conversation(ConversationId.generate())
    call.complete()
    with pytest.raises(InvalidStateTransitionError):
        call.start_conversation(ConversationId.generate())


def test_empty_message_rejected() -> None:
    call = Call.receive(caller_phone=PhoneNumber("+14155552671"), provider_call_id="p3")
    call.answer()
    call.start_conversation(ConversationId.generate())
    with pytest.raises(ValidationError):
        call.take_message("   ")


def test_transfer_then_complete() -> None:
    call = Call.receive(caller_phone=PhoneNumber("+14155552671"), provider_call_id="p4")
    call.answer()
    call.start_conversation(ConversationId.generate())
    call.mark_transferred("+919999999999")
    assert call.status == CallStatus.TRANSFERRED
    call.complete()
    assert call.status == CallStatus.COMPLETED
