"""FastAPI application entrypoint."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.infrastructure.config.settings import get_settings
from src.infrastructure.container import AppContainer, build_container
from src.interfaces.api.deps import set_container
from src.interfaces.api.v1.router import api_router
from src.shared.infrastructure.logging import configure_logging, get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    configure_logging(json_logs=settings.json_logs, level=settings.log_level)
    container = build_container(settings)
    set_container(container)
    app.state.container = container
    logger.info("sheeba_api_started", env=settings.app_env, ai_provider=settings.ai_provider)
    yield


def create_app(container: AppContainer | None = None) -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="Sheeba API",
        version="0.1.0",
        description="Uday's AI personal voice receptionist",
        lifespan=lifespan if container is None else None,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(api_router, prefix="/api/v1")

    if container is not None:
        set_container(container)
        app.state.container = container

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok", "service": "sheeba"}

    return app


app = create_app()
