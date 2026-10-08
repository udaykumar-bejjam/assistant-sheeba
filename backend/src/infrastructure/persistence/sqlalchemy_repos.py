"""SQLAlchemy repository adapters."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.assistant.domain.profile import AssistantProfile
from src.call_management.domain.call import Call
from src.contacts.domain.contact import Contact
from src.infrastructure.persistence.mappers import (
    call_to_row,
    contact_to_row,
    profile_to_row,
    row_to_call,
    row_to_contact,
    row_to_profile,
)
from src.infrastructure.persistence.orm import AssistantProfileRow, CallRow, ContactRow
from src.shared.domain.value_objects import CallId, ContactId, PhoneNumber


class SqlAlchemyCallRepository:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._sessions = session_factory

    async def get(self, call_id: CallId) -> Call | None:
        async with self._sessions() as session:
            row = await session.get(CallRow, str(call_id))
            return row_to_call(row) if row else None

    async def get_by_provider_id(self, provider_call_id: str) -> Call | None:
        async with self._sessions() as session:
            result = await session.execute(
                select(CallRow).where(CallRow.provider_call_id == provider_call_id)
            )
            row = result.scalar_one_or_none()
            return row_to_call(row) if row else None

    async def save(self, call: Call) -> None:
        async with self._sessions() as session:
            existing = await session.get(CallRow, str(call.id))
            mapped = call_to_row(call)
            if existing is None:
                session.add(mapped)
            else:
                for column in CallRow.__table__.columns.keys():  # noqa: SIM118
                    setattr(existing, column, getattr(mapped, column))
            await session.commit()

    async def list_recent(self, *, limit: int = 50) -> list[Call]:
        async with self._sessions() as session:
            result = await session.execute(
                select(CallRow).order_by(CallRow.created_at.desc()).limit(limit)
            )
            return [row_to_call(row) for row in result.scalars().all()]


class SqlAlchemyContactRepository:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._sessions = session_factory

    async def get(self, contact_id: ContactId) -> Contact | None:
        async with self._sessions() as session:
            row = await session.get(ContactRow, str(contact_id))
            return row_to_contact(row) if row else None

    async def find_by_phone(self, phone: PhoneNumber) -> Contact | None:
        async with self._sessions() as session:
            result = await session.execute(select(ContactRow))
            for row in result.scalars().all():
                if phone.value in (row.phone_numbers_json or []):
                    return row_to_contact(row)
            return None

    async def save(self, contact: Contact) -> None:
        async with self._sessions() as session:
            existing = await session.get(ContactRow, str(contact.id))
            mapped = contact_to_row(contact)
            if existing is None:
                session.add(mapped)
            else:
                for column in ContactRow.__table__.columns.keys():  # noqa: SIM118
                    setattr(existing, column, getattr(mapped, column))
            await session.commit()

    async def search(self, query: str, *, limit: int = 20) -> list[Contact]:
        q = query.lower()
        async with self._sessions() as session:
            result = await session.execute(select(ContactRow).limit(500))
            matches = [
                row_to_contact(row)
                for row in result.scalars().all()
                if q in row.name.lower() or (row.company and q in row.company.lower())
            ]
            return matches[:limit]

    async def list_all(self, *, limit: int = 200) -> list[Contact]:
        async with self._sessions() as session:
            result = await session.execute(
                select(ContactRow).order_by(ContactRow.name.asc()).limit(limit)
            )
            return [row_to_contact(row) for row in result.scalars().all()]


class SqlAlchemyAssistantProfileRepository:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._sessions = session_factory

    async def get(self, profile_id: str = "default") -> AssistantProfile | None:
        async with self._sessions() as session:
            row = await session.get(AssistantProfileRow, profile_id)
            return row_to_profile(row) if row else None

    async def save(self, profile: AssistantProfile) -> None:
        async with self._sessions() as session:
            existing = await session.get(AssistantProfileRow, profile.id)
            mapped = profile_to_row(profile)
            if existing is None:
                session.add(mapped)
            else:
                existing.config_json = mapped.config_json
                existing.system_prompt = mapped.system_prompt
                existing.prompt_version = mapped.prompt_version
                existing.updated_at = mapped.updated_at
            await session.commit()
