#!/usr/bin/env python3
"""Classify EverLeaf event/minigame scripts and fail closed on unsafe activation.

This is deliberately a structural release gate, not a substitute for live gameplay.
It inventories every scripts/event/*.js file, records how it can activate, verifies
that externally referenced event managers exist through the existing linkage model,
and protects dormant/seasonal content from becoming silently time-scheduled.

Dormant scripts are reported rather than guessed into service.  A file being present
in scripts/event means the channel script manager evaluates it at startup; whether it
actually starts work is determined by its init()/scheduler behavior or by an explicit
getEventManager("Name") call from another script.
"""

from __future__ import annotations

import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVENTS = ROOT / "scripts" / "event"
SCRIPTS = ROOT / "scripts"

INIT_RE = re.compile(r"\bfunction\s+init\s*\(")
PQ_RE = re.compile(r"\b(?:var\s+)?isPq\s*=\s*true\b", re.IGNORECASE)
EVENT_REF_RE = re.compile(r"\bgetEventManager\s*\(\s*['\"]([^'\"]+)['\"]\s*\)")
SCHEDULE_RE = re.compile(r"\bem\.schedule\s*\(")
TIMESTAMP_RE = re.compile(r"\bem\.scheduleAtTimestamp\s*\(")
FIXED_RE = re.compile(r"\bem\.scheduleAtFixedRate\s*\(")

# Names are intentionally broad: a seasonal script may remain in the tree for archive
# or GM/manual use, but it must not silently turn itself on through wall-clock timers.
SEASONAL_WORDS = (
    "holiday", "christmas", "xmas", "halloween", "easter", "valentine",
    "anniversary", "2xevent", "rescuegaga",
)

# There are currently no production-approved wall-clock seasonal auto-schedulers.
# Add a script stem here only with an explicit production scheduling decision.
APPROVED_SEASONAL_TIMESTAMP_SCHEDULERS: set[str] = set()

RPS_REQUIRED = {
    ROOT / "src/main/java/server/minigame/RockPaperScissor.java": ("class RockPaperScissor",),
    ROOT / "src/main/java/net/server/channel/handlers/RPSActionHandler.java": ("class RPSActionHandler",),
    ROOT / "src/main/java/net/opcodes/RecvOpcode.java": ("RPS_ACTION",),
    ROOT / "src/main/java/net/opcodes/SendOpcode.java": ("RPS_GAME",),
    ROOT / "src/main/java/constants/id/NpcId.java": ("RPS_ADMIN", "9000019"),
    ROOT / "wz/Npc.wz/9000019.img.xml": ("rpsGame",),
}


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def without_comments(text: str) -> str:
    """Remove JS comments well enough for activation/scheduler detection.

    This intentionally does not try to be a JavaScript parser.  Block comments are the
    important case here because the legacy 2x scheduler is preserved inside one.
    Removing // tails as a second pass prevents commented-out single-line schedulers
    from being counted as active.
    """
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.DOTALL)
    return re.sub(r"//[^\n\r]*", "", text)


