# ADR 0005: Split API VPS (password SSH) + UI FTP deploy

## Status

Accepted

## Context

The API must run on an existing multi-tenant VPS that already hosts Postgres,
Redis, and other applications. The UI is served from a different IP where only
FTP upload of static files is available. VPS access is root + password (no SSH keys).

## Decision

1. Deploy API with `sshpass` + `rsync` + systemd unit under `/opt/sheeba` (configurable).
2. Do not install or replace shared Postgres/Redis; only connect via `DATABASE_URL` / `REDIS_URL`.
3. Optionally add a dedicated nginx site file without modifying other sites.
4. Build UI with Vite and upload `frontend/dist` via `lftp` to the FTP host.
5. Keep all secrets in gitignored `.env`; ship `.env.example` as the contract.

## Consequences

- Operators must fill VPS/FTP credentials before `./scripts/deploy.sh`.
- Password SSH is weaker than keys; restrict firewall and rotate passwords.
- CORS and `VITE_API_BASE_URL` must point at the public API origin.
