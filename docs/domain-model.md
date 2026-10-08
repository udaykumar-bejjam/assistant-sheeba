# Domain Model

## Value objects

| VO | Notes |
| --- | --- |
| `PhoneNumber` | E.164 normalized |
| `CallId`, `ContactId`, `ConversationId`, `AppointmentId` | typed UUIDs |
| `EmailAddress` | validated |
| `CallStatus` | RINGING, CONNECTED, IN_PROGRESS, TRANSFERRED, COMPLETED, FAILED, MISSED, ABANDONED |
| `CallPriority` | LOW, MEDIUM, HIGH, URGENT |
| `CallIntent` | GENERAL_ENQUIRY, PERSONAL, BUSINESS, SALES, SUPPORT, APPOINTMENT, CALLBACK, SPAM, UNKNOWN |
| `Language` | EN, TE, HI_EN (Hinglish), AUTO |
| `TimeRange` | start < end |
| `SpamAssessment` | score, classification, reasons |

## Aggregates

### Call

Invariants:

- Completed/failed/missed/abandoned are terminal (no return to IN_PROGRESS).
- Transfer only from IN_PROGRESS.
- Summary structured fields required after meaningful completion.

### AssistantProfile

Invariants:

- Display identity never equals owner name as “self”.
- Identity greeting is mandatory and versioned.
- Transfer rules gate `transfer_call` tool.

### Appointment

Invariants:

- Confirmed appointments require valid `TimeRange`.
- Cannot confirm overlapping blocked slots (enforced via calendar port + domain service).

### Contact

- Known vs unknown via phone lookup.
- `is_blocked` short-circuits AI handling (reject/polite end).
- `is_trusted` may relax transfer thresholds.

### KnowledgeDocument

- Categories: ABOUT_UDAY, BUSINESS, PROJECTS, SERVICES, FAQ, CONTACT_POLICY, AVAILABILITY, PERSONAL_ASSISTANT_RULES
- Only approved documents enter RAG context.

## Domain events

`CallReceived`, `CallAnswered`, `CallStarted`, `CallCompleted`, `CallTransferred`,
`CallerIdentified`, `CallClassified`, `MessageTaken`, `CallbackRequested`,
`AppointmentRequested`, `AppointmentScheduled`, `SpamDetected`,
`TranscriptCompleted`, `CallSummaryGenerated`, `ImportantCallDetected`,
`NotificationRequested`.

Events carry IDs and facts only — handlers live in application/infrastructure.
