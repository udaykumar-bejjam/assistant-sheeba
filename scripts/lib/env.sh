#!/usr/bin/env bash
# Load repo-root .env into the current shell (safe for simple KEY=VALUE lines).
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
ENV_FILE="${ENV_FILE:-$REPO_ROOT/.env}"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "Missing $ENV_FILE — copy .env.example to .env and fill values." >&2
  exit 1
fi

set -a
# shellcheck disable=SC1090
source "$ENV_FILE"
set +a

require_var() {
  local name="$1"
  if [[ -z "${!name:-}" || "${!name}" == CHANGE_ME* ]]; then
    echo "Set $name in $ENV_FILE before deploying." >&2
    exit 1
  fi
}

ssh_cmd() {
  # Password auth only — no SSH keys / agent.
  SSHPASS="$VPS_PASSWORD" sshpass -e ssh \
    -p "${VPS_PORT:-22}" \
    -o StrictHostKeyChecking=accept-new \
    -o PreferredAuthentications=password \
    -o PubkeyAuthentication=no \
    -o IdentitiesOnly=yes \
    -o NumberOfPasswordPrompts=1 \
    "${VPS_USER}@${VPS_HOST}" "$@"
}

rsync_ssh() {
  SSHPASS="$VPS_PASSWORD" sshpass -e rsync -az --delete \
    -e "ssh -p ${VPS_PORT:-22} -o StrictHostKeyChecking=accept-new -o PreferredAuthentications=password -o PubkeyAuthentication=no -o IdentitiesOnly=yes -o NumberOfPasswordPrompts=1" \
    "$@"
}
