#!/usr/bin/env python3
"""Audit active quest item, mob, and map references against the v83 WZ corpus.

A quest is active when one of its Check.wz start/completion NPC owners is
spawned in the active Map.wz corpus. This audit validates stable classic quest
reference groups: Check/item, Check/mob, Check/fieldEnter, and Act/item.
"""
from __future__ import annotations

import json
import re
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QUEST_ROOT = ROOT / "wz" / "Quest.wz"
MAP_TREE = ROOT / "wz" / "Map.wz" / "Map"
MOB_ROOT = ROOT / "wz" / "Mob.wz"
ITEM_ROOT = ROOT / "wz" / "Item.wz"
CHARACTER_ROOT = ROOT / "wz" / "Character.wz"
CHECK = QUEST_ROOT / "Check.img.xml"
ACT = QUEST_ROOT / "Act.img.xml"
NUMERIC_FILE_RE = re.compile(r"^(\d+)\.img\.xml$")

# MapId.NONE is a first-class sentinel throughout the v83 server/WZ data and is
# valid in quest fieldEnter conditions; it is intentionally not a real map.
SPECIAL_MAP_IDS = {"999999999"}


def normalize(value: str | None) -> str:
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
        qid = normalize(node.attrib.get("name"))
        if qid.isdigit():
            result[qid] = node
    return result


def quest_owners(check_node: ET.Element) -> set[str]:
    result: set[str] = set()
    for phase in check_node:
        if phase.tag != "imgdir":
            continue
        npc = normalize(direct_value(phase, "npc"))
        if npc.isdigit() and int(npc) > 0:
            result.add(npc)
    return result


def index_maps_and_npcs() -> tuple[set[str], set[str]]:
    maps: set[str] = set()
    npcs: set[str] = set()
    for path in MAP_TREE.glob("Map*/*.img.xml"):
        match = NUMERIC_FILE_RE.match(path.name)
        if not match:
            continue
        maps.add(normalize(match.group(1)))
        root = parse(path)
        life = next(
            (child for child in root if child.tag == "imgdir" and child.attrib.get("name") == "life"),
            None,
        )
        if life is None:
            continue
        for entry in life:
            if entry.tag != "imgdir" or normalize(direct_value(entry, "type")) != "n":
                continue
            npc = normalize(direct_value(entry, "id"))
            if npc.isdigit() and int(npc) > 0:
                npcs.add(npc)
    return maps, npcs


def index_mobs() -> set[str]:
    result: set[str] = set()
    # QuestCountGroup/*.img.xml are semantic monster-group IDs used directly by
    # Quest.wz kill-count conditions (e.g. 9101000 = Green Mushroom group).
    # They are as valid for quest references as ordinary top-level Mob.wz IDs.
    for path in MOB_ROOT.rglob("*.img.xml"):
        match = NUMERIC_FILE_RE.match(path.name)
        if match:
            result.add(normalize(match.group(1)))
    return result


def index_items() -> set[str]:
    result: set[str] = set()
    for path in CHARACTER_ROOT.rglob("*.img.xml"):
        match = NUMERIC_FILE_RE.match(path.name)
        if match:
            value = normalize(match.group(1))
            if value.isdigit() and 1_000_000 <= int(value) < 2_000_000:
                result.add(value)

    for path in ITEM_ROOT.rglob("*.img.xml"):
        try:
            root = parse(path)
        except ET.ParseError:
            continue
        root_name = normalize(root.attrib.get("name"))
        if root_name.endswith(".img"):
            root_name = normalize(root_name[:-4])
        if root_name.isdigit() and int(root_name) >= 2_000_000:
            result.add(root_name)
        for child in root:
            if child.tag != "imgdir":
                continue
            item_id = normalize(child.attrib.get("name"))
            if item_id.isdigit() and int(item_id) >= 2_000_000:
                result.add(item_id)
    return result


def group_entries(phase: ET.Element, group_name: str) -> list[ET.Element]:
    for child in phase:
        if child.tag == "imgdir" and child.attrib.get("name") == group_name:
            return [entry for entry in child if entry.tag == "imgdir"]
    return []


def collect_check_refs(node: ET.Element) -> tuple[set[str], set[str], set[str], list[str]]:
    items: set[str] = set()
    mobs: set[str] = set()
    maps: set[str] = set()
    quantity_notes: list[str] = []
    for phase in node:
        if phase.tag != "imgdir":
            continue
        for entry in group_entries(phase, "item"):
            item_id = normalize(direct_value(entry, "id"))
            count = normalize(direct_value(entry, "count"))
            if item_id.isdigit() and int(item_id) > 0:
                items.add(item_id)
            if count and count.lstrip("-").isdigit() and abs(int(count)) > 32767:
                quantity_notes.append(f"required item {item_id} count={count}")
        for entry in group_entries(phase, "mob"):
            mob_id = normalize(direct_value(entry, "id"))
            count = normalize(direct_value(entry, "count"))
            if mob_id.isdigit() and int(mob_id) > 0:
                mobs.add(mob_id)
            if count and count.lstrip("-").isdigit() and abs(int(count)) > 32767:
                quantity_notes.append(f"required mob {mob_id} count={count}")
        for group in phase:
            if group.tag != "imgdir" or group.attrib.get("name") != "fieldEnter":
                continue
            for entry in group:
                value = normalize(entry.attrib.get("value"))
                if value.isdigit() and int(value) > 0:
                    maps.add(value)
    return items, mobs, maps, quantity_notes


