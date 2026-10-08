"""Knowledge repository / search ports."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from src.knowledge.domain.knowledge import KnowledgeDocument


@runtime_checkable
class KnowledgeDocumentRepository(Protocol):
    async def get(self, document_id: str) -> KnowledgeDocument | None: ...

    async def save(self, document: KnowledgeDocument) -> None: ...

    async def list_approved(self, *, limit: int = 100) -> list[KnowledgeDocument]: ...


@runtime_checkable
class KnowledgeSearchPort(Protocol):
    async def search(self, query: str, *, limit: int = 5) -> list[str]: ...
