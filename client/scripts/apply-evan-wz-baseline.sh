#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat >&2 <<'EOF'
Usage: apply-evan-wz-baseline.sh <full-client-dir> <donor-dir> [libwz-dir] [build-dir]

Patches the managed v83 full-client Skill.wz, Character.wz, UI.wz and String.wz
with the narrow Evan donor manifests in client/evan-wz. The donor WZs are never
copied wholesale into the client and must all exist before any destination WZ
is replaced.
EOF
  exit 2
}

[[ $# -ge 2 && $# -le 4 ]] || usage

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
full_client="$(realpath "$1")"
donor_dir="$(realpath "$2")"
libwz_dir="${3:-${RUNNER_TEMP:-/tmp}/everleaf-libwz}"
build_dir="${4:-${RUNNER_TEMP:-/tmp}/everleaf-evan-wz-build}"
libwz_commit="41cd5d62ecd229f0eb425c2654ecf0bf8b435d7f"

[[ -d "$full_client" ]] || { echo "Missing full-client directory: $full_client" >&2; exit 3; }
[[ -d "$donor_dir" ]] || { echo "Missing authorized Evan donor directory: $donor_dir" >&2; exit 4; }

wz_names=(Skill Character UI String)
for name in "${wz_names[@]}"; do
  [[ -s "$full_client/$name.wz" ]] || { echo "Missing base WZ: $full_client/$name.wz" >&2; exit 5; }
  [[ -s "$donor_dir/$name.wz" ]] || { echo "Missing authorized donor WZ: $donor_dir/$name.wz" >&2; exit 6; }
  [[ -s "$repo_root/client/evan-wz/$name.copy.txt" ]] || { echo "Missing Evan copy manifest: $name" >&2; exit 7; }
done

if [[ ! -d "$libwz_dir/.git" ]]; then
  rm -rf "$libwz_dir"
  git clone --quiet https://github.com/toyobayashi/libwz.git "$libwz_dir"
fi
git -C "$libwz_dir" fetch --quiet origin "$libwz_commit"
git -C "$libwz_dir" checkout --quiet --detach "$libwz_commit"
git -C "$libwz_dir" submodule update --init --recursive --quiet
[[ "$(git -C "$libwz_dir" rev-parse HEAD)" == "$libwz_commit" ]] || {
  echo "Pinned libwz checkout mismatch" >&2
  exit 8
}

rm -rf "$build_dir"
cmake -S "$repo_root/client/tools/evan-wz-patcher" -B "$build_dir" \
  -DLIBWZ_SOURCE="$libwz_dir" \
  -DCMAKE_BUILD_TYPE=Release >/dev/null
cmake --build "$build_dir" --config Release --parallel 2 >/dev/null

patcher="$build_dir/everleaf-evan-wz-patcher"
if [[ ! -x "$patcher" && -x "$build_dir/Release/everleaf-evan-wz-patcher" ]]; then
  patcher="$build_dir/Release/everleaf-evan-wz-patcher"
fi
[[ -x "$patcher" ]] || { echo "Evan WZ patcher binary was not produced" >&2; exit 9; }

stage_dir="$(mktemp -d "${RUNNER_TEMP:-/tmp}/everleaf-evan-wz.XXXXXX")"
cleanup() { rm -rf "$stage_dir"; }
trap cleanup EXIT

# Build all four patched WZs first. No managed destination is replaced unless
# every donor file parsed and every required Evan node was found successfully.
for name in "${wz_names[@]}"; do
  "$patcher" \
    "$full_client/$name.wz" 83 \
    "$donor_dir/$name.wz" 84 \
    "$repo_root/client/evan-wz/$name.copy.txt" \
    "$stage_dir/$name.wz"
  [[ -s "$stage_dir/$name.wz" ]] || { echo "Patched $name.wz is empty" >&2; exit 10; }
done

for name in "${wz_names[@]}"; do
  before="$(sha256sum "$full_client/$name.wz" | awk '{print $1}')"
  after="$(sha256sum "$stage_dir/$name.wz" | awk '{print $1}')"
  [[ "$before" != "$after" ]] || { echo "Evan patch made no change to $name.wz" >&2; exit 11; }
  mv "$stage_dir/$name.wz" "$full_client/$name.wz"
  printf 'Evan WZ patched: %s.wz %s -> %s\n' "$name" "$before" "$after"
done

echo "EverLeaf Evan full-baseline WZ integration: PASS"
