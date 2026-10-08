# ADR 0001: Hexagonal DDD for Sheeba

## Status

Accepted

## Context

Sheeba must integrate telephony, AI, calendar, and notifications without
locking the domain to any vendor. The product must evolve into a personal
AI operating system across phone, chat, and web.

## Decision

Use practical Domain-Driven Design with hexagonal ports/adapters:

- Domain: pure Python business rules
- Application: use cases + ports
- Infrastructure: SQLAlchemy, Redis, provider SDKs
- Interfaces: FastAPI, webhooks, websockets

## Consequences

- Higher initial structure cost
- Provider swaps do not rewrite business rules
- Testability via fakes/mocks at ports
