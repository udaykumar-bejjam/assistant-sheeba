"""Composition root — wires ports to adapters."""

from __future__ import annotations

from dataclasses import dataclass

from src.ai_agent.domain.policy import PolicyEvaluator
from src.call_management.application.answer_incoming_call import AnswerIncomingCallService
from src.call_management.application.complete_call import CompleteCallService
from src.call_management.application.process_caller_message import (
    ProcessCallerMessageService,
    ToolExecutor,
)
from src.infrastructure.config.settings import Settings, get_settings
from src.infrastructure.messaging.event_bus import InProcessEventBus
from src.infrastructure.persistence.memory import (
    InMemoryAssistantProfileRepository,
    InMemoryCallRepository,
    InMemoryContactRepository,
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


@dataclass(slots=True)
class AppContainer:
    settings: Settings
    calls: InMemoryCallRepository
    contacts: InMemoryContactRepository
    profiles: InMemoryAssistantProfileRepository
    events: InProcessEventBus
    telephony: TelephonyProvider
    ai: AIConversationProvider
    notifications: NotificationProvider
    answer_incoming_call: AnswerIncomingCallService
    process_caller_message: ProcessCallerMessageService
    complete_call: CompleteCallService


def build_container(settings: Settings | None = None) -> AppContainer:
    cfg = settings or get_settings()
    calls = InMemoryCallRepository()
    contacts = InMemoryContactRepository()
    profiles = InMemoryAssistantProfileRepository()
    events = InProcessEventBus()
    telephony: TelephonyProvider = FakeTelephonyProvider()
    notifications: NotificationProvider = FakeNotificationProvider()

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
