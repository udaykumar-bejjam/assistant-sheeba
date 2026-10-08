"""In-memory repositories for tests and local vertical slice."""

from __future__ import annotations

from src.assistant.domain.profile import AssistantProfile
from src.call_management.domain.call import Call
from src.contacts.domain.contact import Contact
from src.shared.domain.value_objects import CallId, ContactId, PhoneNumber


class InMemoryCallRepository:
    def __init__(self) -> None:
        self._by_id: dict[str, Call] = {}
        self._by_provider: dict[str, str] = {}

    async def get(self, call_id: CallId) -> Call | None:
        return self._by_id.get(str(call_id))

    async def get_by_provider_id(self, provider_call_id: str) -> Call | None:
        cid = self._by_provider.get(provider_call_id)
        if cid is None:
            return None
        return self._by_id.get(cid)

    async def save(self, call: Call) -> None:
        self._by_id[str(call.id)] = call
        self._by_provider[call.provider_call_id] = str(call.id)

    async def list_recent(self, *, limit: int = 50) -> list[Call]:
        calls = sorted(self._by_id.values(), key=lambda c: c.created_at, reverse=True)
        return calls[:limit]


class InMemoryContactRepository:
    def __init__(self) -> None:
        self._by_id: dict[str, Contact] = {}

    async def get(self, contact_id: ContactId) -> Contact | None:
        return self._by_id.get(str(contact_id))

    async def find_by_phone(self, phone: PhoneNumber) -> Contact | None:
        for contact in self._by_id.values():
            if contact.has_phone(phone):
                return contact
        return None

    async def save(self, contact: Contact) -> None:
        self._by_id[str(contact.id)] = contact

    async def search(self, query: str, *, limit: int = 20) -> list[Contact]:
        q = query.lower()
        results = [
            c
            for c in self._by_id.values()
            if q in c.name.lower() or (c.company and q in c.company.lower())
        ]
        return results[:limit]

    async def list_all(self, *, limit: int = 200) -> list[Contact]:
        return list(self._by_id.values())[:limit]


class InMemoryAssistantProfileRepository:
    def __init__(self) -> None:
        self._profiles: dict[str, AssistantProfile] = {
            "default": AssistantProfile.default(),
        }

    async def get(self, profile_id: str = "default") -> AssistantProfile | None:
        return self._profiles.get(profile_id)

    async def save(self, profile: AssistantProfile) -> None:
        self._profiles[profile.id] = profile
