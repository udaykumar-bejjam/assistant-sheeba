"""Call administration and inbound webhook-facing endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field

from src.call_management.application.answer_incoming_call import AnswerIncomingCallCommand
from src.call_management.application.complete_call import CompleteCallCommand
from src.call_management.application.process_caller_message import ProcessCallerMessageCommand
from src.infrastructure.container import AppContainer
from src.interfaces.api.deps import get_container
from src.shared.domain.errors import CallNotFoundError, DomainError, ValidationError
from src.shared.domain.value_objects import CallId

router = APIRouter()


class InboundCallRequest(BaseModel):
    provider_call_id: str = Field(min_length=1)
    from_number: str = Field(min_length=3)
    to_number: str = ""


class CallerMessageRequest(BaseModel):
    text: str = Field(min_length=1)


class CompleteCallRequest(BaseModel):
    summary_text: str = Field(min_length=1)
    requested_action: str | None = None
    failed: bool = False


def _container(request: Request) -> AppContainer:
    return get_container(request)


@router.post("/inbound")
async def inbound_call(
    body: InboundCallRequest,
    container: AppContainer = Depends(_container),
) -> dict[str, object]:
    try:
        result = await container.answer_incoming_call.execute(
            AnswerIncomingCallCommand(
                provider_call_id=body.provider_call_id,
                from_number=body.from_number,
                to_number=body.to_number,
            )
        )
    except ValidationError as exc:
        raise HTTPException(status_code=422, detail=exc.message) from exc
    except DomainError as exc:
        raise HTTPException(status_code=400, detail=exc.message) from exc
    return {
        "call_id": result.call_id,
        "conversation_id": result.conversation_id,
        "greeting": result.greeting,
        "caller_known": result.caller_known,
        "caller_name": result.caller_name,
    }


@router.get("")
async def list_calls(container: AppContainer = Depends(_container)) -> dict[str, object]:
    calls = await container.calls.list_recent(limit=100)
    return {
        "items": [
            {
                "id": str(c.id),
                "status": c.status.value,
                "phone": str(c.caller_phone),
                "caller_name": c.caller_name,
                "intent": c.classification.intent.value,
                "priority": c.classification.priority.value,
                "created_at": c.created_at.isoformat(),
                "duration_seconds": c.duration_seconds,
            }
            for c in calls
        ]
    }


@router.get("/{call_id}")
async def get_call(
    call_id: str,
    container: AppContainer = Depends(_container),
) -> dict[str, object]:
    call = await container.calls.get(CallId(call_id))
    if call is None:
        raise HTTPException(status_code=404, detail="Call not found")
    return {
        "id": str(call.id),
        "status": call.status.value,
        "phone": str(call.caller_phone),
        "caller_name": call.caller_name,
        "intent": call.classification.intent.value,
        "priority": call.classification.priority.value,
        "summary": call.summary.to_dict() if call.summary else None,
        "transcript": call.transcript,
        "outcome": {
            "message_taken": call.outcome.message_taken,
            "message_text": call.outcome.message_text,
            "callback_requested": call.outcome.callback_requested,
            "transferred": call.outcome.transferred,
        },
        "created_at": call.created_at.isoformat(),
        "duration_seconds": call.duration_seconds,
    }


@router.post("/{call_id}/messages")
async def post_caller_message(
    call_id: str,
    body: CallerMessageRequest,
    container: AppContainer = Depends(_container),
) -> dict[str, object]:
    try:
        result = await container.process_caller_message.execute(
            ProcessCallerMessageCommand(call_id=call_id, text=body.text)
        )
    except CallNotFoundError as exc:
        raise HTTPException(status_code=404, detail=exc.message) from exc
    except DomainError as exc:
        raise HTTPException(status_code=400, detail=exc.message) from exc
    return {
        "reply": result.reply,
        "tools_executed": result.tools_executed,
        "denied_tools": result.denied_tools,
    }


@router.post("/{call_id}/complete")
async def complete_call(
    call_id: str,
    body: CompleteCallRequest,
    container: AppContainer = Depends(_container),
) -> dict[str, object]:
    try:
        result = await container.complete_call.execute(
            CompleteCallCommand(
                call_id=call_id,
                summary_text=body.summary_text,
                requested_action=body.requested_action,
                failed=body.failed,
            )
        )
    except CallNotFoundError as exc:
        raise HTTPException(status_code=404, detail=exc.message) from exc
    except DomainError as exc:
        raise HTTPException(status_code=400, detail=exc.message) from exc
    return {
        "call_id": result.call_id,
        "status": result.status,
        "summary": result.summary,
        "notified": result.notified,
    }
