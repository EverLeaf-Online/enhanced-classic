#!/usr/bin/env python3
"""Audit release-facing Quest.wz Act.img actions against server runtime support.

This closes the gap between structurally valid quests and actions the server can
actually execute. For non-limited quests owned by spawned NPCs it validates:
* every Act.img action name maps to QuestActionType;
* nextQuest targets resolve to Check.wz quests (0 is allowed as no-next sentinel);
* awarded skills resolve to Skill.wz;
* buffItemID values resolve to the item corpus;
* scalar action values fit signed Java int range.

Limited/event and unspawned quests remain review-only for unsupported donor
fields so obsolete content cannot block normal releases.
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
NUMERIC_FILE = re.compile(r"^(\d+)\.img\.xml$")
INT_MIN = -(2**31)
INT_MAX = 2**31 - 1
SUPPORTED_ACTIONS = {
    "exp", "money", "item", "skill", "nextQuest", "pop", "buffItemID",
    "petskill", "no", "yes", "npc", "lvmin", "normalAutoStart",
    "pettameness", "petspeed", "info", "0",
}
SCALAR_INT_ACTIONS = {
    "exp", "money", "nextQuest", "pop", "buffItemID", "petskill", "no",
    "yes", "npc", "lvmin", "normalAutoStart", "pettameness", "petspeed", "info", "0",
}


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
            if entry.tag != "imgdir" or norm(direct_value(entry, "type")) != "n":
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
    except (ET.ParseError, OSError) as exc:
        print(f"ERROR quest action audit setup failed: {exc}")
        return 1

    active = {
        qid for qid, node in checks.items()
        if bool(owners(node) & active_npcs) and not is_limited(node)
    }
    action_counts: Counter[str] = Counter()
    checked_skills = checked_next = checked_buffs = 0
    unsupported: dict[str, set[str]] = defaultdict(set)

    for qid, node in acts.items():
        release_facing = qid in active
        for p in node:
            if p.tag != "imgdir" or p.attrib.get("name") not in {"0", "1"}:
                continue
            for action in p:
                name = action.attrib.get("name") or ""
                action_counts[name] += 1
                if name not in SUPPORTED_ACTIONS:
                    unsupported[qid].add(name or "<unnamed>")
                    message = f"Quest {qid} Act.img uses unsupported action {name!r}"
                    if release_facing:
                        failures.append(message)
                    else:
                        reviews.append("Dormant/limited " + message.lower())
                    continue

                if name in SCALAR_INT_ACTIONS:
                    value = scalar_int(action)
                    if value is None:
                        message = f"Quest {qid} action {name} has non-integer scalar value {action.attrib.get('value')!r}"
                        if release_facing:
                            failures.append(message)
                        else:
                            reviews.append("Dormant/limited " + message.lower())
                    elif value < INT_MIN or value > INT_MAX:
                        message = f"Quest {qid} action {name} overflows Java int: {value}"
                        if release_facing:
                            failures.append(message)
                        else:
                            reviews.append("Dormant/limited " + message.lower())

                    if name == "nextQuest" and value is not None:
                        checked_next += 1
                        if value > 0 and str(value) not in checks:
                            message = f"Quest {qid} nextQuest target {value} is absent from Check.wz"
                            if release_facing:
                                failures.append(message)
                            else:
                                reviews.append("Dormant/limited " + message.lower())
                    elif name == "buffItemID" and value is not None and value > 0:
                        checked_buffs += 1
                        if str(value) not in item_ids:
                            message = f"Quest {qid} buffItemID {value} is absent from item data"
                            if release_facing:
                                failures.append(message)
                            else:
                                reviews.append("Dormant/limited " + message.lower())

                if name == "skill" and action.tag == "imgdir":
                    for entry in action:
                        if entry.tag != "imgdir":
                            continue
                        sid = norm(direct_value(entry, "id"))
                        if not sid.isdigit() or int(sid) <= 0:
                            message = f"Quest {qid} skill action contains invalid id {sid!r}"
                            if release_facing:
                                failures.append(message)
                            else:
                                reviews.append("Dormant/limited " + message.lower())
                            continue
                        checked_skills += 1
                        if sid not in skill_ids:
                            message = f"Quest {qid} awards missing skill id {sid}"
                            if release_facing:
                                failures.append(message)
                            else:
                                reviews.append("Dormant/limited " + message.lower())

    payload = {
        "releaseFacingQuestCount": len(active),
        "actQuestCount": len(acts),
        "indexedSkillCount": len(skill_ids),
        "indexedItemCount": len(item_ids),
        "checkedSkillRewards": checked_skills,
        "checkedNextQuestActions": checked_next,
        "checkedBuffItemActions": checked_buffs,
        "actionCounts": dict(action_counts),
        "unsupported": {qid: sorted(names) for qid, names in unsupported.items()},
        "reviews": reviews,
        "failures": failures,
    }
    if emit_json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"Quest action audit: {len(active)} release-facing quests / {len(acts)} Act.img quest records")
        print(f"Checked: {checked_skills} skill rewards / {checked_next} nextQuest actions / {checked_buffs} buff-item actions")
        print("Action types: " + ", ".join(f"{k}={v}" for k, v in sorted(action_counts.items())))
        for line in reviews[:100]:
            print(f"[REVIEW] {line}")
        if len(reviews) > 100:
            print(f"[REVIEW] ... {len(reviews) - 100} additional review-only findings")
        for line in failures:
            print(f"[FAIL] {line}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
