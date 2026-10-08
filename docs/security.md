# Security

## Threat model highlights

- Callers are **untrusted**. Speech/text is treated as hostile input.
- Telephony webhooks must verify signature + timestamp.
- Dashboard APIs require authentication and RBAC.
- Secrets never appear in logs, prompts, or client responses.

## Prompt injection defense

1. System policy is versioned and isolated from caller turns.
2. Knowledge and caller input are clearly delimited in model context.
3. Policy evaluator runs before sensitive tools (`transfer_call`,
   `create_calendar_event`, anything touching PII disclosure).
4. Identity impersonation is a hard refusal.

## Webhooks

- HMAC signature verification
- Timestamp skew window
- Reject missing/invalid signatures with 401
- Never trust caller-supplied IDs without repository lookup

## PII

- Phone numbers and transcripts are sensitive.
- Default logging redacts conversation content.
- Configurable retention: `recording_enabled`, `transcription_enabled`, `retention_days`.

## Auth

- JWT/session for dashboard
- OAuth for Google Calendar
- Role-based authorization (owner / operator / viewer)

## Secrets

Environment variables only. See `.env.example`. Never commit `.env`.
