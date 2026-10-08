"""Use case: complete call, attach structured summary, notify if needed."""

from __future__ import annotations

from dataclasses import dataclass

from src.call_management.domain.call import CallSummary
from src.call_management.domain.repository import CallRepository
from src.shared.application.ports import EventBus, NotificationMessage, NotificationProvider
from src.shared.domain.errors import CallNotFoundError
from src.shared.domain.value_objects import CallId, CallPriority
from src.shared.infrastructure.logging import get_logger

logger = get_logger(__name__)


@dataclass(frozen=True, slots=True)
class CompleteCallCommand:
    call_id: str
    summary_text: str
    requested_action: str | None = None
    failed: bool = False


@dataclass(frozen=True, slots=True)
class CompleteCallResult:
    call_id: str
    status: str
    summary: dict[str, object]
    notified: bool


class CompleteCallService:
    def __init__(
        self,
        *,
        calls: CallRepository,
        events: EventBus,
        notifications: NotificationProvider | None = None,
    ) -> None:
        self._calls = calls
        self._events = events
        self._notifications = notifications

    async def execute(self, command: CompleteCallCommand) -> CompleteCallResult:
        call = await self._calls.get(CallId(command.call_id))
        if call is None:
            raise CallNotFoundError(f"Call not found: {command.call_id}")

        if call.status.value not in {"COMPLETED", "FAILED", "TRANSFERRED", "MISSED", "ABANDONED"}:
            call.complete(failed=command.failed)

        summary = CallSummary(
            caller_name=call.caller_name,
            phone_number=str(call.caller_phone),
            intent=call.classification.intent,
            priority=call.classification.priority,
            summary=command.summary_text.strip(),
            requested_action=command.requested_action,
            callback_requested=call.outcome.callback_requested,
            appointment_requested=call.outcome.appointment_requested,
            transferred=call.outcome.transferred,
            follow_up_required=call.outcome.follow_up_required
            or call.outcome.message_taken
            or call.outcome.callback_requested,
        )
        call.attach_summary(summary)
        await self._calls.save(call)
        await self._events.publish(call.collect_events())

        notified = False
        should_notify = (
            summary.follow_up_required
            or summary.priority in {CallPriority.HIGH, CallPriority.URGENT}
            or summary.callback_requested
            or summary.transferred
        )
        if should_notify and self._notifications is not None:
            body = self._format_notification(summary)
            await self._notifications.send(
                NotificationMessage(
                    subject="AI CALL SUMMARY",
                    body=body,
                    channel=self._notifications.channel,
                    metadata={"call_id": str(call.id)},
                )
            )
            notified = True

        logger.info(
            "call_completed",
            call_id=str(call.id),
            status=call.status.value,
            notified=notified,
        )
        return CompleteCallResult(
            call_id=str(call.id),
            status=call.status.value,
            summary=summary.to_dict(),
            notified=notified,
        )

    @staticmethod
    def _format_notification(summary: CallSummary) -> str:
        name = summary.caller_name or "Unknown"
        return (
            "AI CALL SUMMARY\n\n"
            f"Caller: {name}\n"
            f"Phone: {summary.phone_number}\n\n"
            f"Intent: {summary.intent.value.replace('_', ' ').title()}\n\n"
            f"Summary: {summary.summary}\n\n"
            f"Requested action: {summary.requested_action or 'None'}\n\n"
            f"Priority: {summary.priority.value}"
        )
