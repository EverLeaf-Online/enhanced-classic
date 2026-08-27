#!/usr/bin/env bash
set -euo pipefail
APP_DIR="${APP_DIR:-/opt/everleaf/web}"
BACKUP_ROOT="${BACKUP_ROOT:-/opt/everleaf/backups/web}"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
DEST="$BACKUP_ROOT/$STAMP"
mkdir -p "$DEST"
if [ -f "$APP_DIR/.env" ]; then cp -a "$APP_DIR/.env" "$DEST/.env"; fi
if [ -d "$APP_DIR/data" ]; then cp -a "$APP_DIR/data" "$DEST/data"; fi
find "$BACKUP_ROOT" -mindepth 1 -maxdepth 1 -type d -mtime +14 -exec rm -rf {} + 2>/dev/null || true
echo "$DEST"
