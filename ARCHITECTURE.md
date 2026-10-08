# Sheeba — Architecture Overview

**Sheeba** is Uday’s personal AI receptionist / voice assistant platform.
It answers inbound phone calls, converses in English/Telugu/Hinglish,
handles routine requests, and keeps Uday informed — without ever
impersonating Uday.

## Guiding principles

1. **Domain-Driven Design** with practical bounded contexts
2. **Hexagonal / Clean Architecture** — domain has zero framework deps
3. **Dependency inversion** — all external systems behind ports
4. **Secure by default** — untrusted caller input, webhook verification, PII care
5. **Provider abstraction** — telephony, AI, calendar, notifications are swappable
6. **Cursor SDK as AI brain** — Sheeba agent (`sheeba-agent/`) is the LLM brain behind `LLMProvider` / `AIConversationProvider`

## Logical runtime flow

```
Caller
  → Telephony Provider (Twilio/Exotel/… via TelephonyProvider)
  → Voice Streaming Adapter
  → AI Voice Orchestration
       ├── Conversation / Agent (Sheeba via Cursor SDK)
       ├── Knowledge Retrieval
       ├── Tool Execution + Authorization
       ├── Call Classification
       └── Safety / Guardrails
  → Application Layer (Calls, Contacts, Calendar, …)
  → Infrastructure (PostgreSQL, Redis, Object Storage, External APIs)
  → React Admin Dashboard
```

## Bounded contexts

| Context | Responsibility |
| --- | --- |
| **Call Management** | Call lifecycle, status, transfer, outcomes, transcripts, summaries |
| **Voice Conversation** | Real-time conversation state, barge-in, language detection |
| **AI Agent** | Intent, tools, policy, safety, prompt versioning (Sheeba brain) |
| **Contacts** | Caller identity, trust/block, relationship rules |
| **Knowledge** | RAG documents, chunks, semantic search |
| **Scheduling** | Availability, appointments via CalendarProvider |
| **Notifications** | Owner alerts via Telegram/Email/WhatsApp adapters |
| **Assistant Configuration** | Identity rules, transfer rules, languages, recording policy |
| **Identity / Access** | Authn/authz for dashboard and APIs |
| **Analytics** | Aggregated metrics (non-sensitive) |
| **Shared** | Value objects, domain errors, event bus contracts |

## Dependency rule

```
Domain  ←  Application  ←  Interfaces (API/Webhooks)
                ↑
         Infrastructure (adapters implementing ports)
```

- Domain imports **nothing** external (no FastAPI, SQLAlchemy, SDKs).
- Application depends on domain + port protocols.
- Infrastructure implements ports.
- Interfaces invoke application services only.

## Identity invariant (non-negotiable)

Sheeba **must** identify as: *“Hi, I’m Uday’s AI assistant.”* (product name: Sheeba)

Sheeba must **never** claim to be Uday. This is enforced by:

1. Versioned system policy in `AssistantProfile` (not caller-controllable)
2. Policy evaluator before sensitive tools
3. Separation of SYSTEM POLICY / DOMAIN KNOWLEDGE / CALLER INPUT
4. Hard refusal patterns for impersonation / prompt injection

## AI brain: Cursor SDK (Sheeba)

The domain/application layers speak only to:

- `LLMProvider`
- `AIConversationProvider`
- `SpeechToTextProvider` / `TextToSpeechProvider` / `RealtimeVoiceProvider`
- `EmbeddingProvider`

The **Cursor SDK / BDK agent** at `sheeba-agent/` is the first concrete
`AIConversationProvider` / `LLMProvider` implementation. It owns:

- Versioned receptionist instructions
- Tool definitions for call-handling actions
- Safety framing around untrusted caller speech

Python infrastructure adapters call the Sheeba host over HTTP (or local
fakes in tests). OpenAI/other providers remain optional alternate adapters.

## Aggregates (initial)

- **Call** — participants, conversation ref, classification, outcome
- **Appointment** — participants, time range, status
- **AssistantProfile** — identity, languages, transfer/recording rules
- **Contact** — phones, trust, category, handling rules
- **KnowledgeDocument** — chunks, category, embedding refs
- **CallbackRequest** / **Notification** — supporting aggregates

## Vertical slice (Phase 0–4 target)

```
Inbound webhook (fake telephony)
  → Create Call (RINGING → CONNECTED → IN_PROGRESS)
  → Sheeba AI greeting (mock or Cursor SDK)
  → Process message → Take message / classify
  → Complete call → Structured summary
  → Notification port (fake)
```

## Provider capability isolation

Never assume a telephony vendor supports warm transfer, barge-in, or
bidirectional streaming. Each adapter documents supported capabilities
via `TelephonyCapabilities`. Missing features degrade gracefully
(e.g. transfer unavailable → offer callback/message).

## See also

- [docs/architecture.md](docs/architecture.md)
- [docs/domain-model.md](docs/domain-model.md)
- [docs/api.md](docs/api.md)
- [docs/security.md](docs/security.md)
- [docs/deployment.md](docs/deployment.md)
- [docs/decisions/](docs/decisions/)
