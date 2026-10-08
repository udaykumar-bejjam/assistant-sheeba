"""Voice conversation state machine."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum

from src.shared.domain.errors import InvalidStateTransitionError
from src.shared.domain.value_objects import CallId, ConversationId, Language


class VoiceState(StrEnum):
    LISTENING = "LISTENING"
    THINKING = "THINKING"
    SPEAKING = "SPEAKING"
    INTERRUPTED = "INTERRUPTED"
    WAITING = "WAITING"
    ENDING = "ENDING"


_TRANSITIONS: dict[VoiceState, frozenset[VoiceState]] = {
    VoiceState.LISTENING: frozenset(
        {VoiceState.THINKING, VoiceState.ENDING, VoiceState.WAITING}
    ),
    VoiceState.THINKING: frozenset(
        {VoiceState.SPEAKING, VoiceState.LISTENING, VoiceState.ENDING}
    ),
    VoiceState.SPEAKING: frozenset(
        {
            VoiceState.LISTENING,
            VoiceState.INTERRUPTED,
            VoiceState.WAITING,
            VoiceState.ENDING,
        }
    ),
    VoiceState.INTERRUPTED: frozenset(
        {VoiceState.LISTENING, VoiceState.THINKING, VoiceState.ENDING}
    ),
    VoiceState.WAITING: frozenset(
        {VoiceState.LISTENING, VoiceState.THINKING, VoiceState.ENDING}
    ),
    VoiceState.ENDING: frozenset(),
}


@dataclass(slots=True)
class Turn:
    role: str  # "caller" | "assistant" | "system"
    content: str
    at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass(slots=True)
class ConversationState:
    id: ConversationId
    call_id: CallId
    voice_state: VoiceState = VoiceState.LISTENING
    language: Language = Language.AUTO
    turns: list[Turn] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def transition(self, new_state: VoiceState) -> None:
        allowed = _TRANSITIONS.get(self.voice_state, frozenset())
        if new_state not in allowed:
            raise InvalidStateTransitionError(
                f"Invalid voice transition {self.voice_state} → {new_state}"
            )
        self.voice_state = new_state

    def add_caller_message(self, content: str) -> None:
        text = content.strip()
        if not text:
            return
        if self.voice_state == VoiceState.SPEAKING:
            self.transition(VoiceState.INTERRUPTED)
        self.turns.append(Turn(role="caller", content=text))
        if self.voice_state in {
            VoiceState.INTERRUPTED,
            VoiceState.LISTENING,
            VoiceState.WAITING,
        }:
            self.transition(VoiceState.THINKING)

    def add_assistant_message(self, content: str) -> None:
        self.turns.append(Turn(role="assistant", content=content))
        if self.voice_state == VoiceState.THINKING:
            self.transition(VoiceState.SPEAKING)

    def short_term_memory(self, *, limit: int = 20) -> list[Turn]:
        return self.turns[-limit:]
