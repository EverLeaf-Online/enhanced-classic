#!/usr/bin/env python3
"""Audit release-facing Quest.wz scripted handlers against scripts/quest.

Runtime semantics:
* only ``startscript``/``endscript`` map to QuestRequirementType.SCRIPT;
* ScriptRequirement is enabled only by a non-empty string value;
* classic QuestlineFetcher treats a start-phase ``end`` requirement as
  limited/expired event content rather than normal release progression.

Hard failures are therefore limited to non-limited quests whose owner NPC is
spawned in the active world. Limited-time and unspawned quest scripts remain
visible as review findings instead of blocking every release.
"""
from __future__ import annotations

import json
import re
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECK = ROOT / "wz" / "Quest.wz" / "Check.img.xml"
MAP_ROOT = ROOT / "wz" / "Map.wz" / "Map"
SCRIPT_ROOT = ROOT / "scripts" / "quest"
NUMERIC_SCRIPT_RE = re.compile(r"^(\d+)\.js$")
START_RE = re.compile(r"\bfunction\s+start\s*\(")
END_RE = re.compile(r"\bfunction\s+end\s*\(")


def norm(value: str | None) -> str:
    raw = (value or "").strip()
    if raw.lstrip("-").isdigit():
        return str(int(raw))
    return raw


def parse(path: Path) -> ET.Element:
    return ET.parse(path).getroot()


def direct_value(node: ET.Element, name: str) -> str | None:
    for child in node:
        if child.attrib.get("name") == name:
            return child.attrib.get("value")
    return None


def phase(node: ET.Element, phase_name: str) -> ET.Element | None:
    return next(
        (child for child in node if child.tag == "imgdir" and child.attrib.get("name") == phase_name),
        None,
    )


def quest_nodes() -> dict[str, ET.Element]:
    result: dict[str, ET.Element] = {}
    for node in parse(CHECK):
        if node.tag != "imgdir":
            continue
        qid = norm(node.attrib.get("name"))
        if qid.isdigit():
            result[qid] = node
    return result


def phase_script_requirement(node: ET.Element, phase_name: str) -> bool:
    p = phase(node, phase_name)
    if p is None:
        return False
    expected_name = "startscript" if phase_name == "0" else "endscript"
    value = direct_value(p, expected_name)
    return value is not None and value.strip() != ""


def is_limited_quest(node: ET.Element) -> bool:
    """Mirror classic QuestlineFetcher: start-phase `end` marks event content."""
    p = phase(node, "0")
    return p is not None and direct_value(p, "end") is not None


def owners(node: ET.Element) -> set[str]:
    result: set[str] = set()
    for p in node:
        if p.tag != "imgdir":
            continue
        npc = norm(direct_value(p, "npc"))
        if npc.isdigit() and int(npc) > 0:
            result.add(npc)
    return result


def active_npcs() -> set[str]:
    result: set[str] = set()
    for path in MAP_ROOT.glob("Map*/*.img.xml"):
        root = parse(path)
        life = next(
            (child for child in root if child.tag == "imgdir" and child.attrib.get("name") == "life"),
            None,
        )
        if life is None:
            continue
        for entry in life:
            if entry.tag != "imgdir" or norm(direct_value(entry, "type")) != "n":
                continue
            npc = norm(direct_value(entry, "id"))
            if npc.isdigit() and int(npc) > 0:
                result.add(npc)
    return result


def is_medal_fallback(qid: str) -> bool:
    return qid.isdigit() and 29900 <= int(qid) <= 29999


def script_contract(path: Path) -> tuple[bool, bool]:
    text = path.read_text(encoding="utf-8", errors="replace")
    return bool(START_RE.search(text)), bool(END_RE.search(text))


