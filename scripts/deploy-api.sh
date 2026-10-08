#!/usr/bin/env bash
# Rsync Sheeba API to an existing VPS using root + password (no SSH keys).
# Designed to coexist with other services already running on the VPS.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "$SCRIPT_DIR/lib/env.sh"

require_var VPS_HOST
require_var VPS_USER
require_var VPS_PASSWORD
require_var VPS_APP_DIR

if ! command -v sshpass >/dev/null 2>&1; then
  echo "Installing sshpass locally..."
  sudo apt-get update -qq
  sudo DEBIAN_FRONTEND=noninteractive apt-get install -y -qq sshpass
fi

echo "==> Creating remote directories on ${VPS_HOST}"
ssh_cmd "mkdir -p ${VPS_APP_DIR} ${VPS_APP_DIR}/logs ${VPS_APP_DIR}/run ${VPS_APP_DIR}/deploy"

echo "==> Rsync backend → ${VPS_APP_DIR}"
rsync_ssh \
  --exclude '.venv/' \
  --exclude '__pycache__/' \
  --exclude '.pytest_cache/' \
  --exclude '.mypy_cache/' \
  --exclude '.ruff_cache/' \
  --exclude '*.egg-info/' \
  --exclude '.git/' \
  "$REPO_ROOT/backend/" \
  "${VPS_USER}@${VPS_HOST}:${VPS_APP_DIR}/"

echo "==> Rsync deploy assets → ${VPS_APP_DIR}/deploy"
rsync_ssh \
  "$REPO_ROOT/deploy/" \
  "${VPS_USER}@${VPS_HOST}:${VPS_APP_DIR}/deploy/"

echo "==> Upload .env (chmod 600)"
SSHPASS="$VPS_PASSWORD" sshpass -e scp \
  -P "${VPS_PORT:-22}" \
  -o StrictHostKeyChecking=accept-new \
  -o PreferredAuthentications=password \
  -o PubkeyAuthentication=no \
  -o IdentitiesOnly=yes \
  "$ENV_FILE" \
  "${VPS_USER}@${VPS_HOST}:${VPS_APP_DIR}/.env"
ssh_cmd "chmod 600 ${VPS_APP_DIR}/.env"

echo "==> Remote setup (venv, deps, migrate, systemd)"
ssh_cmd "bash ${VPS_APP_DIR}/deploy/remote-setup.sh"

echo "==> API status"
ssh_cmd "systemctl --no-pager --full status ${VPS_SERVICE_NAME:-sheeba-api} | head -n 25 || true"
echo "==> API deploy finished → ${VPS_HOST}:${VPS_APP_DIR}"
