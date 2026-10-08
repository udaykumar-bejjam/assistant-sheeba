# Deployment

Sheeba splits runtime across two hosts:

| Component | Where | How |
| --- | --- | --- |
| **API** | Existing VPS (Postgres/Redis already installed) | `rsync` over SSH **password** auth (`root` + password, no SSH keys) |
| **UI** | Separate IP / shared hosting | Vite `dist/` uploaded via **FTP** |

## 1. Configure `.env`

```bash
cp .env.example .env
# edit: VPS_*, FTP_*, DATABASE_URL, REDIS_URL, JWT_SECRET, CORS_ORIGINS, VITE_API_BASE_URL
```

Required deploy keys:

- `VPS_HOST`, `VPS_USER=root`, `VPS_PASSWORD`, `VPS_APP_DIR=/opt/sheeba`
- `FTP_HOST`, `FTP_USER`, `FTP_PASSWORD`, `FTP_REMOTE_DIR`
- `DATABASE_URL` / `REDIS_URL` pointing at **local** VPS services (`127.0.0.1`)
- `CORS_ORIGINS` must include the UI origin
- `VITE_API_BASE_URL` = public API URL the browser will call

`.env` is gitignored. Never commit passwords.

## 2. One-shot deploy

```bash
chmod +x scripts/deploy.sh scripts/deploy-api.sh scripts/deploy-ui.sh
./scripts/deploy.sh
```

Order:

1. **`deploy-api.sh`** — `sshpass` + `rsync` → VPS, upload `.env`, run `deploy/remote-setup.sh` (venv, pip, alembic, systemd, optional nginx site)
2. **`deploy-ui.sh`** — `npm run build`, then `lftp mirror -R` of `frontend/dist` to the FTP host

Individual steps:

```bash
./scripts/deploy-api.sh
./scripts/deploy-ui.sh
```

## 3. VPS expectations

- Postgres and Redis already running (shared with other apps)
- Free TCP port for Sheeba (`APP_PORT`, default `8000`)
- Nginx optional: script adds `sites-available/sheeba-api` only; does not rewrite other sites
- Create DB once:

```sql
CREATE USER sheeba WITH PASSWORD '...';
CREATE DATABASE sheeba OWNER sheeba;
```

## 4. Local development

```bash
cp .env.example .env
# set APP_ENV=development and local DATABASE_URL/REDIS_URL
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

## 5. Security notes

- SSH uses **password only** (`PubkeyAuthentication=no`) as required for this VPS
- Prefer rotating `VPS_PASSWORD` / `FTP_PASSWORD` after first setup
- Prefer FTPS (`FTP_SSL=true`) when the UI host supports it
- Restrict Postgres/Redis to localhost on the VPS
- Put TLS in front of the API (existing nginx/certbot on the VPS)

## Production checklist

- [ ] Fill real `.env` (VPS + FTP + DB + JWT + CORS)
- [ ] Create Postgres role/database for Sheeba
- [ ] Choose unused `APP_PORT`
- [ ] Run `./scripts/deploy.sh`
- [ ] Verify `curl https://<api>/health`
- [ ] Open UI URL and confirm calls list loads
- [ ] Webhook public URL + signature secrets
- [ ] Retention/deletion jobs for recordings/transcripts