def collect_act_items(node: ET.Element) -> tuple[set[str], list[str]]:
    items: set[str] = set()
    quantity_notes: list[str] = []
    for phase in node:
        if phase.tag != "imgdir":
            continue
        for entry in group_entries(phase, "item"):
            item_id = normalize(direct_value(entry, "id"))
            count = normalize(direct_value(entry, "count"))
            if item_id.isdigit() and int(item_id) > 0:
                items.add(item_id)
            if count and count.lstrip("-").isdigit() and abs(int(count)) > 32767:
                quantity_notes.append(f"act item {item_id} count={count}")
    return items, quantity_notes


def main() -> int:
    emit_json = "--json" in sys.argv
    failures: list[str] = []
    reviews: list[str] = []
    try:
        check_nodes = quest_nodes(CHECK)
        act_nodes = quest_nodes(ACT)
        map_ids, active_npcs = index_maps_and_npcs()
        mob_ids = index_mobs()
        item_ids = index_items()
    except (ET.ParseError, OSError) as exc:
        print(f"ERROR quest content reference audit setup failed: {exc}")
        return 1

    active_quests = {
        qid for qid, node in check_nodes.items() if quest_owners(node) & active_npcs
    }
    missing_items: dict[str, set[str]] = defaultdict(set)
    missing_mobs: dict[str, set[str]] = defaultdict(set)
    missing_maps: dict[str, set[str]] = defaultdict(set)
    checked_item_refs = checked_mob_refs = checked_map_refs = 0

    for qid in sorted(active_quests, key=int):
        check_items, mobs, maps, notes = collect_check_refs(check_nodes[qid])
        act_items, act_notes = collect_act_items(act_nodes[qid]) if qid in act_nodes else (set(), [])
        for note in notes + act_notes:
            reviews.append(f"Quest {qid}: suspicious quantity {note}")
        all_items = check_items | act_items
        checked_item_refs += len(all_items)
        checked_mob_refs += len(mobs)
        checked_map_refs += len(maps)
        for item_id in all_items:
            if item_id not in item_ids:
                missing_items[qid].add(item_id)
        for mob_id in mobs:
            if mob_id not in mob_ids:
                missing_mobs[qid].add(mob_id)
        for map_id in maps:
            if map_id not in map_ids and map_id not in SPECIAL_MAP_IDS:
                missing_maps[qid].add(map_id)

    for qid, ids in sorted(missing_items.items(), key=lambda pair: int(pair[0])):
        failures.append(f"Active quest {qid} references missing item ids: {','.join(sorted(ids, key=int))}")
    for qid, ids in sorted(missing_mobs.items(), key=lambda pair: int(pair[0])):
        failures.append(f"Active quest {qid} references missing mob/group ids: {','.join(sorted(ids, key=int))}")
    for qid, ids in sorted(missing_maps.items(), key=lambda pair: int(pair[0])):
        failures.append(f"Active quest {qid} references missing fieldEnter map ids: {','.join(sorted(ids, key=int))}")

    payload = {
        "activeQuestCount": len(active_quests),
        "indexedItemCount": len(item_ids),
        "indexedMobOrGroupCount": len(mob_ids),
        "indexedMapCount": len(map_ids),
        "specialMapIds": sorted(SPECIAL_MAP_IDS),
        "checkedItemReferenceCount": checked_item_refs,
        "checkedMobReferenceCount": checked_mob_refs,
        "checkedMapReferenceCount": checked_map_refs,
        "missingItems": {qid: sorted(ids, key=int) for qid, ids in missing_items.items()},
        "missingMobs": {qid: sorted(ids, key=int) for qid, ids in missing_mobs.items()},
        "missingMaps": {qid: sorted(ids, key=int) for qid, ids in missing_maps.items()},
        "reviews": reviews,
        "failures": failures,
    }
    if emit_json:
        print(json.dumps(payload, indent=2))
    else:
        print(
            f"Quest content refs: {len(active_quests)} active quests; "
            f"items={len(item_ids)} mobs/groups={len(mob_ids)} maps={len(map_ids)}"
        )
        print(
            f"Checked references: items={checked_item_refs} mobs={checked_mob_refs} maps={checked_map_refs}"
        )
        for line in reviews:
            print(f"[REVIEW] {line}")
        for line in failures:
            print(f"[FAIL] {line}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
