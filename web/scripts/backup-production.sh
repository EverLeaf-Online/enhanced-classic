#!/usr/bin/env bash
set -euo pipefail
umask 077

APP_DIR="${APP_DIR:-/opt/everleaf/web}"
BACKUP_ROOT="${BACKUP_ROOT:-/opt/everleaf/backups/web}"
BACKUP_ROOT="$(realpath -m "$BACKUP_ROOT")"
case "$BACKUP_ROOT" in
  /opt/everleaf/backups/*) ;;
  *) echo 'Backup root must stay below /opt/everleaf/backups.' >&2; exit 2 ;;
esac

STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
DEST="$BACKUP_ROOT/$STAMP"
install -d -m 700 "$BACKUP_ROOT" "$DEST"
test -s "$APP_DIR/.env"
install -m 600 "$APP_DIR/.env" "$DEST/.env"

node "$APP_DIR/scripts/backup-cms.js" \
  "$APP_DIR" "$APP_DIR/.env" "$DEST/cms.sqlite"
node "$APP_DIR/scripts/backup-mysql.js" \
  "$APP_DIR/.env" "$DEST/game-mysql.sql.gz"

test -s "$DEST/cms.sqlite"
test -s "$DEST/game-mysql.sql.gz"
gzip -t "$DEST/game-mysql.sql.gz"
(
  cd "$DEST"
  sha256sum cms.sqlite game-mysql.sql.gz > SHA256SUMS
)
printf 'created_utc=%s\n' "$STAMP" > "$DEST/backup.properties"
chmod 600 "$DEST"/*

find "$BACKUP_ROOT" -mindepth 1 -maxdepth 1 -type d -mtime +14 -exec rm -rf {} + 2>/dev/null || true
echo "$DEST"
