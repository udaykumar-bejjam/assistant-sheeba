# ADR 0002: Cursor SDK (BDK) as Sheeba AI brain

## Status

Accepted

## Context

The product needs a strong conversational brain with tools, instructions,
and evals. The team has Cursor SDK / BDK available. Domain layers must not
depend on any LLM SDK.

## Decision

- Name the assistant **Sheeba**.
- Implement a BDK agent under `sheeba-agent/` as the primary AI brain.
- Expose Python ports `LLMProvider` and `AIConversationProvider`.
- First adapter: `CursorSdkConversationProvider` calling the Sheeba host HTTP API.
- Keep OpenAI/other adapters as optional alternatives behind the same ports.
- Fake providers for unit/CI tests.

## Consequences

- Live model turns require Cursor credentials (`CURSOR_API_KEY` etc.).
- Tool authorization remains in the Python application policy layer;
  Sheeba tools are thin or mirrored for agent-side reasoning.
- Prompt versioning lives in AssistantProfile + sheeba-agent instructions.
