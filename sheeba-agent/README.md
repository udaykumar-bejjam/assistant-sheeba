# Sheeba Agent (Cursor SDK / BDK)

Conversational AI brain for Uday’s receptionist platform.

The Python backend talks to this agent through `CursorSdkConversationProvider`
(`AI_PROVIDER=cursor_sdk`). Domain code never imports BDK types.

## Run locally

```bash
npm install
# requires CURSOR_API_KEY for live model turns
npx bdk validate --dir .
npx bdk serve --dir . --mode single --dev
```

Playground: http://127.0.0.1:3000/playground

## Tools

- `take_message`
- `request_callback`
- `end_call`

Authorization for sensitive actions is enforced again in the Python
`PolicyEvaluator` before side effects persist.
