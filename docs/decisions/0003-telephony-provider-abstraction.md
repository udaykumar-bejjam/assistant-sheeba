# ADR 0003: Telephony provider abstraction with capability flags

## Status

Accepted

## Context

Programmable telephony vendors (Twilio, Exotel, Plivo, …) differ in
streaming, warm transfer, and barge-in support.

## Decision

Define `TelephonyProvider` + `TelephonyCapabilities`. Adapters declare
what they support. Orchestration degrades gracefully when a capability
is missing (e.g. no warm transfer → callback/message offer).

First concrete adapter may target Twilio Media Streams or Exotel;
until credentials exist, use `FakeTelephonyProvider`.

## Consequences

- No assumption that warm transfer always works
- Capability checks before transfer/stream operations
- Documented per-adapter limitations in adapter modules
