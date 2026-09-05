#!/usr/bin/env bash
set -euo pipefail

SRC="${1:-/home/ubuntu/everleafms copycat}"
OUT="${2:-$HOME/copycat-export-$(date -u +%Y%m%d-%H%M%SZ)}"
SPLIT_SIZE="${SPLIT_SIZE:-1G}"
COMPRESS="${COMPRESS:-0}"

if [[ ! -d "$SRC" ]]; then
  echo "ERROR: source directory not found: $SRC" >&2
  exit 2
fi

SRC="$(readlink -f "$SRC")"
mkdir -p "$OUT"
OUT="$(readlink -f "$OUT")"

case "$OUT/" in
  "$SRC/"*)
    echo "ERROR: output must not be inside the source tree" >&2
    exit 2
    ;;
esac

BASE="$(basename "$SRC")"
PARENT="$(dirname "$SRC")"
STAMP="$(date -u +%Y%m%d-%H%M%SZ)"
PREFIX="$OUT/everleafms-copycat-$STAMP.tar"

if [[ "$COMPRESS" == "1" ]]; then
  PREFIX="$PREFIX.gz"
  echo "Streaming full folder -> gzip -> split ($SPLIT_SIZE parts)"
  tar --format=pax --numeric-owner -C "$PARENT" -cf - "$BASE" \
    | gzip -1 \
    | split -b "$SPLIT_SIZE" -d -a 4 - "$PREFIX.part-"
  MODE="gzip"
else
  echo "Streaming full folder -> split ($SPLIT_SIZE parts)"
  tar --format=pax --numeric-owner -C "$PARENT" -cf - "$BASE" \
    | split -b "$SPLIT_SIZE" -d -a 4 - "$PREFIX.part-"
  MODE="plain"
fi

PARTS=("$PREFIX".part-*)
if [[ ${#PARTS[@]} -eq 0 || ! -e "${PARTS[0]}" ]]; then
  echo "ERROR: no archive parts were created" >&2
  exit 1
fi

(
  cd "$OUT"
  sha256sum "$(basename "$PREFIX")".part-* > "$(basename "$PREFIX").parts.sha256"
)

TOTAL_BYTES=0
for part in "${PARTS[@]}"; do
  bytes=$(stat -c '%s' "$part")
  TOTAL_BYTES=$((TOTAL_BYTES + bytes))
done

cat > "$OUT/ARCHIVE-README.txt" <<EOF
EverLeaf copycat full-folder snapshot
Generated UTC: $STAMP
Source: $SRC
Archive mode: $MODE
Split size: $SPLIT_SIZE
Parts: ${#PARTS[@]}
Total archive bytes: $TOTAL_BYTES

Verify parts:
  cd "$OUT"
  sha256sum -c "$(basename "$PREFIX").parts.sha256"

Restore (plain mode):
  cat "$(basename "$PREFIX")".part-* | tar -xf -

Restore (gzip mode):
  cat "$(basename "$PREFIX")".part-* | gzip -dc | tar -xf -

The source folder was read only. No file from the source was executed or modified.
EOF

printf '\nArchive complete: %s\n' "$OUT"
printf 'Parts: %d\n' "${#PARTS[@]}"
printf 'Total archive bytes: %d\n' "$TOTAL_BYTES"
ls -lh "$OUT"
