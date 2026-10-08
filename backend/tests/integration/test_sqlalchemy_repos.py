"""SQLAlchemy repository integration tests (sqlite+aiosqlite)."""

from __future__ import annotations

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from src.assistant.domain.profile import AssistantProfile
from src.call_management.domain.call import Call
from src.contacts.domain.contact import Contact
from src.infrastructure.persistence.orm import Base
from src.infrastructure.persistence.sqlalchemy_repos import (
    SqlAlchemyAssistantProfileRepository,
    SqlAlchemyCallRepository,
    SqlAlchemyContactRepository,
)
from src.shared.domain.value_objects import ConversationId, PhoneNumber


@pytest.fixture
async def session_factory():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    yield factory
    await engine.dispose()


async def test_call_roundtrip(session_factory) -> None:
    repo = SqlAlchemyCallRepository(session_factory)
    call = Call.receive(caller_phone=PhoneNumber("+14155552671"), provider_call_id="p-sql-1")
    call.answer()
    call.start_conversation(ConversationId.generate())
    await repo.save(call)

    loaded = await repo.get(call.id)
    assert loaded is not None
    assert loaded.status.value == "IN_PROGRESS"
    assert str(loaded.caller_phone) == "+14155552671"

    by_provider = await repo.get_by_provider_id("p-sql-1")
    assert by_provider is not None
    assert str(by_provider.id) == str(call.id)


async def test_contact_find_by_phone(session_factory) -> None:
    repo = SqlAlchemyContactRepository(session_factory)
    contact = Contact.create(name="Rajesh", phone=PhoneNumber("+919876543210"), is_trusted=True)
    await repo.save(contact)
    found = await repo.find_by_phone(PhoneNumber("+919876543210"))
    assert found is not None
    assert found.name == "Rajesh"
    assert found.is_trusted is True


async def test_assistant_profile_roundtrip(session_factory) -> None:
    repo = SqlAlchemyAssistantProfileRepository(session_factory)
    profile = AssistantProfile.default()
    await repo.save(profile)
    loaded = await repo.get("default")
    assert loaded is not None
    assert loaded.identity.assistant_name == "Sheeba"
    assert "Never claim to be Uday" in loaded.system_prompt
