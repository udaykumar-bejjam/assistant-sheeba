"""Fake notification provider."""

from __future__ import annotations

from src.shared.application.ports import NotificationMessage


class FakeNotificationProvider:
    channel = "telegram"

    def __init__(self) -> None:
        self.sent: list[NotificationMessage] = []

    async def send(self, message: NotificationMessage) -> None:
        self.sent.append(message)
