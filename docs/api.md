# API Design

Base path: `/api/v1`

Admin APIs use JWT/session auth. Telephony webhooks use signature verification.

## Calls

| Method | Path | Description |
| --- | --- | --- |
| POST | `/calls/inbound` | Telephony inbound (webhook-facing; also used by fakes) |
| GET | `/calls` | List calls |
| GET | `/calls/{id}` | Call detail + summary/transcript refs |
| POST | `/calls/{id}/complete` | Force-complete (ops) |
| POST | `/calls/{id}/transfer` | Request transfer |

## Contacts / Callbacks / Appointments / Knowledge

| Method | Path |
| --- | --- |
| GET/POST | `/contacts` |
| GET/PATCH | `/contacts/{id}` |
| GET/POST | `/callbacks` |
| GET/POST | `/appointments` |
| GET/POST | `/knowledge` |
| GET/PUT | `/assistant/settings` |
| GET/PUT | `/notifications/settings` |
| GET | `/analytics/dashboard` |

## Real-time

- WebSocket `/ws/v1/voice/{call_id}` for streaming audio when the telephony adapter requires app-mediated media.

## OpenAPI

FastAPI generates OpenAPI at `/openapi.json` and Swagger UI at `/docs`.
