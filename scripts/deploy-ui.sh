#!/usr/bin/env bash
# Build the React dashboard and upload dist/ via FTP.
# Uploads through the API VPS jump host because direct FTP data channels
# from some CI/cloud networks fail against Hostinger passive FTP.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "$SCRIPT_DIR/lib/env.sh"

require_var FTP_HOST
require_var FTP_USER
require_var FTP_PASSWORD
require_var FTP_REMOTE_DIR
require_var VPS_HOST
require_var VPS_USER
require_var VPS_PASSWORD

FTP_HOST="${FTP_HOST#ftp://}"
FTP_HOST="${FTP_HOST#ftps://}"
FTP_HOST="${FTP_HOST%%/*}"

FRONTEND_DIR="$REPO_ROOT/frontend"
DIST_DIR="$FRONTEND_DIR/dist"
REMOTE_STAGE="/tmp/sheeba-ui-dist"

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

if ! command -v sshpass >/dev/null 2>&1; then
  sudo apt-get update -qq
  sudo DEBIAN_FRONTEND=noninteractive apt-get install -y -qq sshpass rsync
fi

echo "==> Stage dist on VPS ${VPS_HOST}:${REMOTE_STAGE}"
ssh_cmd "rm -rf ${REMOTE_STAGE} && mkdir -p ${REMOTE_STAGE}"
rsync_ssh "$DIST_DIR/" "${VPS_USER}@${VPS_HOST}:${REMOTE_STAGE}/"

echo "==> FTP upload from VPS → ${FTP_HOST}:${FTP_REMOTE_DIR}"
ssh_cmd "python3 - <<'PY'
from ftplib import FTP, error_perm
from pathlib import Path
import time

host = '''${FTP_HOST}'''
user = '''${FTP_USER}'''
password = '''${FTP_PASSWORD}'''
remote_dir = '''${FTP_REMOTE_DIR}'''
local = Path('''${REMOTE_STAGE}''')

def connect():
    ftp = FTP()
    ftp.connect(host, int('${FTP_PORT:-21}'), timeout=180)
    ftp.login(user, password)
    ftp.set_pasv(True)
    if remote_dir not in ('', '/', '.'):
        try:
            ftp.cwd(remote_dir)
        except error_perm:
            # try create nested path
            parts = [p for p in remote_dir.split('/') if p]
            for i in range(len(parts)):
                cur = '/'.join(parts[: i + 1])
                try:
                    ftp.mkd('/' + cur if remote_dir.startswith('/') else cur)
                except error_perm:
                    pass
            ftp.cwd(remote_dir)
    return ftp

def upload_file(rel: str, path: Path) -> None:
    for attempt in range(1, 6):
        ftp = None
        try:
            ftp = connect()
            parent = '/'.join(rel.split('/')[:-1])
            if parent:
                try:
                    ftp.mkd(parent)
                except error_perm:
                    pass
            print(f'[{attempt}] {rel} ({path.stat().st_size})', flush=True)
            with path.open('rb') as fh:
                ftp.storbinary(f'STOR {rel}', fh, blocksize=64 * 1024)
            ftp.quit()
            print('OK', rel, flush=True)
            return
        except Exception as exc:
            print('FAIL', rel, exc, flush=True)
            try:
                if ftp is not None:
                    ftp.close()
            except Exception:
                pass
            time.sleep(attempt)
    raise SystemExit(f'give up on {rel}')

for path in sorted(local.rglob('*')):
    if not path.is_file():
        continue
    rel = str(path.relative_to(local)).replace('\\\\', '/')
    upload_file(rel, path)

ftp = connect()
for name in ('default.php',):
    try:
        ftp.delete(name)
        print('deleted', name)
    except Exception as exc:
        print('skip delete', name, exc)
ftp.quit()
print('UI UPLOAD COMPLETE')
PY"

echo "==> UI deploy finished → https://aisheeba.bejjam.com (ftp://${FTP_HOST}${FTP_REMOTE_DIR})"
