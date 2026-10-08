"""Test defaults — never hit production Postgres from unit/API tests."""

from __future__ import annotations

import os

import pytest

# Force non-production before settings are constructed.
os.environ["APP_ENV"] = "test"
os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+asyncpg://sheeba:sheeba@localhost:5432/sheeba",
)

from src.infrastructure.config.settings import get_settings  # noqa: E402


@pytest.fixture(autouse=True)
def _reset_settings_cache() -> None:
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()
