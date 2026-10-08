#!/usr/bin/env bash
# Build the React dashboard and upload dist/ via FTP to a separate UI host.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "$SCRIPT_DIR/lib/env.sh"

require_var FTP_HOST
require_var FTP_USER
require_var FTP_PASSWORD
require_var FTP_REMOTE_DIR

# Allow FTP_HOST values like ftp://1.2.3.4
FTP_HOST="${FTP_HOST#ftp://}"
FTP_HOST="${FTP_HOST#ftps://}"
FTP_HOST="${FTP_HOST%%/*}"

FRONTEND_DIR="$REPO_ROOT/frontend"
DIST_DIR="$FRONTEND_DIR/dist"

if ! command -v lftp >/dev/null 2>&1; then
  echo "Installing lftp locally..."
  sudo apt-get update -qq
  sudo DEBIAN_FRONTEND=noninteractive apt-get install -y -qq lftp
fi

echo "==> Building frontend (VITE_API_BASE_URL=${VITE_API_BASE_URL:-})"
cd "$FRONTEND_DIR"
if [[ ! -d node_modules ]]; then
  npm install
fi
export VITE_API_BASE_URL="${VITE_API_BASE_URL:-}"
npm run build

if [[ ! -d "$DIST_DIR" ]]; then
  echo "Build failed: $DIST_DIR missing" >&2
  exit 1
fi

SSL_OPTS=""
if [[ "${FTP_SSL:-false}" == "true" ]]; then
  SSL_OPTS="set ftp:ssl-force true; set ftp:ssl-protect-data true; set ssl:verify-certificate no;"
else
  SSL_OPTS="set ftp:ssl-allow no;"
fi

echo "==> FTP upload → ${FTP_HOST}:${FTP_REMOTE_DIR}"
# mirror -R uploads local dist into remote dir; --delete removes stale assets
lftp -u "${FTP_USER},${FTP_PASSWORD}" -p "${FTP_PORT:-21}" "ftp://${FTP_HOST}" <<EOF
set cmd:fail-exit true
${SSL_OPTS}
set net:max-retries 3
set net:timeout 30
mkdir -p ${FTP_REMOTE_DIR}
cd ${FTP_REMOTE_DIR}
mirror -R --delete --verbose ${DIST_DIR} .
bye
EOF

echo "==> UI deploy finished → ftp://${FTP_HOST}${FTP_REMOTE_DIR}"
