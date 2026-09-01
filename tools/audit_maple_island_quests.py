#!/usr/bin/env python3
"""Audit the classic Maple Island beginner quest/tutorial chain.

This is deliberately stricter than the broad world audit. Maple Island is the
first player-facing quest experience and custom NPC work must not replace its
classic quest/tutorial behavior.

Checks:
- discover Maple Island NPCs from active Map.wz data (map IDs below 100000)
- isolate classic low-ID tutorial NPCs from global event/service NPCs
- discover quests whose Check.wz start/completion owner is one of those NPCs
- require each discovered quest to retain Check/Say/QuestInfo data
- validate quest-owner NPC references have Npc.wz assets
- validate tutorial portal script references still exist
- hard-gate quest 1031 (Heena and Sera)
- hard-gate Heena NPC 2101 against another custom Evan/skip override

The script is read-only and safe for CI.
"""
from __future__ import annotations

import json
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAP_ROOT = ROOT / "wz" / "Map.wz" / "Map" / "Map0"
NPC_ROOT = ROOT / "wz" / "Npc.wz"
NPC_SCRIPTS = ROOT / "scripts" / "npc"
PORTAL_SCRIPTS = ROOT / "scripts" / "portal"
QUEST_ROOT = ROOT / "wz" / "Quest.wz"

QUEST_FILES = {
    "check": QUEST_ROOT / "Check.img.xml",
    "act": QUEST_ROOT / "Act.img.xml",
    "say": QUEST_ROOT / "Say.img.xml",
    "info": QUEST_ROOT / "QuestInfo.img.xml",
}

HEENA_NPC = "2101"
HEENA_QUEST = "1031"
HEENA_PORTAL_SCRIPT = "infoMinimap"
CLASSIC_NPC_MAX = 100000


def direct_imgdir(root: ET.Element, name: str) -> ET.Element | None:
    return next((c for c in root if c.tag == "imgdir" and c.attrib.get("name") == name), None)


def child_value(node: ET.Element, name: str) -> str | None:
    for child in node:
        if child.attrib.get("name") == name:
            return child.attrib.get("value")
    return None


def normalize(value: str | None) -> str:
    raw = (value or "").strip()
    if raw.lstrip("-").isdigit():
        return str(int(raw))
    return raw


def parse(path: Path) -> ET.Element:
    return ET.parse(path).getroot()


def maple_island_maps() -> dict[str, Path]:
    result: dict[str, Path] = {}
    for path in MAP_ROOT.glob("*.img.xml"):
        raw = path.name.split(".", 1)[0]
        if not raw.isdigit():
            continue
        map_id = int(raw)
        if 0 <= map_id < 100000:
            result[str(map_id)] = path
    return result


def collect_island_npcs(maps: dict[str, Path]) -> tuple[set[str], dict[str, set[str]], list[str]]:
    npcs: set[str] = set()
    locations: dict[str, set[str]] = defaultdict(set)
    portal_scripts: list[str] = []
    for map_id, path in sorted(maps.items(), key=lambda item: int(item[0])):
        root = parse(path)
        life = direct_imgdir(root, "life")
        if life is not None:
            for node in life:
                if node.tag != "imgdir" or normalize(child_value(node, "type")) != "n":
                    continue
                npc_id = normalize(child_value(node, "id"))
                if npc_id:
                    npcs.add(npc_id)
                    locations[npc_id].add(map_id)
        portals = direct_imgdir(root, "portal")
        if portals is not None:
            for node in portals:
                if node.tag != "imgdir":
                    continue
                script = (child_value(node, "script") or "").strip()
                if script:
                    portal_scripts.append(script)
    return npcs, locations, portal_scripts


def quest_nodes(root: ET.Element) -> dict[str, ET.Element]:
    nodes: dict[str, ET.Element] = {}
    for node in root:
        if node.tag != "imgdir":
            continue
        qid = normalize(node.attrib.get("name"))
        if qid.isdigit():
            nodes[qid] = node
    return nodes


def quest_owner_npcs(check_node: ET.Element) -> set[str]:
    refs: set[str] = set()
    for phase in check_node:
        if phase.tag != "imgdir":
            continue
        npc = normalize(child_value(phase, "npc"))
        if npc.isdigit():
            refs.add(npc)
    return refs


def npc_asset_exists(npc_id: str) -> bool:
    return npc_id.isdigit() and (NPC_ROOT / f"{int(npc_id):07d}.img.xml").is_file()


