#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 2 || $# -gt 4 ]]; then
  echo "Usage: build-evan-donor-from-zip.sh <Evan.zip> <output-dir> [libwz-dir] [build-dir]" >&2
  exit 2
fi

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
source_zip="$(realpath "$1")"
output_dir="$(mkdir -p "$2" && realpath "$2")"
libwz_dir="${3:-${RUNNER_TEMP:-/tmp}/everleaf-libwz}"
build_dir="${4:-${RUNNER_TEMP:-/tmp}/everleaf-evan-xml-build}"
source_sha='961e0cbf826aca48efa619afec51fd12c2472a82e654e6e73542b5bf65a0e5ce'
libwz_commit='41cd5d62ecd229f0eb425c2654ecf0bf8b435d7f'

[[ -s "$source_zip" ]] || { echo "Missing Evan source archive: $source_zip" >&2; exit 3; }
printf '%s  %s\n' "$source_sha" "$source_zip" | sha256sum --check --strict

extract_dir="$(mktemp -d "${RUNNER_TEMP:-/tmp}/everleaf-evan-source.XXXXXX")"
cleanup() { rm -rf "$extract_dir"; }
trap cleanup EXIT
unzip -q "$source_zip" -d "$extract_dir"

python3 - "$extract_dir" <<'PY'
from pathlib import Path
from collections import Counter
import sys
import xml.etree.ElementTree as ET

root = Path(sys.argv[1])
actual = {
    p.relative_to(root).as_posix()
    for p in root.rglob('*')
    if p.is_file()
}

skill_stages = ['2001', '2200', '2210', '2211', '2212', '2213', '2214', '2215', '2216', '2217', '2218']
dragon_skill_stages = ['2200', '2210', '2211', '2212', '2213', '2214', '2215', '2216', '2217', '2218']
dragon_character_ids = [
    f'019{family}{variant:03d}'
    for family in (42, 52, 62, 72)
    for variant in range(5)
]

expected = {
    'Evan/Character/00002000.img.xml',
    *{f'Evan/Character/Dragon/{image}.img.xml' for image in dragon_character_ids},
    *{f'Evan/Skill/{stage}.img.xml' for stage in skill_stages},
    *{f'Evan/Skill/Dragon/{stage}.img.xml' for stage in dragon_skill_stages},
    'Evan/String/Skill.img.xml',
    'Evan/UI/Basic.img.xml',
    'Evan/UI/UIWindow.img.xml',
}

assert len(expected) == 45, f'Internal Evan source contract is wrong: expected set has {len(expected)} files'
assert actual == expected, (
    'Evan source archive layout differs from the pinned contract: '
    f'missing={sorted(expected - actual)} extra={sorted(actual - expected)}'
)

supported_tags = {'imgdir', 'canvas', 'int', 'short', 'string', 'vector', 'uol'}
tag_counts = Counter()
canvas_count = 0
missing_basedata = []

for relative in sorted(expected):
    path = root / relative
    assert path.stat().st_size > 0, f'Empty Evan source entry: {relative}'
    xml_root = ET.parse(path).getroot()
    assert xml_root.tag == 'imgdir', f'Unexpected XML root in {relative}: {xml_root.tag}'
    for node in xml_root.iter():
        tag_counts[node.tag] += 1
        assert node.tag in supported_tags, f'Unsupported Evan XML tag {node.tag!r} in {relative}'
        if node.tag == 'canvas':
            canvas_count += 1
            if not node.get('basedata'):
                missing_basedata.append(relative)

assert canvas_count == 8400, f'Expected 8400 Evan canvases, found {canvas_count}'
assert not missing_basedata, f'Canvas nodes missing basedata: {sorted(set(missing_basedata))}'
print('Authorized Evan source archive layout/schema: PASS')
print(f'Evan source files={len(actual)} canvases={canvas_count} tags={dict(sorted(tag_counts.items()))}')
PY

if [[ ! -d "$libwz_dir/.git" ]]; then
  rm -rf "$libwz_dir"
  git clone --quiet https://github.com/toyobayashi/libwz.git "$libwz_dir"
fi
git -C "$libwz_dir" fetch --quiet origin "$libwz_commit"
git -C "$libwz_dir" checkout --quiet --detach "$libwz_commit"
git -C "$libwz_dir" submodule update --init --recursive --quiet
[[ "$(git -C "$libwz_dir" rev-parse HEAD)" == "$libwz_commit" ]] || {
  echo 'Pinned libwz checkout mismatch' >&2
  exit 4
}

rm -rf "$build_dir"
cmake -S "$repo_root/client/tools/evan-xml-donor-builder" -B "$build_dir" \
  -DLIBWZ_SOURCE="$libwz_dir" \
  -DCMAKE_BUILD_TYPE=Release >/dev/null
cmake --build "$build_dir" --config Release --parallel 2 >/dev/null

builder="$build_dir/everleaf-evan-xml-donor-builder"
if [[ ! -x "$builder" && -x "$build_dir/Release/everleaf-evan-xml-donor-builder" ]]; then
  builder="$build_dir/Release/everleaf-evan-xml-donor-builder"
fi
[[ -x "$builder" ]] || { echo 'Evan XML donor builder binary was not produced' >&2; exit 5; }

stage="$(mktemp -d "${RUNNER_TEMP:-/tmp}/everleaf-evan-donor.XXXXXX")"
"$builder" "$extract_dir/Evan" "$stage"

rm -rf "$output_dir"/*
for wz in Skill Character UI String; do
  [[ -s "$stage/$wz.wz" ]] || { echo "Missing generated donor $wz.wz" >&2; exit 6; }
  mv "$stage/$wz.wz" "$output_dir/$wz.wz"
  sha256sum "$output_dir/$wz.wz"
done
rm -rf "$stage"
chmod 600 "$output_dir"/*.wz

echo 'EverLeaf Evan source ZIP -> donor WZ build: PASS'
