from __future__ import annotations

from src.knowledge.domain.knowledge import KnowledgeCategory, KnowledgeDocument


def test_chunk_document() -> None:
    doc = KnowledgeDocument.create(
        title="About Uday",
        category=KnowledgeCategory.ABOUT_UDAY,
        content="Uday builds software. " * 40,
        approved=True,
    )
    chunks = doc.chunk_text(size=80, overlap=10)
    assert len(chunks) >= 2
    assert all(c.document_id == doc.id for c in chunks)