def main() -> int:
    emit_json = "--json" in sys.argv
    failures: list[str] = []
    reviews: list[str] = []

    try:
        maps = maple_island_maps()
        if not maps:
            failures.append("No Maple Island/tutorial maps were discovered below map ID 100000")
            raise RuntimeError("no maps")
        island_npcs, npc_locations, portal_scripts = collect_island_npcs(maps)
    except (ET.ParseError, OSError, RuntimeError) as exc:
        if not failures:
            failures.append(f"Unable to parse Maple Island map data: {exc}")
        maps, island_npcs, npc_locations, portal_scripts = {}, set(), defaultdict(set), []

    classic_island_npcs = {
        npc for npc in island_npcs
        if npc.isdigit() and 0 <= int(npc) < CLASSIC_NPC_MAX
    }

    quest_sets: dict[str, dict[str, ET.Element]] = {}
    for kind, path in QUEST_FILES.items():
        try:
            quest_sets[kind] = quest_nodes(parse(path))
        except (ET.ParseError, OSError) as exc:
            failures.append(f"Unable to parse {path.relative_to(ROOT)}: {exc}")
            quest_sets[kind] = {}

    discovered: set[str] = set()
    quest_owner_refs: dict[str, set[str]] = defaultdict(set)
    for qid, node in quest_sets.get("check", {}).items():
        refs = quest_owner_npcs(node)
        quest_owner_refs[qid].update(refs)
        if refs & classic_island_npcs:
            discovered.add(qid)

    for qid in sorted(discovered, key=int):
        for required in ("check", "say", "info"):
            if qid not in quest_sets.get(required, {}):
                failures.append(f"Maple Island quest {qid} is missing {required} data")
        if qid not in quest_sets.get("act", {}):
            reviews.append(f"Maple Island quest {qid} has no Act.img entry (may be dialogue/tutorial-only)")
        for npc_id in sorted(quest_owner_refs.get(qid, set()), key=int):
            if npc_id in classic_island_npcs and not npc_asset_exists(npc_id):
                failures.append(f"Quest {qid} references missing quest-owner NPC asset {npc_id}")

    if HEENA_NPC not in classic_island_npcs:
        failures.append("Heena NPC 2101 is not spawned on the Maple Island/tutorial map set")
    if HEENA_QUEST not in discovered:
        failures.append("Quest 1031 (Heena and Sera) is no longer owned by a classic Maple Island NPC in Check.wz")
    for required in ("check", "say", "info"):
        if HEENA_QUEST not in quest_sets.get(required, {}):
            failures.append(f"Quest 1031 is missing {required} data")

    heena_script_path = NPC_SCRIPTS / "2101.js"
    if not heena_script_path.is_file():
        failures.append("scripts/npc/2101.js is missing")
    else:
        lowered = heena_script_path.read_text(encoding="utf-8", errors="replace").lower()
        required_fragments = (
            "are you done with your training",
            "then, i will send you out from here. good job.",
            "cm.warp(40000, 0)",
        )
        for fragment in required_fragments:
            if fragment not in lowered:
                failures.append(f"Heena 2101 script lost classic tutorial behavior: missing {fragment!r}")
        forbidden_fragments = (
            "evan",
            "changejob",
            "lith harbor",
            "skip the tutorial",
            "skip maple island",
        )
        for fragment in forbidden_fragments:
            if fragment in lowered:
                failures.append(f"Heena 2101 script contains custom class/tutorial override text: {fragment!r}")

    portal_path = PORTAL_SCRIPTS / f"{HEENA_PORTAL_SCRIPT}.js"
    if not portal_path.is_file():
        failures.append(f"Quest 1031 tutorial hook scripts/portal/{HEENA_PORTAL_SCRIPT}.js is missing")
    else:
        portal_text = portal_path.read_text(encoding="utf-8", errors="replace")
        if "1031" not in portal_text or "isQuestStarted" not in portal_text:
            failures.append("infoMinimap.js no longer checks active quest 1031")

    missing_portal_scripts = sorted({s for s in portal_scripts if not (PORTAL_SCRIPTS / f"{s}.js").is_file()})
    for script in missing_portal_scripts:
        failures.append(f"Maple Island portal references missing script {script}.js")

    scripted_classic_npcs = sorted(
        npc for npc in classic_island_npcs if (NPC_SCRIPTS / f"{npc}.js").is_file()
    )
    payload = {
        "maps": len(maps),
        "allIslandNpcs": len(island_npcs),
        "classicIslandNpcIds": sorted(classic_island_npcs, key=int),
        "scriptedClassicIslandNpcs": scripted_classic_npcs,
        "discoveredQuestCount": len(discovered),
        "discoveredQuests": sorted(discovered, key=int),
        "heenaMaps": sorted(npc_locations.get(HEENA_NPC, set()), key=int),
        "failures": failures,
        "reviews": reviews,
    }

    if emit_json:
        print(json.dumps(payload, indent=2))
    else:
        print(
            f"Maple Island quest audit: {len(maps)} maps, {len(island_npcs)} total NPCs, "
            f"{len(classic_island_npcs)} classic NPCs, {len(discovered)} owned quest records"
        )
        print("Classic NPCs:", ", ".join(payload["classicIslandNpcIds"]) or "none")
        print("Discovered quests:", ", ".join(payload["discoveredQuests"]) or "none")
        print("Heena maps:", ", ".join(payload["heenaMaps"]) or "none")
        for item in reviews:
            print(f"[REVIEW] {item}")
        for item in failures:
            print(f"[FAIL] {item}")

    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
