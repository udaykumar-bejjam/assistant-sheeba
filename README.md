# Sheeba — AI Personal Receptionist for Uday

Sheeba answers inbound phone calls on Uday’s behalf, converses in English/Telugu/Hinglish,
handles routine requests, and keeps Uday informed — **without ever impersonating Uday**.

> “Hi, I’m Uday’s AI assistant.”

## Architecture

Hexagonal / DDD platform with provider ports for telephony, AI, calendar, and notifications.
**Cursor SDK (BDK)** powers the conversational brain (`sheeba-agent/`).

See [ARCHITECTURE.md](ARCHITECTURE.md) and [docs/](docs/).

## Repository layout

| Path | Role |
| --- | --- |
| `backend/` | FastAPI + domain/application/infrastructure |
| `sheeba-agent/` | Cursor SDK AI brain (Sheeba) |
| `frontend/` | React admin dashboard |
| `docs/` | Architecture, API, security, ADRs |
| `docker-compose.yml` | PostgreSQL + Redis + API |

## Quick start

```bash
cp .env.example .env
docker compose up -d postgres redis

cd backend
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest
uvicorn src.interfaces.api.main:app --reload --port 8000
```

Dashboard:

```bash
cd frontend && npm install && npm run dev
```

Sheeba AI brain (optional live model; needs `CURSOR_API_KEY`):

```bash
cd sheeba-agent && npm install
# npx bdk serve --dir . --mode single --dev
```

Set `AI_PROVIDER=cursor_sdk` and `CURSOR_SDK_BASE_URL` to point the API at Sheeba.

## Vertical slice (working now)

```
POST /api/v1/calls/inbound
  → answer + greeting
POST /api/v1/calls/{id}/messages
  → AI reply + authorized tools (message/callback/…)
POST /api/v1/calls/{id}/complete
  → structured summary + notification port
```

External vendors are behind ports; CI uses fakes.

## Deploy (VPS API + FTP UI)

API runs on an existing VPS (Postgres/Redis already present) via **rsync + root password**.
UI `dist/` is uploaded to a **separate FTP host**.

```bash
cp .env.example .env
# fill VPS_HOST, VPS_PASSWORD, FTP_*, DATABASE_URL, CORS_ORIGINS, VITE_API_BASE_URL, JWT_SECRET
chmod +x scripts/deploy.sh scripts/deploy-api.sh scripts/deploy-ui.sh
./scripts/deploy.sh
```

Details: [docs/deployment.md](docs/deployment.md)

## Quality

```bash
cd backend
ruff check src tests
mypy src
pytest
```

## License

Proprietary — Uday / Sheeba project.
