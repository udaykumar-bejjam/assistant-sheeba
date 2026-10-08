"""Environment-based configuration."""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: Literal["development", "test", "production"] = "development"
    app_name: str = "Sheeba"
    log_level: str = "INFO"
    json_logs: bool = True

    database_url: str = Field(
        default="postgresql+asyncpg://sheeba:sheeba@localhost:5432/sheeba",
        alias="DATABASE_URL",
    )
    redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")

    ai_provider: Literal["fake", "cursor_sdk"] = Field(default="fake", alias="AI_PROVIDER")
    ai_api_key: str | None = Field(default=None, alias="AI_API_KEY")
    cursor_sdk_base_url: str = Field(
        default="http://127.0.0.1:3000",
        alias="CURSOR_SDK_BASE_URL",
    )
    cursor_api_key: str | None = Field(default=None, alias="CURSOR_API_KEY")

    telephony_provider: Literal["fake"] = Field(default="fake", alias="TELEPHONY_PROVIDER")
    telephony_api_key: str | None = Field(default=None, alias="TELEPHONY_API_KEY")
    telephony_webhook_secret: str | None = Field(
        default=None, alias="TELEPHONY_WEBHOOK_SECRET"
    )

    google_client_id: str | None = Field(default=None, alias="GOOGLE_CLIENT_ID")
    google_client_secret: str | None = Field(default=None, alias="GOOGLE_CLIENT_SECRET")

    telegram_bot_token: str | None = Field(default=None, alias="TELEGRAM_BOT_TOKEN")
    storage_bucket: str | None = Field(default=None, alias="STORAGE_BUCKET")

    jwt_secret: str = Field(default="dev-only-change-me", alias="JWT_SECRET")
    cors_origins: str = Field(default="http://localhost:5173", alias="CORS_ORIGINS")

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
