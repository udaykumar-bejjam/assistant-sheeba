"""Call repository port."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from src.call_management.domain.call import Call
from src.shared.domain.value_objects import CallId


@runtime_checkable
class CallRepository(Protocol):
    async def get(self, call_id: CallId) -> Call | None: ...

    async def get_by_provider_id(self, provider_call_id: str) -> Call | None: ...

    async def save(self, call: Call) -> None: ...

    async def list_recent(self, *, limit: int = 50) -> list[Call]: ...
