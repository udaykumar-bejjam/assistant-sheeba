from __future__ import annotations

from src.ai_agent.domain.conversation_state import ConversationState, VoiceState
from src.shared.domain.value_objects import CallId, ConversationId


def test_barge_in_path() -> None:
    state = ConversationState(id=ConversationId.generate(), call_id=CallId.generate())
    state.transition(VoiceState.THINKING)
    state.add_assistant_message("Hello, how can I help?")
    assert state.voice_state == VoiceState.SPEAKING
    state.add_caller_message("Actually wait")
    assert state.voice_state == VoiceState.THINKING
