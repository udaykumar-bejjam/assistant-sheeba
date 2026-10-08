# Deployment

## Local development

```bash
cp .env.example .env
docker compose up -d postgres redis
cd backend && python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
alembic upgrade head
uvicorn src.interfaces.api.main:app --reload --port 8000
```

Frontend:

```bash
cd frontend && npm install && npm run dev
```

Sheeba AI brain (Cursor SDK):

```bash
cd sheeba-agent && npm install
# Requires CURSOR_API_KEY for live model turns
npx bdk serve --dir . --mode single --dev
```

## Production checklist

- [ ] HTTPS termination (Nginx/ingress)
- [ ] Managed PostgreSQL + Redis
- [ ] Object storage for recordings
- [ ] Secrets via vault/KMS/env injection
- [ ] Alembic migrations in deploy pipeline
- [ ] Webhook public URL + signature secrets
- [ ] Observability exporters (structured logs + metrics)
- [ ] Retention/deletion jobs for recordings/transcripts
- [ ] Rate limiting at edge and app

## Docker Compose

`docker-compose.yml` provides PostgreSQL, Redis, API, and optionally
the dashboard for local stacks. Production prefers managed services.