def external_references() -> dict[str, list[Path]]:
    refs: dict[str, list[Path]] = defaultdict(list)
    for path in SCRIPTS.rglob("*.js"):
        if path.parent == EVENTS:
            continue
        for manager in EVENT_REF_RE.findall(read(path)):
            refs[manager].append(path.relative_to(ROOT))
    return refs


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []

    if not EVENTS.is_dir():
        print("ERROR scripts/event directory is missing")
        return 1

    event_files = sorted(EVENTS.glob("*.js"), key=lambda p: p.name.lower())
    if not event_files:
        print("ERROR no event scripts found")
        return 1

    names = {p.stem for p in event_files}
    lower_names: dict[str, list[str]] = defaultdict(list)
    for name in names:
        lower_names[name.lower()].append(name)
    for lowered, variants in sorted(lower_names.items()):
        if len(variants) > 1:
            errors.append(f"case-colliding event manager names: {', '.join(sorted(variants))}")

    if "0_EXAMPLE" not in names:
        errors.append("0_EXAMPLE.js fallback is missing")

    refs = external_references()
    for manager, sources in sorted(refs.items()):
        if manager in names:
            continue
        variants = lower_names.get(manager.lower(), [])
        if variants:
            errors.append(
                f"event manager case mismatch: {manager}.js referenced by {sources[0]} "
                f"but repository has {variants[0]}.js"
            )
        else:
            errors.append(f"missing referenced event manager {manager}.js (first reference: {sources[0]})")

    rows: list[dict[str, object]] = []
    for path in event_files:
        raw = read(path)
        active = without_comments(raw)
        stem = path.stem

        if not INIT_RE.search(active):
            errors.append(f"{path.relative_to(ROOT)} has no active init() function")

        referenced = stem in refs
        is_pq = bool(PQ_RE.search(active))
        scheduled = bool(SCHEDULE_RE.search(active) or FIXED_RE.search(active))
        timestamp_scheduled = bool(TIMESTAMP_RE.search(active))
        seasonal = any(word in stem.lower() for word in SEASONAL_WORDS)

        if stem == "0_EXAMPLE":
            classification = "fallback"
        elif seasonal and not referenced and not scheduled and not timestamp_scheduled:
            classification = "seasonal-dormant"
        elif scheduled or timestamp_scheduled:
            classification = "background-scheduled"
        elif is_pq:
            classification = "pq-instance"
        elif referenced:
            classification = "referenced-instance"
        else:
            classification = "dormant-unreferenced"

        if seasonal and timestamp_scheduled and stem not in APPROVED_SEASONAL_TIMESTAMP_SCHEDULERS:
            errors.append(
                f"seasonal script {stem}.js has an active scheduleAtTimestamp call but is not approved for automatic scheduling"
            )

        # Protect the known legacy rate-event script specifically: the file can stay as
        # reference/manual tooling, but the historical hard-coded timestamps must remain inactive.
        if stem == "2xEvent" and timestamp_scheduled:
            errors.append("2xEvent.js historical timestamp scheduler became active")

        rows.append({
            "name": stem,
            "classification": classification,
            "referenced": referenced,
            "reference_count": len(refs.get(stem, [])),
            "is_pq": is_pq,
            "scheduled": scheduled,
            "timestamp_scheduled": timestamp_scheduled,
            "seasonal": seasonal,
        })

    # RPS is a packet/NPC minigame rather than an event-manager script.  Keep its
    # protocol, handler, implementation, NPC id and WZ marker together as one release gate.
    for path, tokens in RPS_REQUIRED.items():
        if not path.is_file():
            errors.append(f"RPS minigame dependency missing: {path.relative_to(ROOT)}")
            continue
        text = read(path)
        for token in tokens:
            if token not in text:
                errors.append(f"RPS minigame dependency {path.relative_to(ROOT)} is missing token {token!r}")

    classes = Counter(str(row["classification"]) for row in rows)
    referenced_distinct = sum(1 for row in rows if row["referenced"])
    pq_count = sum(1 for row in rows if row["is_pq"])
    scheduled_count = sum(1 for row in rows if row["scheduled"] or row["timestamp_scheduled"])
    seasonal_rows = [row for row in rows if row["seasonal"]]
    dormant = [row["name"] for row in rows if row["classification"] in {"dormant-unreferenced", "seasonal-dormant"}]

    print("EverLeaf event/minigame inventory audit")
    print(f"  event scripts: {len(rows)}")
    print(f"  externally referenced managers: {referenced_distinct}")
    print(f"  PQ-labelled scripts: {pq_count}")
    print(f"  scripts with active scheduler calls: {scheduled_count}")
    print("  classifications: " + ", ".join(f"{k}={v}" for k, v in sorted(classes.items())))
    if seasonal_rows:
        print("  seasonal scripts:")
        for row in seasonal_rows:
            print(
                f"    {row['name']}: {row['classification']} "
                f"referenced={row['referenced']} scheduled={row['scheduled']} "
                f"timestamp={row['timestamp_scheduled']}"
            )
    if dormant:
        print("  dormant/unreferenced (report-only, not auto-enabled): " + ", ".join(map(str, dormant)))
    print("  RPS structural dependencies: PRESENT" if not any("RPS" in e for e in errors) else "  RPS structural dependencies: FAILED")

    for warning in warnings:
        print(f"WARNING {warning}")
    if errors:
        for error in errors:
            print(f"ERROR {error}")
        return 1

    print("EverLeaf event/minigame inventory audit: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
