"""Shared value objects."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from uuid import UUID, uuid4

import phonenumbers

from src.shared.domain.errors import ValidationError

_E164 = re.compile(r"^\+[1-9]\d{6,14}$")
_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class CallStatus(StrEnum):
    RINGING = "RINGING"
    CONNECTED = "CONNECTED"
    IN_PROGRESS = "IN_PROGRESS"
    TRANSFERRED = "TRANSFERRED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    MISSED = "MISSED"
    ABANDONED = "ABANDONED"


TERMINAL_CALL_STATUSES: frozenset[CallStatus] = frozenset(
    {
        CallStatus.COMPLETED,
        CallStatus.FAILED,
        CallStatus.MISSED,
        CallStatus.ABANDONED,
        CallStatus.TRANSFERRED,
    }
)


class CallPriority(StrEnum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    URGENT = "URGENT"


class CallIntent(StrEnum):
    GENERAL_ENQUIRY = "GENERAL_ENQUIRY"
    PERSONAL = "PERSONAL"
    BUSINESS = "BUSINESS"
    SALES = "SALES"
    SUPPORT = "SUPPORT"
    APPOINTMENT = "APPOINTMENT"
    CALLBACK = "CALLBACK"
    SPAM = "SPAM"
    UNKNOWN = "UNKNOWN"


class Language(StrEnum):
    EN = "EN"
    TE = "TE"
    HI_EN = "HI_EN"
    AUTO = "AUTO"


@dataclass(frozen=True, slots=True)
class PhoneNumber:
    value: str

    def __post_init__(self) -> None:
        normalized = self._normalize(self.value)
        object.__setattr__(self, "value", normalized)

    @staticmethod
    def _normalize(raw: str) -> str:
        text = raw.strip()
        if not text:
            raise ValidationError("Phone number is required")
        try:
            parsed = phonenumbers.parse(text, None)
            if not phonenumbers.is_possible_number(parsed):
                raise ValidationError(f"Invalid phone number: {raw}")
            e164 = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
        except phonenumbers.NumberParseException:
            if _E164.match(text):
                return text
            raise ValidationError(f"Invalid phone number: {raw}") from None
        if not _E164.match(e164):
            raise ValidationError(f"Invalid phone number: {raw}")
        return e164

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class EmailAddress:
    value: str

    def __post_init__(self) -> None:
        normalized = self.value.strip().lower()
        if not _EMAIL.match(normalized):
            raise ValidationError(f"Invalid email: {self.value}")
        object.__setattr__(self, "value", normalized)

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class TimeRange:
    start: datetime
    end: datetime

    def __post_init__(self) -> None:
        if self.end <= self.start:
            raise ValidationError("TimeRange end must be after start")

    def overlaps(self, other: TimeRange) -> bool:
        return self.start < other.end and other.start < self.end


def _new_id() -> str:
    return str(uuid4())


@dataclass(frozen=True, slots=True)
class CallId:
    value: str

    def __post_init__(self) -> None:
        UUID(self.value)  # validate format

    @classmethod
    def generate(cls) -> CallId:
        return cls(_new_id())

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class ContactId:
    value: str

    def __post_init__(self) -> None:
        UUID(self.value)

    @classmethod
    def generate(cls) -> ContactId:
        return cls(_new_id())

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class ConversationId:
    value: str

    def __post_init__(self) -> None:
        UUID(self.value)

    @classmethod
    def generate(cls) -> ConversationId:
        return cls(_new_id())

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class AppointmentId:
    value: str

    def __post_init__(self) -> None:
        UUID(self.value)

    @classmethod
    def generate(cls) -> AppointmentId:
        return cls(_new_id())

    def __str__(self) -> str:
        return self.value
