"""Use case: process a caller utterance through Sheeba + tools/policy."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.ai_agent.domain.policy import PolicyContext, PolicyEvaluator, ToolAction
from src.ai_agent.domain.tools import ToolName
from src.assistant.domain.repository import AssistantProfileRepository
from src.call_management.domain.repository import CallRepository
from src.contacts.domain.repository import ContactRepository
from src.shared.application.ports import AIConversationProvider, EventBus
from src.shared.domain.errors import CallNotFoundError, UnauthorizedToolError
from src.shared.domain.value_objects import CallId
from src.shared.infrastructure.logging import get_logger

logger = get_logger(__name__)


@dataclass(frozen=True, slots=True)
class ProcessCallerMessageCommand:
    call_id: str
    text: str


@dataclass(frozen=True, slots=True)
class ProcessCallerMessageResult:
    reply: str
    tools_executed: list[str]
    denied_tools: list[str]


class ProcessCallerMessageService:
    def __init__(
        self,
        *,
        calls: CallRepository,
        contacts: ContactRepository,
        profiles: AssistantProfileRepository,
        ai: AIConversationProvider,
        policy: PolicyEvaluator,
        events: EventBus,
        tool_executor: ToolExecutor,
    ) -> None:
        self._calls = calls
        self._contacts = contacts
        self._profiles = profiles
        self._ai = ai
        self._policy = policy
        self._events = events
        self._tools = tool_executor

    async def execute(self, command: ProcessCallerMessageCommand) -> ProcessCallerMessageResult:
        call = await self._calls.get(CallId(command.call_id))
        if call is None:
            raise CallNotFoundError(f"Call not found: {command.call_id}")
        if call.conversation_id is None:
            raise CallNotFoundError(f"Call has no conversation: {command.call_id}")

        profile = await self._profiles.get("default")
        if profile is None:
            from src.assistant.domain.profile import AssistantProfile

            profile = AssistantProfile.default()

        contact = None
        if call.contact_id is not None:
            contact = await self._contacts.get(call.contact_id)

        # Prompt-injection: refuse impersonation attempts with fixed identity reply.
        if self._policy.detect_injection(command.text):
            reply = self._policy.refuse_impersonation_response(profile)
            logger.info(
                "injection_refused",
                call_id=str(call.id),
            )
            return ProcessCallerMessageResult(reply=reply, tools_executed=[], denied_tools=[])

        session_id = str(call.conversation_id)
        ai_reply = await self._ai.send_user_message(session_id=session_id, content=command.text)

        executed: list[str] = []
        denied: list[str] = []
        ctx = PolicyContext(
            profile=profile,
            contact=contact,
            call_priority=call.classification.priority,
            latest_caller_utterance=command.text,
        )

        for raw in ai_reply.tool_calls:
            name = raw.get("name")
            args = raw.get("arguments") or {}
            if name is None:
                continue
            try:
                tool = ToolName(name)
            except ValueError:
                denied.append(str(name))
                continue

            ctx.caller_confirmed = bool(args.get("caller_confirmed", False))
            decision = self._policy.evaluate(tool, ctx, args)
            if decision.action == ToolAction.DENY:
                denied.append(tool.value)
                logger.info("tool_denied", tool=tool.value, reason=decision.reason)
                continue
            if decision.action == ToolAction.REQUIRE_CONFIRMATION:
                denied.append(tool.value)
                continue

            await self._tools.execute(tool, call_id=str(call.id), args=args)
            executed.append(tool.value)

        # Reload call after tool side-effects
        call = await self._calls.get(CallId(command.call_id))
        assert call is not None
        await self._events.publish(call.collect_events())

        reply = ai_reply.text.strip() or profile.identity.greeting
        return ProcessCallerMessageResult(
            reply=reply,
            tools_executed=executed,
            denied_tools=denied,
        )


class ToolExecutor:
    """Application-level tool execution (no arbitrary code)."""

    def __init__(
        self,
        *,
        calls: CallRepository,
        events: EventBus,
    ) -> None:
        self._calls = calls
        self._events = events

    async def execute(
        self, tool: ToolName, *, call_id: str, args: dict[str, Any]
    ) -> dict[str, Any]:
        call = await self._calls.get(CallId(call_id))
        if call is None:
            raise CallNotFoundError(call_id)

        if tool == ToolName.TAKE_MESSAGE:
            message = str(args.get("message", "")).strip()
            call.take_message(message)
            await self._calls.save(call)
            return {"ok": True}

        if tool == ToolName.REQUEST_CALLBACK:
            note = str(args.get("note", "")).strip()
            preferred = str(args.get("preferred_time", "")).strip()
            combined = note if not preferred else f"{note} (preferred: {preferred})"
            call.request_callback(combined)
            await self._calls.save(call)
            return {"ok": True}

        if tool == ToolName.END_CALL:
            call.complete()
            await self._calls.save(call)
            return {"ok": True}

        if tool == ToolName.TRANSFER_CALL:
            # Actual telephony transfer is orchestrated elsewhere; mark intent.
            dest = "owner"
            call.mark_transferred(dest)
            await self._calls.save(call)
            return {"ok": True, "destination": dest}

        if tool in {
            ToolName.SEARCH_KNOWLEDGE,
            ToolName.GET_CONTACT,
            ToolName.SEARCH_CONTACTS,
            ToolName.GET_OWNER_AVAILABILITY,
        }:
            # Read tools stubbed until knowledge/calendar adapters wired.
            return {"ok": True, "results": []}

        if tool == ToolName.CREATE_CALENDAR_EVENT:
            call.outcome.appointment_requested = True
            call.outcome.follow_up_required = True
            await self._calls.save(call)
            return {"ok": True, "pending_confirmation": False}

        if tool == ToolName.SEND_NOTIFICATION:
            return {"ok": True, "queued": True}

        raise UnauthorizedToolError(f"Tool not executable: {tool}")
