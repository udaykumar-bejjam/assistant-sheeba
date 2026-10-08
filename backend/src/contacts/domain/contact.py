"""Contact aggregate."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum

from src.shared.domain.errors import ValidationError
from src.shared.domain.value_objects import (
    CallPriority,
    ContactId,
    EmailAddress,
    PhoneNumber,
)


class ContactCategory(StrEnum):
    PERSONAL = "PERSONAL"
    BUSINESS = "BUSINESS"
    FAMILY = "FAMILY"
    VENDOR = "VENDOR"
    UNKNOWN = "UNKNOWN"


@dataclass(slots=True)
class Contact:
    id: ContactId
    name: str
    phone_numbers: list[PhoneNumber]
    email: EmailAddress | None = None
    company: str | None = None
    relationship: str | None = None
    category: ContactCategory = ContactCategory.UNKNOWN
    priority: CallPriority = CallPriority.MEDIUM
    notes: str | None = None
    is_trusted: bool = False
    is_blocked: bool = False
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValidationError("Contact name is required")
        if not self.phone_numbers:
            raise ValidationError("At least one phone number is required")
        if self.is_trusted and self.is_blocked:
            raise ValidationError("Contact cannot be both trusted and blocked")

    @classmethod
    def create(
        cls,
        *,
        name: str,
        phone: PhoneNumber,
        contact_id: ContactId | None = None,
        **kwargs: object,
    ) -> Contact:
        return cls(
            id=contact_id or ContactId.generate(),
            name=name.strip(),
            phone_numbers=[phone],
            **kwargs,  # type: ignore[arg-type]
        )

    def has_phone(self, phone: PhoneNumber) -> bool:
        return any(p.value == phone.value for p in self.phone_numbers)

    def block(self) -> None:
        self.is_blocked = True
        self.is_trusted = False
        self.updated_at = datetime.now(UTC)

    def trust(self) -> None:
        if self.is_blocked:
            raise ValidationError("Unblock contact before trusting")
        self.is_trusted = True
        self.updated_at = datetime.now(UTC)
