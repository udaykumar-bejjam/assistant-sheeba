"""API v1 router aggregation."""

from __future__ import annotations

from fastapi import APIRouter

from src.interfaces.api.v1 import assistant, calls, contacts, health

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(calls.router, prefix="/calls", tags=["calls"])
api_router.include_router(contacts.router, prefix="/contacts", tags=["contacts"])
api_router.include_router(assistant.router, prefix="/assistant", tags=["assistant"])
