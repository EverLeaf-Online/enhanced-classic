#!/usr/bin/env python3
"""Audit script -> event-manager linkage used by bosses, PQs and transports.

The scripting API resolves getEventManager("Name") to scripts/event/Name.js.  A
missing or case-mismatched file is a runtime failure that static Java tests do
not catch, so keep this as a release gate.

Empress-development paths are intentionally excluded from EverLeaf release QA.
"""

from __future__ import annotations

import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
EVENTS = SCRIPTS / "event"
REF_RE = re.compile(r"\bgetEventManager\s*\(\s*['\"]([^'\"]+)['\"]\s*\)")

# Useful operational labels only; linkage validation itself is generic and does
# not depend on exact upstream file names.
BOSS_WORDS = ("zak", "horntail", "hontale", "pink", "pap", "krexel", "scar", "targa", "cwk", "boss")
PQ_WORDS = ("pq", "kerning", "ludi", "orbis", "ellin", "pirate", "romeo", "juliet", "guild")


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def release_script(path: Path) -> bool:
    return "empress" not in str(path).lower()


def main() -> int:
    if not EVENTS.is_dir():
        print("ERROR scripts/event directory is missing")
        return 1

    event_files = {p.name: p for p in EVENTS.glob("*.js") if release_script(p)}
    lower_to_names: dict[str, list[str]] = defaultdict(list)
    for name in event_files:
        lower_to_names[name.lower()].append(name)

    references: list[tuple[Path, str]] = []
    for path in SCRIPTS.rglob("*.js"):
        if path.parent == EVENTS or not release_script(path):
            continue
        for name in REF_RE.findall(read(path)):
            references.append((path, name))

    missing: list[tuple[Path, str]] = []
    case_mismatch: list[tuple[Path, str, str]] = []
    empty: list[tuple[Path, str]] = []
    referenced_names: set[str] = set()

    for source, manager in references:
        expected = manager + ".js"
        referenced_names.add(expected)
        if expected in event_files:
            if not read(event_files[expected]).strip():
                empty.append((source, manager))
            continue
        alternatives = lower_to_names.get(expected.lower(), [])
        if alternatives:
            case_mismatch.append((source, manager, alternatives[0]))
        else:
            missing.append((source, manager))

    if missing or case_mismatch or empty:
        for source, manager in missing:
            print(f"ERROR missing event manager {manager}.js referenced by {source.relative_to(ROOT)}")
        for source, manager, actual in case_mismatch:
            print(
                f"ERROR event manager case mismatch: {source.relative_to(ROOT)} references "
                f"{manager}.js but repository has {actual}"
            )
        for source, manager in empty:
            print(f"ERROR empty event manager {manager}.js referenced by {source.relative_to(ROOT)}")
        return 1

    boss_refs = sorted(
        n[:-3] for n in referenced_names if any(word in n.lower() for word in BOSS_WORDS)
    )
    pq_refs = sorted(
        n[:-3] for n in referenced_names if any(word in n.lower() for word in PQ_WORDS)
    )

    print("EverLeaf event-manager linkage audit: PASS")
    print(f"  Event scripts available: {len(event_files)}")
    print(f"  Literal getEventManager references checked: {len(references)}")
    print(f"  Distinct referenced event managers: {len(referenced_names)}")
    print(f"  Boss-labelled managers observed: {len(boss_refs)}")
    print(f"  PQ-labelled managers observed: {len(pq_refs)}")
    if boss_refs:
        print("  Boss managers: " + ", ".join(boss_refs[:24]))
    if pq_refs:
        print("  PQ managers: " + ", ".join(pq_refs[:24]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
