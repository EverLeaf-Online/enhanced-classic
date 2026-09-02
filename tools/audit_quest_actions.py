#!/usr/bin/env python3
"""Audit release-facing Quest.wz Act.img actions against server runtime support.

The server intentionally ignores several Act.img dialogue/control fields. This
audit therefore hard-validates only actions that Quest.getAction() actually
executes, while keeping unknown/client metadata visible as review-only output.
It also guards the historical ``quest`` mapping: QuestAction exists and Act.img
uses it to mutate other quest states, so QuestActionType must map that WZ name.
"""
from __future__ import annotations

import json
import re
import sys
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QUEST = ROOT / "wz" / "Quest.wz"
CHECK = QUEST / "Check.img.xml"
ACT = QUEST / "Act.img.xml"
MAP_ROOT = ROOT / "wz" / "Map.wz" / "Map"
SKILL_ROOT = ROOT / "wz" / "Skill.wz"
ITEM_ROOT = ROOT / "wz" / "Item.wz"
CHAR_ROOT = ROOT / "wz" / "Character.wz"
ACTION_TYPE_SOURCE = ROOT / "src" / "main" / "java" / "server" / "quest" / "QuestActionType.java"
NUMERIC_FILE = re.compile(r"^(\d+)\.img\.xml$")
INT_MIN = -(2**31)
INT_MAX = 2**31 - 1

# These are the Act.img names for which Quest.getAction() returns a handler.
EXECUTABLE_ACTIONS = {
    "exp", "money", "item", "quest", "skill", "nextQuest", "pop",
    "buffItemID", "petskill", "pettameness", "petspeed", "info",
}
# Known WZ metadata/control fields mapped by QuestActionType but intentionally
# not instantiated by Quest.getAction(). Do not confuse these with rewards.
KNOWN_METADATA = {"no", "yes", "npc", "lvmin", "normalAutoStart", "0"}
SCALAR_INT_ACTIONS = {
    "exp", "money", "nextQuest", "pop", "buffItemID", "petskill",
    "pettameness", "petspeed",
}
VALID_QUEST_STATES = {0, 1, 2}


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


def quest_nodes(path: Path) -> dict[str, ET.Element]:
    result: dict[str, ET.Element] = {}
    for node in parse(path):
        if node.tag != "imgdir":
            continue
        qid = norm(node.attrib.get("name"))
        if qid.isdigit():
            result[qid] = node
    return result


def phase(node: ET.Element, name: str) -> ET.Element | None:
    return next((c for c in node if c.tag == "imgdir" and c.attrib.get("name") == name), None)


def owners(node: ET.Element) -> set[str]:
    result: set[str] = set()
    for p in node:
        if p.tag != "imgdir":
            continue
        npc = norm(direct_value(p, "npc"))
        if npc.isdigit() and int(npc) > 0:
            result.add(npc)
    return result


def is_limited(node: ET.Element) -> bool:
    p = phase(node, "0")
    return p is not None and direct_value(p, "end") is not None


def spawned_npcs() -> set[str]:
    result: set[str] = set()
    for path in MAP_ROOT.glob("Map*/*.img.xml"):
        root = parse(path)
        life = next((c for c in root if c.tag == "imgdir" and c.attrib.get("name") == "life"), None)
        if life is None:
            continue
        for entry in life:
            if entry.tag != "imgdir"" or norm(direct_value(entry, "type")) != "n":
                continue
            npc = norm(direct_value(entry, "id"))
            if npc.isdigit() and int(npc) > 0:
                result.add(npc)
    return result


def index_skills() -> set[str]:
    result: set[str] = set()
    for path in SKILL_ROOT.glob("*.img.xml"):
        try:
            root = parse(path)
        except ET.ParseError:
            continue
        group = next((c for c in root if c.tag == "imgdir" and c.attrib.get("name") == "skill"), None)
        if group is None:
            continue
        for entry in group:
            sid = norm(entry.attrib.get("name"))
            if entry.tag == "imgdir" and sid.isdigit() and int(sid) > 0:
                result.add(sid)
    return result


def index_items() -> set[str]:
    result: set[str] = set()
    for path in CHAR_ROOT.rglob("*.img.xml"):
        m = NUMERIC_FILE.match(path.name)
        if m:
            iid = norm(m.group(1))
            if iid.isdigit() and 1_000_000 <= int(iid) < 2_000_000:
                result.add(iid)
    for path in ITEM_ROOT.rglob("*.img.xml"):
        try:
            root = parse(path)
        except ET.ParseError:
            continue
        root_name = (root.attrib.get("name") or "")
        if root_name.endswith(".img"):
            root_name = root_name[:-4]
        iid = norm(root_name)
        if iid.isdigit() and int(iid) >= 2_000_000:
            result.add(iid)
        for child in root:
            if child.tag != "imgdir":
                continue
            iid = norm(child.attrib.get("name"))
            if iid.isdigit() and int(iid) >= 2_000_000:
                result.add(iid)
    return result


def scalar_int(node: ET.Element) -> int | None:
    raw = norm(node.attrib.get("value"))
    return int(raw) if raw.lstrip("-").isdigit() else None


def report(message: str, release_facing: bool, failures: list[str], reviews: list[str]) -> None:
    if release_facing:
        failures.append(message)
    else:
        reviews.append("Dormant/limited " + message.lower())


