"""Fake AI providers for tests and local vertical slice."""

from __future__ import annotations

from typing import Any

from src.shared.application.ports import ChatMessage, ConversationReply, LLMResponse


class FakeLLMProvider:
    def __init__(self, response: str = "How can I help you today?") -> None:
        self.response = response
        self.calls: list[dict[str, Any]] = []

    async def complete(
        self,
        *,
        system: str,
        messages: list[ChatMessage],
        tools: list[dict[str, Any]] | None = None,
    ) -> LLMResponse:
        self.calls.append({"system": system, "messages": messages, "tools": tools})
        return LLMResponse(content=self.response, model="fake", latency_ms=1)


class FakeAIConversationProvider:
    """Deterministic conversation brain used until Cursor SDK is wired."""

    def __init__(self) -> None:
        self.sessions: dict[str, list[dict[str, str]]] = {}
        self.system_prompts: dict[str, str] = {}

    async def start_session(self, *, session_id: str, system_prompt: str) -> None:
        self.sessions[session_id] = []
        self.system_prompts[session_id] = system_prompt

    async def send_user_message(self, *, session_id: str, content: str) -> ConversationReply:
        if session_id not in self.sessions:
            self.sessions[session_id] = []
        self.sessions[session_id].append({"role": "user", "content": content})

        lower = content.lower()
        tool_calls: list[dict[str, Any]] = []
        text: str

        wants_message = "message" in lower and (
            "leave" in lower or "tell uday" in lower or "take a message" in lower
        )
        if wants_message:
            tool_calls.append(
                {
                    "name": "take_message",
                    "arguments": {"message": content},
                }
            )
            text = "Of course. I've noted that message for Uday."
        elif "callback" in lower or "call me back" in lower:
            tool_calls.append(
                {
                    "name": "request_callback",
                    "arguments": {"note": content, "preferred_time": ""},
                }
            )
            text = "I've created a callback request for Uday."
        elif "transfer" in lower or "speak to uday" in lower or "talk to uday" in lower:
            tool_calls.append(
                {
                    "name": "transfer_call",
                    "arguments": {"reason": content, "caller_confirmed": True},
                }
            )
            text = "I can connect you with Uday. Connecting you now."
        elif "bye" in lower or "goodbye" in lower or "that's all" in lower:
            tool_calls.append({"name": "end_call", "arguments": {"reason": "caller_ended"}})
            text = "Thank you for calling. Goodbye."
        else:
            text = (
                "Thanks for sharing that. I can take a message, request a callback, "
                "or help with scheduling if you'd like."
            )

        self.sessions[session_id].append({"role": "assistant", "content": text})
        return ConversationReply(text=text, tool_calls=tool_calls)

    async def end_session(self, *, session_id: str) -> None:
        self.sessions.pop(session_id, None)
        self.system_prompts.pop(session_id, None)
