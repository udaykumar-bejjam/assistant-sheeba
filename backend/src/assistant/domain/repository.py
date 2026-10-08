"""Assistant profile repository port."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from src.assistant.domain.profile import AssistantProfile


@runtime_checkable
class AssistantProfileRepository(Protocol):
    async def get(self, profile_id: str = "default") -> AssistantProfile | None: ...

    async def save(self, profile: AssistantProfile) -> None: ...
