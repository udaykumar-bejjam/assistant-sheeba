from __future__ import annotations

from fastapi import APIRouter

router = APIRouter()


@router.get("/status")
async def api_status() -> dict[str, str]:
    return {"status": "ok", "api": "v1"}
