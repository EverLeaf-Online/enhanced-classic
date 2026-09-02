#!/usr/bin/env python3
"""Release-facing quest gameplay completeness audit for EverLeaf.

Complements the existing structural quest audits with checks tied to the
remaining gameplay checklist:
- item and mob/kill counter shape and quantity safety
- repeatable quest interval validity
- item reward/removal quantity safety, including Java short boundaries
- start-phase rewards that deserve abandon/restart exploit review
- active quest owner reachability classification

This audit is deliberately conservative. Structural/runtime-impossible data is
a hard failure. Potential abandon/restart reward surfaces are review findings
because many retail quests intentionally restore quest items when restarted.
"""
from __future__ import annotations

import json
import re
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QUEST_ROOT = ROOT / "wz" / "Quest.wz"
CHECK = QUEST_ROOT / "Check.img.xml"
ACT = QUEST_ROOT / "Act.img.xml"
MAP_ROOT = ROOT / "wz" / "Map.wz" / "Map"
ITEM_ROOT = ROOT / "wz" / "Item.wz"
CHAR_ROOT = ROOT / "wz" / "Character.wz"
MOB_ROOT = ROOT / "wz" / "Mob.wz"
NUMERIC_FILE = re.compile(r"^(\d+)\.img\.xml$")
SHORT_MIN = -32768
SHORT_MAX = 32767
INT_MIN = -(2**31)
INT_MAX = 2**31 - 1


@dataclass(frozen=True)
class Finding:
    severity: str
    code: str
    quest_id: str
    phase: str
    detail: str


def norm(value: str | None) -> str:
    raw = (value or "").strip()
    if raw.lstrip("-").isdigit():
        return str(int(raw))
    return raw


def direct_value(node: ET.Element, name: str) -> str | None:
    for child in node:
        if child.attrib.get("name") == name:
            return child.attrib.get("value")
    return None


def direct_group(node: ET.Element, name: str) -> ET.Element | None:
    return next((child for child in node if child.tag == "imgdir" and child.attrib.get("name") == name), None)


def parse_quest_nodes(path: Path) -> dict[str, ET.Element]:
    result: dict[str, ET.Element] = {}
    for node in ET.parse(path).getroot():
        if node.tag != "imgdir":
            continue
        qid = norm(node.attrib.get("name"))
        if qid.isdigit():
            result[qid] = node
    return result


def spawned_npcs() -> set[str]:
    result: set[str] = set()
    for path in MAP_ROOT.glob("Map*/*.img.xml"):
        root = ET.parse(path).getroot()
        life = direct_group(root, "life")
        if life is None:
            continue
        for entry in life:
            if entry.tag != "imgdir" or norm(direct_value(entry, "type")) != "n":
                continue
            npc_id = norm(direct_value(entry, "id"))
            if npc_id.isdigit() and int(npc_id) > 0:
                result.add(npc_id)
    return result


def quest_owners(node: ET.Element) -> set[str]:
    result: set[str] = set()
    for phase in node:
        if phase.tag != "imgdir":
            continue
        npc = norm(direct_value(phase, "npc"))
        if npc.isdigit() and int(npc) > 0:
            result.add(npc)
    return result


def index_items() -> set[str]:
    result: set[str] = set()
    for path in CHAR_ROOT.rglob("*.img.xml"):
        match = NUMERIC_FILE.match(path.name)
        if match:
            iid = norm(match.group(1))
            if iid.isdigit() and 1_000_000 <= int(iid) < 2_000_000:
                result.add(iid)
    for path in ITEM_ROOT.rglob("*.img.xml"):
        try:
            root = ET.parse(path).getroot()
        except ET.ParseError:
            continue
        root_name = (root.attrib.get("name") or "").removesuffix(".img")
        iid = norm(root_name)
        if iid.isdigit() and int(iid) >= 2_000_000:
            result.add(iid)
        for child in root:
            if child.tag == "imgdir":
                iid = norm(child.attrib.get("name"))
                if iid.isdigit() and int(iid) >= 2_000_000:
                    result.add(iid)
    return result


def index_mobs() -> set[str]:
    result: set[str] = set()
    for path in MOB_ROOT.rglob("*.img.xml"):
        match = NUMERIC_FILE.match(path.name)
        if match:
            result.add(norm(match.group(1)))
    return result


def parse_int(raw: str | None) -> int | None:
    value = norm(raw)
    return int(value) if value.lstrip("-").isdigit() else None


def add(hard: list[Finding], review: list[Finding], release_facing: bool, code: str, qid: str, phase: str, detail: str) -> None:
    target = hard if release_facing else review
    severity = "FAIL" if release_facing else "REVIEW"
    target.append(Finding(severity, code, qid, phase, detail))


