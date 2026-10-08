"""Environment-based configuration."""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_env: Literal["development", "test", "production"] = "development"
    app_name: str = Field(default="Sheeba", alias="APP_NAME")
    app_host: str = Field(default="0.0.0.0", alias="APP_HOST")
    app_port: int = Field(default=8000, alias="APP_PORT")
    public_api_url: str | None = Field(default=None, alias="PUBLIC_API_URL")
    log_level: str = "INFO"
    json_logs: bool = True

    database_url: str = Field(
        default="postgresql+asyncpg://sheeba:sheeba@localhost:5432/sheeba",
        alias="DATABASE_URL",
    )
    database_pool_size: int = Field(default=10, alias="DATABASE_POOL_SIZE")
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
    telephony_webhook_base_url: str | None = Field(
        default=None, alias="TELEPHONY_WEBHOOK_BASE_URL"
    )

    google_client_id: str | None = Field(default=None, alias="GOOGLE_CLIENT_ID")
    google_client_secret: str | None = Field(default=None, alias="GOOGLE_CLIENT_SECRET")
    google_redirect_uri: str | None = Field(default=None, alias="GOOGLE_REDIRECT_URI")

    telegram_bot_token: str | None = Field(default=None, alias="TELEGRAM_BOT_TOKEN")
    telegram_chat_id: str | None = Field(default=None, alias="TELEGRAM_CHAT_ID")
    notification_email_from: str | None = Field(
        default=None, alias="NOTIFICATION_EMAIL_FROM"
    )
    smtp_host: str | None = Field(default=None, alias="SMTP_HOST")
    smtp_port: int = Field(default=587, alias="SMTP_PORT")
    smtp_user: str | None = Field(default=None, alias="SMTP_USER")
    smtp_password: str | None = Field(default=None, alias="SMTP_PASSWORD")

    storage_bucket: str | None = Field(default=None, alias="STORAGE_BUCKET")
    storage_endpoint: str | None = Field(default=None, alias="STORAGE_ENDPOINT")
    storage_access_key: str | None = Field(default=None, alias="STORAGE_ACCESS_KEY")
    storage_secret_key: str | None = Field(default=None, alias="STORAGE_SECRET_KEY")

    jwt_secret: str = Field(default="dev-only-change-me", alias="JWT_SECRET")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    jwt_expire_minutes: int = Field(default=10080, alias="JWT_EXPIRE_MINUTES")
    cors_origins: str = Field(default="http://localhost:5173", alias="CORS_ORIGINS")

    recording_enabled: bool = Field(default=False, alias="RECORDING_ENABLED")
    transcription_enabled: bool = Field(default=True, alias="TRANSCRIPTION_ENABLED")
    retention_days: int = Field(default=30, alias="RETENTION_DAYS")

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
