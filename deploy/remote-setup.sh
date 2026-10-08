#!/usr/bin/env bash
# Runs ON the VPS after rsync. Uses existing Postgres/Redis; does not install them.
set -euo pipefail

APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$APP_DIR"

if [[ -f "$APP_DIR/.env" ]]; then
  set -a
  # shellcheck disable=SC1091
  source "$APP_DIR/.env"
  set +a
fi

PYTHON_BIN="${VPS_PYTHON:-python3.12}"
SERVICE_NAME="${VPS_SERVICE_NAME:-sheeba-api}"
APP_PORT="${APP_PORT:-8000}"
APP_HOST="${APP_HOST:-0.0.0.0}"

mkdir -p "$APP_DIR/logs" "$APP_DIR/run"

if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  PYTHON_BIN="python3"
fi

echo "[remote] Python: $($PYTHON_BIN --version)"

if [[ ! -d .venv ]]; then
  echo "[remote] Creating venv"
  "$PYTHON_BIN" -m venv .venv
fi
# shellcheck disable=SC1091
source .venv/bin/activate
pip install -U pip wheel
pip install -e .

echo "[remote] Alembic migrations (uses DATABASE_URL from .env)"
if [[ -f alembic.ini ]]; then
  alembic upgrade head || {
    echo "[remote] WARNING: alembic failed — ensure DB role/database exist:"
    echo "  CREATE USER sheeba WITH PASSWORD '...';"
    echo "  CREATE DATABASE sheeba OWNER sheeba;"
  }
fi

echo "[remote] Installing systemd unit (will not stop other services)"
UNIT_SRC="$APP_DIR/deploy/systemd/sheeba-api.service"
UNIT_DST="/etc/systemd/system/${SERVICE_NAME}.service"
sed \
  -e "s|__APP_DIR__|${APP_DIR}|g" \
  -e "s|__APP_HOST__|${APP_HOST}|g" \
  -e "s|__APP_PORT__|${APP_PORT}|g" \
  "$UNIT_SRC" > "$UNIT_DST"

systemctl daemon-reload
systemctl enable "$SERVICE_NAME"
systemctl restart "$SERVICE_NAME"

if [[ -d "${VPS_NGINX_AVAILABLE:-/etc/nginx/sites-available}" ]] && [[ -f "$APP_DIR/deploy/nginx/sheeba-api.conf" ]]; then
  echo "[remote] Installing nginx site (optional; does not overwrite other sites)"
  NGINX_AVAIL="${VPS_NGINX_AVAILABLE:-/etc/nginx/sites-available}"
  NGINX_ENAB="${VPS_NGINX_ENABLED:-/etc/nginx/sites-enabled}"
  sed \
    -e "s|__SERVER_NAME__|${VPS_API_SERVER_NAME:-_}|g" \
    -e "s|__UPSTREAM_PORT__|${APP_PORT}|g" \
    "$APP_DIR/deploy/nginx/sheeba-api.conf" > "${NGINX_AVAIL}/sheeba-api"
  ln -sfn "${NGINX_AVAIL}/sheeba-api" "${NGINX_ENAB}/sheeba-api"
  if nginx -t; then
    systemctl reload nginx
  else
    echo "[remote] WARNING: nginx -t failed; left site file in place but did not reload"
  fi
fi

echo "[remote] Health check"
sleep 2
curl -fsS "http://127.0.0.1:${APP_PORT}/health" || true
echo
echo "[remote] Setup complete for ${SERVICE_NAME}"
