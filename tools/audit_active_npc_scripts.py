#!/usr/bin/env python3
"""Inventory active NPC script coverage for EverLeaf.

This review audit scans NPCs that are actually spawned in Map.wz and classifies
whether their dedicated scripts are missing, trivial stubs, or substantive.
It is intentionally non-fatal for now: some retail NPCs are informational or
client-driven, so a missing/stub script must be triaged before becoming a hard
CI failure.
"""
from __future__ import annotations

import json
import re
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAP_ROOT = ROOT / "wz" / "Map.wz" / "Map"
NPC_SCRIPT_ROOT = ROOT / "scripts" / "npc"


def child_value(node: ET.Element, name: str) -> str | None:
    for child in node:
        if child.attrib.get("name") == name:
            return child.attrib.get("value")
    return None


def direct_imgdir(root: ET.Element, name: str) -> ET.Element | None:
    for child in root:
        if child.tag == "imgdir" and child.attrib.get("name") == name:
            return child
    return None


def normalize_script(text: str) -> str:
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    text = re.sub(r"//.*", "", text)
    return re.sub(r"\s+", "", text)


def is_trivial_stub(text: str) -> bool:
    normalized = normalize_script(text)
    trivial = {
        "functionstart(){cm.dispose();}",
        "functionstart(){cm.sendOk(\"\");cm.dispose();}",
    }
    if normalized in trivial:
        return True
    # Catch equivalent one-function scripts that do nothing except dispose.
    return bool(re.fullmatch(r"functionstart\(\)\{(?:cm\.)?dispose\(\);\}", normalized))


def main() -> int:
    emit_json = "--json" in sys.argv
    spawns: dict[str, set[str]] = defaultdict(set)
    parse_errors: list[str] = []

    for path in MAP_ROOT.glob("Map*/*.img.xml"):
        map_id = path.name.split(".", 1)[0]
        try:
            root = ET.parse(path).getroot()
        except (ET.ParseError, OSError) as exc:
            parse_errors.append(f"{path.relative_to(ROOT)}: {exc}")
            continue
        life = direct_imgdir(root, "life")
        if life is None:
            continue
        for node in life:
            if node.tag != "imgdir" or child_value(node, "type") != "n":
                continue
            npc_id = child_value(node, "id")
            if npc_id and npc_id.isdigit():
                spawns[str(int(npc_id))].add(str(int(map_id)))

    missing: list[dict[str, object]] = []
    stubs: list[dict[str, object]] = []
    substantive = 0

    for npc_id, maps in sorted(spawns.items(), key=lambda item: int(item[0])):
        script = NPC_SCRIPT_ROOT / f"{npc_id}.js"
        item = {"npcId": int(npc_id), "maps": sorted(map(int, maps))}
        if not script.is_file():
            missing.append(item)
            continue
        try:
            text = script.read_text(encoding="utf-8", errors="replace")
        except OSError:
            missing.append(item)
            continue
        if is_trivial_stub(text):
            stubs.append(item)
        else:
            substantive += 1

    payload = {
        "uniqueSpawnedNpcCount": len(spawns),
        "substantiveScriptCount": substantive,
        "missingDedicatedScriptCount": len(missing),
        "trivialStubScriptCount": len(stubs),
        "parseErrors": parse_errors,
        "missingDedicatedScripts": missing,
        "trivialStubScripts": stubs,
    }

    if emit_json:
        print(json.dumps(payload, indent=2))
    else:
        print(
            "EverLeaf active NPC script audit: "
            f"{len(spawns)} unique spawned NPCs; {substantive} substantive scripts; "
            f"{len(missing)} missing dedicated scripts; {len(stubs)} trivial stubs"
        )
        for item in stubs[:40]:
            print(f"[REVIEW] stub NPC {item['npcId']} spawned on maps {item['maps']}")
        if len(stubs) > 40:
            print(f"[REVIEW] ... {len(stubs) - 40} additional stub NPCs omitted")
        for item in missing[:40]:
            print(f"[REVIEW] no dedicated script for NPC {item['npcId']} on maps {item['maps']}")
        if len(missing) > 40:
            print(f"[REVIEW] ... {len(missing) - 40} additional missing scripts omitted")
        for error in parse_errors[:20]:
            print(f"[REVIEW] XML parse error: {error}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
