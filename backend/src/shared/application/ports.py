"""Cross-cutting application ports (protocols)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Protocol, runtime_checkable

from src.shared.domain.events import DomainEvent


@runtime_checkable
class EventBus(Protocol):
    async def publish(self, events: list[DomainEvent]) -> None: ...


@runtime_checkable
class UnitOfWork(Protocol):
    async def commit(self) -> None: ...

    async def rollback(self) -> None: ...


@dataclass(frozen=True, slots=True)
class ChatMessage:
    role: str
    content: str


@dataclass(frozen=True, slots=True)
class LLMResponse:
    content: str
    model: str = "unknown"
    tool_calls: list[dict[str, Any]] = field(default_factory=list)
    latency_ms: int = 0


@runtime_checkable
class LLMProvider(Protocol):
    async def complete(
        self,
        *,
        system: str,
        messages: list[ChatMessage],
        tools: list[dict[str, Any]] | None = None,
    ) -> LLMResponse: ...


@dataclass(frozen=True, slots=True)
class ConversationReply:
    text: str
    tool_calls: list[dict[str, Any]] = field(default_factory=list)
    language_hint: str | None = None


@runtime_checkable
class AIConversationProvider(Protocol):
    async def start_session(self, *, session_id: str, system_prompt: str) -> None: ...

    async def send_user_message(self, *, session_id: str, content: str) -> ConversationReply: ...

    async def end_session(self, *, session_id: str) -> None: ...


@runtime_checkable
class SpeechToTextProvider(Protocol):
    async def transcribe(self, audio: bytes, *, language: str | None = None) -> str: ...


@runtime_checkable
class TextToSpeechProvider(Protocol):
    async def synthesize(self, text: str, *, language: str | None = None) -> bytes: ...


@runtime_checkable
class RealtimeVoiceProvider(Protocol):
    async def connect(self, call_id: str) -> None: ...

    async def disconnect(self, call_id: str) -> None: ...


@runtime_checkable
class EmbeddingProvider(Protocol):
    async def embed(self, texts: list[str]) -> list[list[float]]: ...


@dataclass(frozen=True, slots=True)
class TelephonyCapabilities:
    answer: bool = True
    reject: bool = True
    hangup: bool = True
    cold_transfer: bool = False
    warm_transfer: bool = False
    bidirectional_audio_stream: bool = False
    recording: bool = False


@dataclass(frozen=True, slots=True)
class CallDetails:
    provider_call_id: str
    from_number: str
    to_number: str
    status: str


@runtime_checkable
class TelephonyProvider(Protocol):
    capabilities: TelephonyCapabilities

    async def answer_call(self, provider_call_id: str) -> None: ...

    async def reject_call(self, provider_call_id: str) -> None: ...

    async def hangup_call(self, provider_call_id: str) -> None: ...

    async def transfer_call(self, provider_call_id: str, destination: str) -> None: ...

    async def start_audio_stream(self, provider_call_id: str) -> None: ...

    async def stop_audio_stream(self, provider_call_id: str) -> None: ...

    async def get_call_details(self, provider_call_id: str) -> CallDetails: ...


@dataclass(frozen=True, slots=True)
class AvailabilitySlot:
    start: datetime
    end: datetime


@runtime_checkable
class CalendarProvider(Protocol):
    async def get_availability(self, start: datetime, end: datetime) -> list[AvailabilitySlot]: ...

    async def create_event(
        self,
        *,
        title: str,
        start: datetime,
        end: datetime,
        attendees: list[str] | None = None,
    ) -> str: ...

    async def cancel_event(self, event_id: str) -> None: ...

    async def update_event(
        self,
        event_id: str,
        *,
        title: str | None = None,
        start: datetime | None = None,
        end: datetime | None = None,
    ) -> None: ...


@dataclass(frozen=True, slots=True)
class NotificationMessage:
    subject: str
    body: str
    channel: str  # telegram | email | whatsapp
    metadata: dict[str, Any] = field(default_factory=dict)


@runtime_checkable
class NotificationProvider(Protocol):
    channel: str

    async def send(self, message: NotificationMessage) -> None: ...


@runtime_checkable
class ObjectStorageProvider(Protocol):
    async def put(self, key: str, data: bytes, content_type: str) -> str: ...

    async def get(self, key: str) -> bytes: ...

    async def delete(self, key: str) -> None: ...
