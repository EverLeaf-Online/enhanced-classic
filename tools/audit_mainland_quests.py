#!/usr/bin/env python3
"""Regional quest integrity audit for the major post-Victoria classic world.

The global Quest.wz audits prove references resolve. This regional layer makes
that coverage useful for release planning by grouping active quests by the
classic town/map families players actually progress through.

A regional quest is one whose Check.wz start/completion owner NPC is spawned in
that region. Missing owner assets are hard failures. Missing Say/Info/Act
sections are review-only because classic/event/tutorial records legitimately
vary in shape.
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

# Use narrow canonical town/continent families rather than broad hundred-million
# buckets so unrelated event/PQ maps do not silently define a region as healthy.
REGIONS: dict[str, tuple[tuple[int, int], ...]] = {
    "Orbis": ((200_000_000, 201_000_000),),
    "El Nath": ((211_000_000, 212_000_000),),
    "Ludibrium": ((220_000_000, 221_000_000),),
    "Omega Sector": ((221_000_000, 222_000_000),),
    "Korean Folk Town": ((222_000_000, 223_000_000),),
    "Aqua Road": ((230_000_000, 231_000_000),),
    "Leafre": ((240_000_000, 241_000_000),),
    "Mu Lung": ((250_000_000, 251_000_000),),
    "Herb Town": ((251_000_000, 252_000_000),),
    "Ariant": ((260_000_000, 261_000_000),),
    "Magatia": ((261_000_000, 262_000_000),),
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


def regions_for_map(map_id: int) -> set[str]:
    result: set[str] = set()
    for region, ranges in REGIONS.items():
        for lo, hi in ranges:
            if lo <= map_id < hi:
                result.add(region)
                break
    return result


def collect_region_npcs() -> tuple[dict[str, set[str]], dict[str, set[str]], dict[str, int]]:
    by_region: dict[str, set[str]] = defaultdict(set)
    npc_regions: dict[str, set[str]] = defaultdict(set)
    map_counts: dict[str, int] = defaultdict(int)
    for path in MAP_ROOT.glob("Map*/*.img.xml"):
        raw = path.name.split(".", 1)[0]
        if not raw.isdigit():
            continue
        map_regions = regions_for_map(int(raw))
        if not map_regions:
            continue
        for region in map_regions:
            map_counts[region] += 1
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
            if not npc.isdigit() or int(npc) <= 0:
                continue
            for region in map_regions:
                by_region[region].add(npc)
                npc_regions[npc].add(region)
    return by_region, npc_regions, map_counts


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
        region_npcs, npc_regions, map_counts = collect_region_npcs()
    except (ET.ParseError, OSError) as exc:
        print(f"ERROR mainland quest audit setup failed: {exc}")
        return 1

    quests_by_region: dict[str, set[str]] = defaultdict(set)
    regional_quests: set[str] = set()
    missing_sections: dict[str, dict[str, set[str]]] = {
        region: {"act": set(), "say": set(), "info": set()} for region in REGIONS
    }

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
            if qid not in act:
                missing_sections[region]["act"].add(qid)
            if qid not in say:
                missing_sections[region]["say"].add(qid)
            if qid not in info:
                missing_sections[region]["info"].add(qid)

        for npc in qowners:
            if npc in npc_regions and not npc_asset_exists(npc):
                failures.append(f"Regional quest {qid} spawned owner NPC {npc} has no Npc.wz asset")

    # All named core regions should have actual maps, NPCs, and at least one
    # quest owner. This catches accidental bulk deletion or bad range edits.
    for region in REGIONS:
        if map_counts.get(region, 0) == 0:
            failures.append(f"{region}: no maps found in configured regional ranges")
        if not region_npcs.get(region):
            failures.append(f"{region}: no active NPCs found")
        if not quests_by_region.get(region):
            failures.append(f"{region}: no discoverable quest-owner records")

        for section in ("act", "say", "info"):
            missing = sorted(missing_sections[region][section], key=int)
            if missing:
                preview = ", ".join(missing[:12]) + (" ..." if len(missing) > 12 else "")
                reviews.append(f"{region}: {len(missing)} quests missing {section}: {preview}")

    payload = {
        "regionalQuestCount": len(regional_quests),
        "regions": {
            region: {
                "mapCount": map_counts.get(region, 0),
                "npcCount": len(region_npcs.get(region, set())),
                "questCount": len(quests_by_region.get(region, set())),
                "questIds": sorted(quests_by_region.get(region, set()), key=int),
                "missingSectionCounts": {
                    section: len(missing_sections[region][section])
                    for section in ("act", "say", "info")
                },
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
        print(f"Classic mainland quest audit: {len(regional_quests)} unique regional quest records")
        for region in REGIONS:
            data = payload["regions"][region]
            print(
                f"{region}: {data['mapCount']} maps / {data['npcCount']} NPCs / "
                f"{data['questCount']} quests"
            )
        if reviews:
            print(f"Review-only section findings: {len(reviews)}")
            for line in reviews[:50]:
                print(f"[REVIEW] {line}")
            if len(reviews) > 50:
                print(f"[REVIEW] ... and {len(reviews) - 50} more")
        for line in failures:
            print(f"[FAIL] {line}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
