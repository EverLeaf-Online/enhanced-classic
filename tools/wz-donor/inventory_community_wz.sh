#!/usr/bin/env bash
set -euo pipefail

COMMUNITY_WZ_ROOT="${COMMUNITY_WZ_ROOT:-/home/ubuntu/everleaf-staging/community-wz/extracted/Community Repack WZs}"
CURRENT_PATCH_ROOT="${CURRENT_PATCH_ROOT:-/opt/everleaf/patches/files}"

echo '=== COMMUNITY WZ ROOT ==='
test -d "$COMMUNITY_WZ_ROOT"
find "$COMMUNITY_WZ_ROOT" -maxdepth 1 -type f -iname '*.wz' -printf '%f\t%s\n' | sort

echo
echo '=== COMMUNITY SHA256 ==='
find "$COMMUNITY_WZ_ROOT" -maxdepth 1 -type f -iname '*.wz' -print0 | sort -z | xargs -0 sha256sum

echo
echo '=== CURRENT LAUNCHER WZ FILES ==='
if [ -d "$CURRENT_PATCH_ROOT" ]; then
  find "$CURRENT_PATCH_ROOT" -maxdepth 3 -type f -iname '*.wz' -printf '%p\t%s\n' | sort
fi

echo
echo '=== CURRENT LAUNCHER SHA256 ==='
if [ -d "$CURRENT_PATCH_ROOT" ]; then
  find "$CURRENT_PATCH_ROOT" -maxdepth 3 -type f -iname '*.wz' -print0 | sort -z | xargs -0 -r sha256sum
fi

echo
echo '=== DISK ==='
df -h /