def main() -> int:
    emit_json = "--json" in sys.argv
    hard: list[Finding] = []
    review: list[Finding] = []
    counts: Counter[str] = Counter()

    try:
        checks = parse_quest_nodes(CHECK)
        acts = parse_quest_nodes(ACT)
        live_npcs = spawned_npcs()
        item_ids = index_items()
        mob_ids = index_mobs()
    except (ET.ParseError, OSError) as exc:
        print(f"quest gameplay audit setup failed: {exc}", file=sys.stderr)
        return 2

    active = {qid for qid, node in checks.items() if quest_owners(node) & live_npcs}
    counts["check_quests"] = len(checks)
    counts["active_quests"] = len(active)

    for qid, qnode in sorted(checks.items(), key=lambda pair: int(pair[0])):
        release_facing = qid in active
        for phase in qnode:
            if phase.tag != "imgdir" or phase.attrib.get("name") not in {"0", "1"}:
                continue
            phase_name = "start" if phase.attrib.get("name") == "0" else "complete"

            interval_node = next((c for c in phase if c.attrib.get("name") == "interval"), None)
            if interval_node is not None:
                counts["repeat_intervals"] += 1
                interval = parse_int(interval_node.attrib.get("value"))
                if interval is None:
                    add(hard, review, release_facing, "invalid_repeat_interval", qid, phase_name, "interval is non-numeric")
                elif interval <= 0:
                    add(hard, review, release_facing, "nonpositive_repeat_interval", qid, phase_name, f"interval={interval} minutes")
                elif interval > INT_MAX:
                    add(hard, review, release_facing, "repeat_interval_overflow", qid, phase_name, f"interval={interval} exceeds Java int")

            for group_name in ("item", "mob"):
                group = direct_group(phase, group_name)
                if group is None:
                    continue
                for entry in group:
                    if entry.tag != "imgdir":
                        continue
                    object_id = norm(direct_value(entry, "id"))
                    count = parse_int(direct_value(entry, "count"))
                    counts[f"{group_name}_counter_entries"] += 1
                    if not object_id.isdigit() or int(object_id) <= 0:
                        add(hard, review, release_facing, f"invalid_{group_name}_counter_id", qid, phase_name, f"id={object_id!r}")
                        continue
                    if group_name == "item" and object_id not in item_ids:
                        add(hard, review, release_facing, "missing_item_counter_asset", qid, phase_name, f"item {object_id} is absent from item data")
                    if group_name == "mob" and object_id not in mob_ids:
                        add(hard, review, release_facing, "missing_mob_counter_asset", qid, phase_name, f"mob/group {object_id} is absent from Mob.wz")
                    if count is None:
                        add(hard, review, release_facing, f"invalid_{group_name}_counter_count", qid, phase_name, f"{object_id} count is missing/non-numeric")
                    elif count < INT_MIN or count > INT_MAX:
                        add(hard, review, release_facing, f"{group_name}_counter_overflow", qid, phase_name, f"{object_id} count={count}")
                    elif group_name == "mob" and count <= 0:
                        review.append(Finding("REVIEW", "nonpositive_mob_counter", qid, phase_name, f"mob/group {object_id} count={count}; verify intentional"))

    for qid, anode in sorted(acts.items(), key=lambda pair: int(pair[0])):
        release_facing = qid in active
        for phase in anode:
            if phase.tag != "imgdir" or phase.attrib.get("name") not in {"0", "1"}:
                continue
            is_start = phase.attrib.get("name") == "0"
            phase_name = "start" if is_start else "complete"
            item_group = direct_group(phase, "item")
            if item_group is not None:
                for entry in item_group:
                    if entry.tag != "imgdir":
                        continue
                    item_id = norm(direct_value(entry, "id"))
                    count = parse_int(direct_value(entry, "count"))
                    if count is None:
                        count = 1
                    counts["item_action_entries"] += 1
                    if not item_id.isdigit() or int(item_id) <= 0:
                        add(hard, review, release_facing, "invalid_item_action_id", qid, phase_name, f"id={item_id!r}")
                        continue
                    if item_id not in item_ids:
                        add(hard, review, release_facing, "missing_item_action_asset", qid, phase_name, f"item {item_id} is absent from item data")
                    if count < SHORT_MIN or count > SHORT_MAX:
                        add(hard, review, release_facing, "item_action_short_overflow", qid, phase_name, f"item {item_id} count={count} exceeds runtime short quantity")
                    if count == 0:
                        review.append(Finding("REVIEW", "zero_item_action", qid, phase_name, f"item {item_id} has zero reward/removal count"))
                    if is_start and count > 0 and release_facing:
                        review.append(Finding("REVIEW", "restart_reward_surface", qid, phase_name, f"start action grants {count}x item {item_id}; verify forfeit/restart cannot duplicate unintended value"))

            for scalar_name in ("money", "exp", "pop"):
                scalar = next((c for c in phase if c.attrib.get("name") == scalar_name), None)
                if scalar is None:
                    continue
                value = parse_int(scalar.attrib.get("value"))
                if value is None:
                    add(hard, review, release_facing, f"invalid_{scalar_name}_action", qid, phase_name, "non-numeric value")
                    continue
                if value < INT_MIN or value > INT_MAX:
                    add(hard, review, release_facing, f"{scalar_name}_action_overflow", qid, phase_name, f"value={value}")
                if is_start and value > 0 and release_facing:
                    review.append(Finding("REVIEW", "restart_reward_surface", qid, phase_name, f"start action grants {scalar_name}={value}; verify forfeit/restart behavior"))

    payload = {
        "counts": dict(sorted(counts.items())),
        "hardFailureCount": len(hard),
        "reviewFindingCount": len(review),
        "hardFindings": [asdict(f) for f in hard],
        "reviewFindings": [asdict(f) for f in review],
    }
    if emit_json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"Quest gameplay completeness: {counts['active_quests']} active / {counts['check_quests']} Check.wz quests")
        print(f"Hard failures: {len(hard)}; reviews: {len(review)}; repeat intervals: {counts['repeat_intervals']}")
        for f in hard:
            print(f"[FAIL] {f.code} quest={f.quest_id} phase={f.phase}: {f.detail}")
        for f in review[:80]:
            print(f"[REVIEW] {f.code} quest={f.quest_id} phase={f.phase}: {f.detail}")
        if len(review) > 80:
            print(f"[REVIEW] ... {len(review) - 80} additional review findings")
    return 1 if hard else 0


if __name__ == "__main__":
    raise SystemExit(main())
