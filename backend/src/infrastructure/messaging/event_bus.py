"""In-process async event bus."""

from __future__ import annotations

from collections.abc import Awaitable, Callable

from src.shared.domain.events import DomainEvent
from src.shared.infrastructure.logging import get_logger

logger = get_logger(__name__)

EventHandler = Callable[[DomainEvent], Awaitable[None]]


class InProcessEventBus:
    def __init__(self) -> None:
        self._handlers: list[EventHandler] = []
        self.published: list[DomainEvent] = []

    def subscribe(self, handler: EventHandler) -> None:
        self._handlers.append(handler)

    async def publish(self, events: list[DomainEvent]) -> None:
        for event in events:
            self.published.append(event)
            logger.info(
                "domain_event",
                event_type=event.event_type,
                aggregate_id=event.aggregate_id,
            )
            for handler in self._handlers:
                try:
                    await handler(event)
                except Exception:
                    logger.exception(
                        "event_handler_failed",
                        event_type=event.event_type,
                    )


class RecordingEventBus:
    """Test helper that records events without handlers."""

    def __init__(self) -> None:
        self.published: list[DomainEvent] = []

    async def publish(self, events: list[DomainEvent]) -> None:
        self.published.extend(events)

    def of_type(self, name: str) -> list[DomainEvent]:
        return [e for e in self.published if e.event_type == name]