def main() -> int:
    emit_json = "--json" in sys.argv
    failures: list[str] = []
    reviews: list[str] = []
    try:
        quests = quest_nodes()
        spawned_npcs = active_npcs()
    except (ET.ParseError, OSError) as exc:
        print(f"ERROR scripted quest audit setup failed: {exc}")
        return 1

    medal_fallback = SCRIPT_ROOT / "medalQuest.js"
    if not medal_fallback.is_file():
        failures.append("Generic medal quest fallback scripts/quest/medalQuest.js is missing")
    else:
        start_ok, end_ok = script_contract(medal_fallback)
        if not start_ok or not end_ok:
            failures.append("medalQuest.js must expose both start(...) and end(...)")

    active_scripted: dict[str, set[str]] = defaultdict(set)
    review_scripted: dict[str, set[str]] = defaultdict(set)
    limited_scripted: set[str] = set()
    required_script_ids: set[str] = set()

    for qid, node in quests.items():
        phases: set[str] = set()
        if phase_script_requirement(node, "0"):
            phases.add("start")
        if phase_script_requirement(node, "1"):
            phases.add("end")
        if not phases:
            continue

        required_script_ids.add(qid)
        limited = is_limited_quest(node)
        spawned = bool(owners(node) & spawned_npcs)
        is_active = spawned and not limited
        if is_active:
            active_scripted[qid].update(phases)
        else:
            review_scripted[qid].update(phases)
            if limited:
                limited_scripted.add(qid)

        script_path = SCRIPT_ROOT / f"{qid}.js"
        fallback = is_medal_fallback(qid)
        if not script_path.is_file():
            if fallback:
                continue
            message = f"Quest {qid} requires scripted {','.join(sorted(phases))} phase(s) but {qid}.js is missing"
            if is_active:
                failures.append(message)
            else:
                prefix = "Limited/event" if limited else "Dormant"
                reviews.append(f"{prefix} {message.lower()}")
            continue

        has_start, has_end = script_contract(script_path)
        if "start" in phases and not has_start:
            message = f"Quest {qid} has scripted start requirement but {qid}.js has no start(...) function"
            if is_active:
                failures.append(message)
            else:
                reviews.append(("Limited/event " if limited else "Dormant ") + message.lower())
        if "end" in phases and not has_end:
            message = f"Quest {qid} has scripted end requirement but {qid}.js has no end(...) function"
            if is_active:
                failures.append(message)
            else:
                reviews.append(("Limited/event " if limited else "Dormant ") + message.lower())

    numeric_scripts = {
        norm(match.group(1))
        for path in SCRIPT_ROOT.glob("*.js")
        if (match := NUMERIC_SCRIPT_RE.match(path.name))
    }
    orphan_scripts = sorted(numeric_scripts - set(quests), key=int)
    unused_numeric_scripts = sorted(numeric_scripts - required_script_ids, key=int)
    if orphan_scripts:
        reviews.append(
            f"{len(orphan_scripts)} numeric quest scripts have no Check.wz quest: "
            + ", ".join(orphan_scripts[:25]) + (" ..." if len(orphan_scripts) > 25 else "")
        )
    if unused_numeric_scripts:
        reviews.append(
            f"{len(unused_numeric_scripts)} numeric quest scripts exist without a current SCRIPT requirement: "
            + ", ".join(unused_numeric_scripts[:25]) + (" ..." if len(unused_numeric_scripts) > 25 else "")
        )

    payload = {
        "activeScriptedQuestCount": len(active_scripted),
        "reviewScriptedQuestCount": len(review_scripted),
        "limitedScriptedQuestCount": len(limited_scripted),
        "numericQuestScriptCount": len(numeric_scripts),
        "activeScripted": {qid: sorted(phases) for qid, phases in sorted(active_scripted.items(), key=lambda p: int(p[0]))},
        "reviewScripted": {qid: sorted(phases) for qid, phases in sorted(review_scripted.items(), key=lambda p: int(p[0]))},
        "orphanScripts": orphan_scripts,
        "unusedNumericScripts": unused_numeric_scripts,
        "reviews": reviews,
        "failures": failures,
    }
    if emit_json:
        print(json.dumps(payload, indent=2))
    else:
        print(
            f"Quest script audit: {len(active_scripted)} release-facing / "
            f"{len(review_scripted)} review-only ({len(limited_scripted)} limited/event) / "
            f"{len(numeric_scripts)} numeric JS files"
        )
        for line in reviews:
            print(f"[REVIEW] {line}")
        for line in failures:
            print(f"[FAIL] {line}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
