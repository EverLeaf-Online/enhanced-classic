#!/usr/bin/env python3
"""Compare the metadata-only 2026-09-05 copycat WZ reference to Cosmic.

This script never reads or publishes donor WZ bytes. It exists to keep selective
content migration grounded in exact file identity rather than filenames alone.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
COSMIC = ROOT / "client" / "cosmic-wz-baseline.json"
COPYCAT = ROOT / "client" / "copycat-wz-reference.json"

SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
CRITICAL = {
    "Character.wz", "Etc.wz", "Item.wz", "Map.wz", "Mob.wz", "Npc.wz",
    "Quest.wz", "Reactor.wz", "Skill.wz", "String.wz", "UI.wz",
}


def load(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if value.get("schemaVersion") != 1:
        raise SystemExit(f"Unsupported schema in {path}")
    return value


def index_files(document: dict, label: str) -> dict[str, dict]:
    result: dict[str, dict] = {}
    for entry in document.get("files", []):
        path = entry.get("path")
        size = entry.get("size")
        digest = entry.get("sha256", "")
        if not isinstance(path, str) or not path.endswith(".wz"):
            raise SystemExit(f"Invalid {label} WZ path: {path!r}")
        if path in result:
            raise SystemExit(f"Duplicate {label} WZ path: {path}")
        if not isinstance(size, int) or size <= 0:
            raise SystemExit(f"Invalid {label} size for {path}: {size!r}")
        if not isinstance(digest, str) or not SHA256_RE.fullmatch(digest):
            raise SystemExit(f"Invalid {label} SHA-256 for {path}: {digest!r}")
        result[path] = entry
    return result


cosmic = index_files(load(COSMIC), "Cosmic")
copycat_document = load(COPYCAT)
if copycat_document.get("distributionPolicy") != "metadata-only; raw donor WZ files are not committed or published":
    raise SystemExit("Copycat reference must remain metadata-only")
copycat = index_files(copycat_document, "copycat")

missing = sorted(CRITICAL - copycat.keys())
if missing:
    raise SystemExit(f"Copycat reference is missing critical WZ metadata: {missing}")

common = sorted(cosmic.keys() & copycat.keys())
identical = [name for name in common if cosmic[name]["sha256"] == copycat[name]["sha256"]]

print("# Cosmic vs copycat WZ metadata comparison")
print()
print(f"Cosmic entries: {len(cosmic)}")
print(f"Copycat entries: {len(copycat)}")
print(f"Common entries: {len(common)}")
print(f"Byte-identical common entries: {len(identical)}")
print()
print("| WZ | Cosmic bytes | Copycat bytes | Ratio | Same SHA-256 |")
print("|---|---:|---:|---:|:---:|")
for name in common:
    old = cosmic[name]
    new = copycat[name]
    ratio = new["size"] / old["size"]
    same = "yes" if old["sha256"] == new["sha256"] else "no"
    print(f"| {name} | {old['size']:,} | {new['size']:,} | {ratio:.2f}x | {same} |")

print()
print("Reference-only entries not present in the pinned Cosmic manifest:")
for name in sorted(copycat.keys() - cosmic.keys()):
    entry = copycat[name]
    print(f"- {name}: {entry['size']:,} bytes, {entry['sha256']}")

# The audit established a fundamentally different donor set. If a future edit
# accidentally replaces this reference with Cosmic hashes, fail rather than
# silently presenting the donor as newer content.
if identical:
    raise SystemExit(f"Unexpected byte-identical Cosmic/copycat WZ entries: {identical}")

print()
print("Copycat WZ reference comparison: PASS (metadata only; no promotion performed)")