def main() -> int:
    emit_json = "--json" in sys.argv
    failures: list[str] = []
    reviews: list[str] = []
    try:
        checks = quest_nodes(CHECK)
        acts = quest_nodes(ACT)
        active_npcs = spawned_npcs()
        skill_ids = index_skills()
        item_ids = index_items()
        action_type_source = ACTION_TYPE_SOURCE.read_text(encoding="utf-8")
    except (ET.ParseError, OSError) as exc:
        print(f"ERROR quest action audit setup failed: {exc}")
        return 1

    if not re.search(r'case\s+"quest"\s*:\s*\n\s*return\s+QUEST\s*;', action_type_source):
        failures.append('QuestActionType must map WZ action "quest" to QUEST')

    active = {
        qid for qid, node in checks.items()
        if bool(owners(node) & active_npcs) and not is_limited(node)
    }
    action_counts: Counter[str] = Counter()
    metadata_counts: Counter[str] = Counter()
    unknown_counts: Counter[str] = Counter()
    checked_skills = checked_next = checked_buffs = checked_quest_states = 0

    for qid, node in acts.items():
        release_facing = qid in active
        for p in node:
            if p.tag != "imgdir" or p.attrib.get("name") not in {"0", "1"}:
                continue
            for action in p:
                name = action.attrib.get("name") or ""
                if name in KNOWN_METADATA:
                    metadata_counts[name] += 1
                    continue
                if name not in EXECUTABLE_ACTIONS:
                    unknown_counts[name or "<unnamed>"] += 1
                    continue

                action_counts[name] += 1
                if name in SCALAR_INT_ACTIONS:
                    value = scalar_int(action)
                    if value is None:
                        report(
                            f"Quest {qid} action {name} has non-integer scalar value {action.attrib.get('value')!r}",
                            release_facing, failures, reviews,
                        )
                        continue
                    if value < INT_MIN or value > INT_MAX:
                        report(f"Quest {qid} action {name} overflows Java int: {value}", release_facing, failures, reviews)
                    if name == "nextQuest":
                        checked_next += 1
                        if value > 0 and str(value) not in checks:
                            report(f"Quest {qid} nextQuest target {value} is absent from Check.wz", release_facing, failures, reviews)
                    elif name == "buffItemID" and value > 0:
                        checked_buffs += 1
                        if str(value) not in item_ids:
                            report(f"Quest {qid} buffItemID {value} is absent from item data", release_facing, failures, reviews)

                elif name == "skill":
                    if action.tag != "imgdir":
                        report(f"Quest {qid} skill action is not an imgdir", release_facing, failures, reviews)
                        continue
                    for entry in action:
                        if entry.tag != "imgdir":
                            continue
                        sid = norm(direct_value(entry, "id"))
                        if not sid.isdigit() or int(sid) <= 0:
                            report(f"Quest {qid} skill action contains invalid id {sid!r}", release_facing, failures, reviews)
                            continue
                        checked_skills += 1
                        if sid not in skill_ids:
                            report(f"Quest {qid} awards missing skill id {sid}", release_facing, failures, reviews)

                elif name == "quest":
                    if action.tag != "imgdir":
                        report(f"Quest {qid} quest-state action is not an imgdir", release_facing, failures, reviews)
                        continue
                    for entry in action:
                        if entry.tag != "imgdir":
                            continue
                        target = norm(direct_value(entry, "id"))
                        state_raw = norm(direct_value(entry, "state"))
                        checked_quest_states += 1
                        if not target.isdigit() or int(target) <= 0:
                            report(f"Quest {qid} quest-state action has invalid target id {target!r}", release_facing, failures, reviews)
                        elif target not in checks:
                            report(f"Quest {qid} quest-state action targets missing quest {target}", release_facing, failures, reviews)
                        if not state_raw.lstrip("-").isdigit() or int(state_raw) not in VALID_QUEST_STATES:
                            report(f"Quest {qid} quest-state action has invalid state {state_raw!r} for target {target}", release_facing, failures, reviews)

                elif name == "item":
                    # Item/action references and quantities are covered by the dedicated
                    # quest content-reference audit; count here to prove runtime coverage.
                    pass
                elif name == "info":
                    # InfoAction intentionally accepts arbitrary strings.
                    pass

    if unknown_counts:
        reviews.append(
            "Act.img contains client/dialogue fields intentionally not executed by Quest.getAction(): "
            + ", ".join(f"{k}={v}" for k, v in sorted(unknown_counts.items()))
        )

    payload = {
        "releaseFacingQuestCount": len(active),
        "actQuestCount": len(acts),
        "indexedSkillCount": len(skill_ids),
        "indexedItemCount": len(item_ids),
        "checkedSkillRewards": checked_skills,
        "checkedNextQuestActions": checked_next,
        "checkedBuffItemActions": checked_buffs,
        "checkedQuestStateActions": checked_quest_states,
        "executableActionCounts": dict(action_counts),
        "metadataCounts": dict(metadata_counts),
        "unknownClientFields": dict(unknown_counts),
        "reviews": reviews,
        "failures": failures,
    }
    if emit_json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"Quest action audit: {len(active)} release-facing quests / {len(acts)} Act.img quest records")
        print(
            f"Checked: {checked_skills} skill rewards / {checked_next} nextQuest / "
            f"{checked_buffs} buff-item / {checked_quest_states} quest-state actions"
        )
        print("Executable actions: " + ", ".join(f"{k}={v}" for k, v in sorted(action_counts.items())))
        for line in reviews[:50]:
            print(f"[REVIEW] {line}")
        if len(reviews) > 50:
            print(f"[REVIEW] ... {len(reviews) - 50} additional review-only findings")
        for line in failures:
            print(f"[FAIL] {line}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
