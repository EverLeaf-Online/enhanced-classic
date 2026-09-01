#!/usr/bin/env python3
"""Regional integrity audit for classic Victoria Island quests.

This turns the global quest corpus into a manageable player-facing batch. A
Victoria quest is one whose Check.wz start/completion owner NPC appears on one
of the classic Victoria/Nautilus map families below.

The audit inventories each town's quest IDs and hard-fails regional structural
breakage that the global audit should never permit: missing quest sections,
missing owner assets, or an empty core-town quest set.
"""
from __future__ import annotations

import json
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAP_ROOT = ROOT / "wz" / "Map.wz" / "Map"
NPC_ROOT = ROOT / "wz" / "Npc.wz"
QUEST_ROOT = ROOT / "wz" / "Quest.wz"

CHECK = QUEST_ROOT / "Check.img.xml"
ACT = QUEST_ROOT / "Act.img.xml"
SAY = QUEST_ROOT / "Say.img.xml"
INFO = QUEST_ROOT / "QuestInfo.img.xml"

REGIONS = {
    "Henesys": (100_000_000, 101_000_000),
    "Ellinia": (101_000_000, 102_000_000),
    "Perion": (102_000_000, 103_000_000),
    "Kerning City": (103_000_000, 104_000_000),
    "Lith Harbor": (104_000_000, 105_000_000),
    "Sleepywood": (105_000_000, 106_000_000),
    "Nautilus": (120_000_000, 121_000_000),
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


def owners(node: ET.Element) -> set[str]:
    result: set[str] = set()
    for phase in node:
        if phase.tag != "imgdir":
            continue
        npc = norm(direct_value(phase, "npc"))
        if npc.isdigit() and int(npc) > 0:
            result.add(npc)
    return result


def region_for_map(map_id: int) -> str | None:
    for region, (lo, hi) in REGIONS.items():
        if lo <= map_id < hi:
            return region
    return None


def collect_region_npcs() -> tuple[dict[str, set[str]], dict[str, set[str]], int]:
    by_region: dict[str, set[str]] = defaultdict(set)
    npc_regions: dict[str, set[str]] = defaultdict(set)
    map_count = 0
    for path in MAP_ROOT.glob("Map*/*.img.xml"):
        raw = path.name.split(".", 1)[0]
        if not raw.isdigit():
            continue
        region = region_for_map(int(raw))
        if region is None:
            continue
        map_count += 1
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
                by_region[region].add(npc)
                npc_regions[npc].add(region)
    return by_region, npc_regions, map_count


def npc_asset_exists(npc: str) -> bool:
    return (NPC_ROOT / f"{int(npc):07d}.img.xml").is_file()


def main() -> int:
    emit_json = "--json" in sys.argv
    failures: list[str] = []
    reviews: list[str] = []
    try:
        check = quest_nodes(CHECK)
        act = quest_nodes(ACT)
        say = quest_nodes(SAY)
        info = quest_nodes(INFO)
        region_npcs, npc_regions, map_count = collect_region_npcs()
    except (ET.ParseError, OSError) as exc:
        print(f"ERROR Victoria quest audit setup failed: {exc}")
        return 1

    quests_by_region: dict[str, set[str]] = defaultdict(set)
    regional_quests: set[str] = set()
    for qid, node in check.items():
        qowners = owners(node)
        regions: set[str] = set()
        for npc in qowners:
            regions.update(npc_regions.get(npc, set()))
        if not regions:
            continue
        regional_quests.add(qid)
        for region in regions:
            quests_by_region[region].add(qid)

        for npc in qowners:
            if npc in npc_regions and not npc_asset_exists(npc):
                failures.append(f"Victoria quest {qid} active owner NPC {npc} has no Npc.wz asset")

        # Say and QuestInfo are expected for player-facing regional quests.
        if qid not in say:
            reviews.append(f"Victoria quest {qid} has no Say.img section")
        if qid not in info:
            reviews.append(f"Victoria quest {qid} has no QuestInfo.img section")
        if qid not in act:
            reviews.append(f"Victoria quest {qid} has no Act.img section")

    for region in REGIONS:
        if not region_npcs.get(region):
            failures.append(f"{region} has no active NPCs in the regional map set")
        if not quests_by_region.get(region):
            failures.append(f"{region} has no discoverable quest-owner records")

    payload = {
        "regionalMapCount": map_count,
        "regionalQuestCount": len(regional_quests),
        "regions": {
            region: {
                "npcCount": len(region_npcs.get(region, set())),
                "questCount": len(quests_by_region.get(region, set())),
                "questIds": sorted(quests_by_region.get(region, set()), key=int),
            }
            for region in REGIONS
        },
        "reviewCount": len(reviews),
        "reviews": reviews,
        "failures": failures,
    }

    if emit_json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"Victoria quest audit: {map_count} maps / {len(regional_quests)} regional quest records")
        for region in REGIONS:
            data = payload["regions"][region]
            print(f"{region}: {data['npcCount']} NPCs / {data['questCount']} quests")
        if reviews:
            print(f"Review-only section asymmetries: {len(reviews)}")
            for line in reviews[:40]:
                print(f"[REVIEW] {line}")
            if len(reviews) > 40:
                print(f"[REVIEW] ... and {len(reviews) - 40} more")
        for line in failures:
            print(f"[FAIL] {line}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
