"""Cursor SDK (BDK Sheeba host) AI conversation adapter.

Talks to the Sheeba agent HTTP API. Domain/application never import
BDK/Cursor SDK types — only this adapter does HTTP.
"""

from __future__ import annotations

from typing import Any

import httpx

from src.shared.application.ports import ConversationReply
from src.shared.domain.errors import AIProviderError
from src.shared.infrastructure.logging import get_logger

logger = get_logger(__name__)


class CursorSdkConversationProvider:
    """AIConversationProvider backed by Sheeba BDK HTTP host.

    Expected Sheeba host endpoints (BDK serve):
      POST /v1/chat  { message, continuationToken? }
    Exact paths may vary by BDK version; configure via base_url.
    """

    def __init__(
        self,
        *,
        base_url: str,
        api_key: str | None = None,
        timeout_seconds: float = 60.0,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key
        self._timeout = timeout_seconds
        self._tokens: dict[str, str] = {}
        self._system: dict[str, str] = {}

    def _headers(self) -> dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self._api_key:
            headers["Authorization"] = f"Bearer {self._api_key}"
        return headers

    async def start_session(self, *, session_id: str, system_prompt: str) -> None:
        self._system[session_id] = system_prompt
        self._tokens.pop(session_id, None)
        logger.info("cursor_sdk_session_started", session_id=session_id)

    async def send_user_message(self, *, session_id: str, content: str) -> ConversationReply:
        # Prefix untrusted caller content; system prompt stays server-side in Sheeba.
        framed = (
            "[CALLER_INPUT — untrusted]\n"
            f"{content}\n"
            "[/CALLER_INPUT]"
        )
        payload: dict[str, Any] = {"message": framed}
        token = self._tokens.get(session_id)
        if token:
            payload["continuationToken"] = token

        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.post(
                    f"{self._base_url}/v1/chat",
                    json=payload,
                    headers=self._headers(),
                )
                response.raise_for_status()
                data = response.json()
        except httpx.HTTPError as exc:
            raise AIProviderError(f"Sheeba Cursor SDK unavailable: {exc}") from exc

        # BDK response shapes vary; accept common fields.
        text = (
            data.get("message")
            or data.get("text")
            or data.get("output")
            or data.get("content")
            or ""
        )
        if isinstance(text, dict):
            text = text.get("text") or text.get("content") or str(text)

        new_token = data.get("continuationToken") or data.get("continuation_token")
        if isinstance(new_token, str) and new_token:
            self._tokens[session_id] = new_token

        tool_calls = data.get("toolCalls") or data.get("tool_calls") or []
        if not isinstance(tool_calls, list):
            tool_calls = []

        return ConversationReply(text=str(text), tool_calls=tool_calls)

    async def end_session(self, *, session_id: str) -> None:
        self._tokens.pop(session_id, None)
        self._system.pop(session_id, None)
