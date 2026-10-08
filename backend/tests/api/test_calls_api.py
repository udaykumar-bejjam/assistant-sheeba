"""API tests for call endpoints."""

from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient
from src.infrastructure.container import build_container
from src.interfaces.api.main import create_app


@pytest.fixture
def app_client():
    container = build_container()
    app = create_app(container=container)
    return app, container


async def test_inbound_message_complete_flow(app_client) -> None:
    app, _container = app_client
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        health = await client.get("/health")
        assert health.status_code == 200

        inbound = await client.post(
            "/api/v1/calls/inbound",
            json={
                "provider_call_id": "api-1",
                "from_number": "+14155552671",
            },
        )
        assert inbound.status_code == 200
        data = inbound.json()
        call_id = data["call_id"]
        assert "AI assistant" in data["greeting"]

        msg = await client.post(
            f"/api/v1/calls/{call_id}/messages",
            json={"text": "Please call me back tomorrow"},
        )
        assert msg.status_code == 200
        assert "request_callback" in msg.json()["tools_executed"]

        done = await client.post(
            f"/api/v1/calls/{call_id}/complete",
            json={
                "summary_text": "Requested callback tomorrow",
                "requested_action": "Callback",
            },
        )
        assert done.status_code == 200
        assert done.json()["status"] == "COMPLETED"

        detail = await client.get(f"/api/v1/calls/{call_id}")
        assert detail.status_code == 200
        assert detail.json()["summary"]["callback_requested"] is True


async def test_assistant_settings(app_client) -> None:
    app, _ = app_client
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/assistant/settings")
        assert resp.status_code == 200
        body = resp.json()
        assert body["assistant_name"] == "Sheeba"
        assert body["owner_name"] == "Uday"
