# Architecture Detail

## Package layout

```
backend/src/
  shared/                 # Cross-cutting domain primitives
  call_management/        # Call aggregate & use cases
  voice/                  # Conversation state machine
  ai_agent/               # Agent orchestration, tools, policy
  contacts/
  knowledge/
  scheduling/
  notifications/
  assistant/              # AssistantProfile aggregate
  identity/
  analytics/
  infrastructure/         # Adapters, config, persistence
  interfaces/             # FastAPI, webhooks, websockets
sheeba-agent/             # Cursor SDK (BDK) AI brain
frontend/                 # React admin dashboard
```

Each bounded context uses:

```
domain/         # entities, VOs, events, repository protocols
application/    # commands, use cases, DTOs
infrastructure/ # ORM models, adapters (optional early)
interfaces/     # HTTP routers for this context (optional)
```

## Ports (selected)

| Port | Purpose |
| --- | --- |
| `TelephonyProvider` | answer/reject/hangup/transfer/stream |
| `LLMProvider` | text generation |
| `AIConversationProvider` | multi-turn conversation |
| `RealtimeVoiceProvider` | streaming STT/TTS/realtime |
| `SpeechToTextProvider` / `TextToSpeechProvider` | media conversion |
| `EmbeddingProvider` | knowledge embeddings |
| `CalendarProvider` | availability + events |
| `NotificationProvider` | Telegram/Email/WhatsApp |
| `ObjectStorageProvider` | recordings/transcripts |
| `EventBus` | domain event dispatch |

## Event flow (async post-call)

```
CallCompleted
  → GenerateTranscript
  → GenerateCallSummary
  → DeterminePriority
  → NotifyOwner (if required)
  → UpdateAnalytics
```

Live call path stays latency-critical; post-call work is async.

## Conversation states

`LISTENING → THINKING → SPEAKING → INTERRUPTED → WAITING → ENDING`

## Configuration

Environment-based via Pydantic Settings. Secrets never committed.
See `.env.example`.
