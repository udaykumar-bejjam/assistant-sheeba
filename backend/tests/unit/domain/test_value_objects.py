from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest
from src.shared.domain.errors import ValidationError
from src.shared.domain.value_objects import EmailAddress, PhoneNumber, TimeRange


def test_phone_e164() -> None:
    phone = PhoneNumber("+1 (415) 555-2671")
    assert phone.value.startswith("+")


def test_invalid_phone() -> None:
    with pytest.raises(ValidationError):
        PhoneNumber("not-a-phone")


def test_email() -> None:
    assert str(EmailAddress("Uday@Example.COM")) == "uday@example.com"


def test_time_range() -> None:
    start = datetime.now(UTC)
    end = start + timedelta(hours=1)
    tr = TimeRange(start=start, end=end)
    assert tr.overlaps(TimeRange(start=start + timedelta(minutes=30), end=end + timedelta(hours=1)))
    with pytest.raises(ValidationError):
        TimeRange(start=end, end=start)
