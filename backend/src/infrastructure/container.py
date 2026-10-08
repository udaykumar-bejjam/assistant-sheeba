"""Composition root — wires ports to adapters."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from src.ai_agent.domain.policy import PolicyEvaluator
from src.assistant.domain.profile import AssistantProfile
from src.call_management.application.answer_incoming_call import AnswerIncomingCallService
from src.call_management.application.complete_call import CompleteCallService
from src.call_management.application.process_caller_message import (
    ProcessCallerMessageService,
    ToolExecutor,
)
from src.call_management.domain.call import Call
from src.contacts.domain.contact import Contact
from src.infrastructure.config.settings import Settings, get_settings
from src.infrastructure.messaging.event_bus import InProcessEventBus
from src.infrastructure.persistence.database import create_engine, create_session_factory
from src.infrastructure.persistence.memory import (
    InMemoryAssistantProfileRepository,
    InMemoryCallRepository,
    InMemoryContactRepository,
)
from src.infrastructure.persistence.sqlalchemy_repos import (
    SqlAlchemyAssistantProfileRepository,
    SqlAlchemyCallRepository,
    SqlAlchemyContactRepository,
)
from src.infrastructure.providers.ai.cursor_sdk import CursorSdkConversationProvider
from src.infrastructure.providers.ai.fake import FakeAIConversationProvider
from src.infrastructure.providers.notification.fake import FakeNotificationProvider
from src.infrastructure.providers.telephony.fake import FakeTelephonyProvider
from src.shared.application.ports import (
    AIConversationProvider,
    NotificationProvider,
    TelephonyProvider,
)
from src.shared.domain.value_objects import CallId, ContactId, PhoneNumber


class CallRepositoryPort(Protocol):
    async def get(self, call_id: CallId) -> Call | None: ...

    async def get_by_provider_id(self, provider_call_id: str) -> Call | None: ...

    async def save(self, call: Call) -> None: ...

    async def list_recent(self, *, limit: int = 50) -> list[Call]: ...


class ContactRepositoryPort(Protocol):
    async def get(self, contact_id: ContactId) -> Contact | None: ...

    async def find_by_phone(self, phone: PhoneNumber) -> Contact | None: ...

    async def save(self, contact: Contact) -> None: ...

    async def search(self, query: str, *, limit: int = 20) -> list[Contact]: ...

    async def list_all(self, *, limit: int = 200) -> list[Contact]: ...


class AssistantProfileRepositoryPort(Protocol):
    async def get(self, profile_id: str = "default") -> AssistantProfile | None: ...

    async def save(self, profile: AssistantProfile) -> None: ...


@dataclass(slots=True)
class AppContainer:
    settings: Settings
    calls: CallRepositoryPort
    contacts: ContactRepositoryPort
    profiles: AssistantProfileRepositoryPort
    events: InProcessEventBus
    telephony: TelephonyProvider
    ai: AIConversationProvider
    notifications: NotificationProvider
    answer_incoming_call: AnswerIncomingCallService
    process_caller_message: ProcessCallerMessageService
    complete_call: CompleteCallService


def build_container(settings: Settings | None = None) -> AppContainer:
    cfg = settings or get_settings()
    events = InProcessEventBus()
    telephony: TelephonyProvider = FakeTelephonyProvider()
    notifications: NotificationProvider = FakeNotificationProvider()

    # Production uses Postgres; local/tests stay in-memory unless production env.
    if cfg.app_env == "production":
        engine = create_engine(cfg.database_url, pool_size=cfg.database_pool_size)
        sessions = create_session_factory(engine)
        calls: CallRepositoryPort = SqlAlchemyCallRepository(sessions)
        contacts: ContactRepositoryPort = SqlAlchemyContactRepository(sessions)
        profiles: AssistantProfileRepositoryPort = SqlAlchemyAssistantProfileRepository(sessions)
    else:
        calls = InMemoryCallRepository()
        contacts = InMemoryContactRepository()
        profiles = InMemoryAssistantProfileRepository()

    if cfg.ai_provider == "cursor_sdk":
        ai: AIConversationProvider = CursorSdkConversationProvider(
            base_url=cfg.cursor_sdk_base_url,
            api_key=cfg.cursor_api_key or cfg.ai_api_key,
        )
    else:
        ai = FakeAIConversationProvider()

    policy = PolicyEvaluator()
    tools = ToolExecutor(calls=calls, events=events)

    return AppContainer(
        settings=cfg,
        calls=calls,
        contacts=contacts,
        profiles=profiles,
        events=events,
        telephony=telephony,
        ai=ai,
        notifications=notifications,
        answer_incoming_call=AnswerIncomingCallService(
            calls=calls,
            contacts=contacts,
            profiles=profiles,
            telephony=telephony,
            ai=ai,
            events=events,
        ),
        process_caller_message=ProcessCallerMessageService(
            calls=calls,
            contacts=contacts,
            profiles=profiles,
            ai=ai,
            policy=policy,
            events=events,
            tool_executor=tools,
        ),
        complete_call=CompleteCallService(
            calls=calls,
            events=events,
            notifications=notifications,
        ),
    )
