#!/usr/bin/env bash
# Run the USBIP GUI server. Must be started with sufficient privileges
# (root or with a sudoers rule for the usbip commands).
set -euo pipefail

cd "$(dirname "$0")/src"
exec uvicorn main:app \
  --host "${USBIPGUI_HOST:-0.0.0.0}" \
  --port "${USBIPGUI_PORT:-8000}" \
  --log-level "${USBIPGUI_LOG_LEVEL:-info}" \
  "$@"
