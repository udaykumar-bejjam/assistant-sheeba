"""FastAPI dependencies."""

from __future__ import annotations

from fastapi import Request

from src.infrastructure.container import AppContainer

_container: AppContainer | None = None


def set_container(container: AppContainer) -> None:
    global _container
    _container = container


def get_container(request: Request | None = None) -> AppContainer:
    if request is not None and hasattr(request.app.state, "container"):
        container = request.app.state.container
        if isinstance(container, AppContainer):
            return container
    if _container is None:
        raise RuntimeError("App container not initialized")
    return _container
