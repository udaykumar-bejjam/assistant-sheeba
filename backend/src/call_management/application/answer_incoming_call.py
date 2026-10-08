"""Use case: answer an incoming call and start AI greeting."""

from __future__ import annotations

from dataclasses import dataclass

from src.assistant.domain.profile import AssistantProfile
from src.assistant.domain.repository import AssistantProfileRepository
from src.call_management.domain.call import Call
from src.call_management.domain.repository import CallRepository
from src.contacts.domain.repository import ContactRepository
from src.shared.application.ports import (
    AIConversationProvider,
    EventBus,
    TelephonyProvider,
)
from src.shared.domain.value_objects import ConversationId, PhoneNumber
from src.shared.infrastructure.logging import get_logger

logger = get_logger(__name__)


@dataclass(frozen=True, slots=True)
class AnswerIncomingCallCommand:
    provider_call_id: str
    from_number: str
    to_number: str = ""


@dataclass(frozen=True, slots=True)
class AnswerIncomingCallResult:
    call_id: str
    conversation_id: str
    greeting: str
    caller_known: bool
    caller_name: str | None


class AnswerIncomingCallService:
    def __init__(
        self,
        *,
        calls: CallRepository,
        contacts: ContactRepository,
        profiles: AssistantProfileRepository,
        telephony: TelephonyProvider,
        ai: AIConversationProvider,
        events: EventBus,
    ) -> None:
        self._calls = calls
        self._contacts = contacts
        self._profiles = profiles
        self._telephony = telephony
        self._ai = ai
        self._events = events

    async def execute(self, command: AnswerIncomingCallCommand) -> AnswerIncomingCallResult:
        phone = PhoneNumber(command.from_number)
        existing = await self._calls.get_by_provider_id(command.provider_call_id)
        if existing is not None:
            call = existing
        else:
            call = Call.receive(
                caller_phone=phone,
                provider_call_id=command.provider_call_id,
            )

        contact = await self._contacts.find_by_phone(phone)
        if contact is not None:
            if contact.is_blocked:
                await self._telephony.reject_call(command.provider_call_id)
                call.complete(failed=True)
                await self._calls.save(call)
                await self._events.publish(call.collect_events())
                return AnswerIncomingCallResult(
                    call_id=str(call.id),
                    conversation_id="",
                    greeting="",
                    caller_known=True,
                    caller_name=contact.name,
                )
            call.identify_caller(contact_id=contact.id, name=contact.name)

        await self._telephony.answer_call(command.provider_call_id)
        if call.status.value == "RINGING":
            call.answer()

        conversation_id = ConversationId.generate()
        call.start_conversation(conversation_id)

        profile = await self._get_profile()
        greeting = profile.identity.greeting
        if contact is not None and contact.name:
            greeting = f"{greeting} Hi {contact.name}."

        await self._ai.start_session(
            session_id=str(conversation_id),
            system_prompt=profile.system_prompt,
        )
        # Seed assistant greeting into conversation provider.
        await self._calls.save(call)
        await self._events.publish(call.collect_events())

        logger.info(
            "call_answered",
            call_id=str(call.id),
            conversation_id=str(conversation_id),
            caller_known=contact is not None,
        )

        return AnswerIncomingCallResult(
            call_id=str(call.id),
            conversation_id=str(conversation_id),
            greeting=greeting,
            caller_known=contact is not None,
            caller_name=contact.name if contact else None,
        )

    async def _get_profile(self) -> AssistantProfile:
        profile = await self._profiles.get("default")
        if profile is None:
            profile = AssistantProfile.default()
            await self._profiles.save(profile)
        return profile
