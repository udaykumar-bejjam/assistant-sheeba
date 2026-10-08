"""Knowledge base domain types for RAG."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from uuid import uuid4

from src.shared.domain.errors import ValidationError


class KnowledgeCategory(StrEnum):
    ABOUT_UDAY = "ABOUT_UDAY"
    BUSINESS = "BUSINESS"
    PROJECTS = "PROJECTS"
    SERVICES = "SERVICES"
    FAQ = "FAQ"
    CONTACT_POLICY = "CONTACT_POLICY"
    AVAILABILITY = "AVAILABILITY"
    PERSONAL_ASSISTANT_RULES = "PERSONAL_ASSISTANT_RULES"


@dataclass(slots=True)
class KnowledgeChunk:
    id: str
    document_id: str
    content: str
    chunk_index: int
    embedding: list[float] | None = None


@dataclass(slots=True)
class KnowledgeDocument:
    id: str
    title: str
    category: KnowledgeCategory
    content: str
    approved: bool = False
    chunks: list[KnowledgeChunk] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    @classmethod
    def create(
        cls,
        *,
        title: str,
        category: KnowledgeCategory,
        content: str,
        approved: bool = False,
    ) -> KnowledgeDocument:
        if not title.strip() or not content.strip():
            raise ValidationError("Knowledge document title and content are required")
        return cls(
            id=str(uuid4()),
            title=title.strip(),
            category=category,
            content=content.strip(),
            approved=approved,
        )

    def approve(self) -> None:
        self.approved = True
        self.updated_at = datetime.now(UTC)

    def chunk_text(self, *, size: int = 500, overlap: int = 50) -> list[KnowledgeChunk]:
        if size <= overlap:
            raise ValidationError("chunk size must exceed overlap")
        text = self.content
        chunks: list[KnowledgeChunk] = []
        index = 0
        start = 0
        while start < len(text):
            end = min(len(text), start + size)
            piece = text[start:end].strip()
            if piece:
                chunks.append(
                    KnowledgeChunk(
                        id=str(uuid4()),
                        document_id=self.id,
                        content=piece,
                        chunk_index=index,
                    )
                )
                index += 1
            if end >= len(text):
                break
            start = end - overlap
        self.chunks = chunks
        return chunks
