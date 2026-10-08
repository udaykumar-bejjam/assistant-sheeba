"""Contact repository port."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from src.contacts.domain.contact import Contact
from src.shared.domain.value_objects import ContactId, PhoneNumber


@runtime_checkable
class ContactRepository(Protocol):
    async def get(self, contact_id: ContactId) -> Contact | None: ...

    async def find_by_phone(self, phone: PhoneNumber) -> Contact | None: ...

    async def save(self, contact: Contact) -> None: ...

    async def search(self, query: str, *, limit: int = 20) -> list[Contact]: ...

    async def list_all(self, *, limit: int = 200) -> list[Contact]: ...
