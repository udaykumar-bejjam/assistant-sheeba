#!/usr/bin/env bash
# Full deploy: 1) rsync API to VPS (password SSH)  2) FTP UI dist to UI host
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "========================================"
echo " Sheeba deploy"
echo "  1) API → VPS (rsync + systemd)"
echo "  2) UI  → FTP (vite build + mirror)"
echo "========================================"

"$SCRIPT_DIR/deploy-api.sh"
"$SCRIPT_DIR/deploy-ui.sh"

echo "========================================"
echo " Deploy complete"
echo "========================================"
