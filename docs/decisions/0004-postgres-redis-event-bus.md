# ADR 0004: PostgreSQL + Redis + in-process event bus (initial)

## Status

Accepted

## Context

Need durable persistence, short-lived call session state, and async
post-call processing without introducing Kafka on day one.

## Decision

- PostgreSQL (SQLAlchemy 2 + Alembic) for aggregates
- Redis for conversation short-term memory / rate limits / locks
- In-process async `EventBus` with optional Redis pub/sub later
- Vector search behind `KnowledgeSearchPort` (pgvector-ready)

## Consequences

- Simple local Docker Compose
- Can replace bus with queue (SQS/Rabbit) without domain changes
