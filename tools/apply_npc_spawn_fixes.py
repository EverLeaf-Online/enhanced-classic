#!/usr/bin/env python3
"""Apply verified EverLeaf NPC spawn-range corrections.

The fixes here were identified by scripts/audit_npc_spawns.py and cross-checked
against the older v83 map data. This script deliberately edits only rx0/rx1
inside the exact NPC life node and preserves the rest of each XML file byte-for-
byte (apart from the intended numeric values).
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class Fix:
    map_bucket: str
    map_id: str
    npc_id: str
    x: int
    bad_rx0: int
    bad_rx1: int
    good_rx0: int
    good_rx1: int
    reason: str

    @property
    def path(self) -> Path:
        return ROOT / "wz" / "Map.wz" / "Map" / self.map_bucket / f"{self.map_id}.img.xml"


FIXES = (
    Fix(
        "Map1", "101000000", "9010003", -596,
        -376, -276, -646, -546,
        "Ellinia spawn remained at x=-596 while its 100px range was shifted away from it; restore v83-centered range.",
    ),
    Fix(
        "Map1", "101000000", "9000036", -79,
        -57, 43, -129, -29,
        "Ellinia event NPC remained at x=-79 while its 100px range was shifted away from it; restore v83-centered range.",
    ),
    Fix(
        "Map1", "106020000", "1300000", 137,
        407, 407, 137, 137,
        "Mushroom Castle stationary NPC is at x=137 but its fixed range points to x=407.",
    ),
    Fix(
        "Map1", "106020000", "1300004", -45,
        67, 167, -95, 5,
        "Mushroom Castle NPC is at x=-45; restore the original 100px range centered on that unchanged spawn.",
    ),
)


def child_value(node: ET.Element, name: str) -> str | None:
    for child in node:
        if child.attrib.get("name") == name:
            return child.attrib.get("value")
    return None


def find_life_node(path: Path, npc_id: str) -> ET.Element:
    root = ET.parse(path).getroot()
    life = next(
        (child for child in root if child.tag == "imgdir" and child.attrib.get("name") == "life"),
        None,
    )
    if life is None:
        raise RuntimeError(f"{path}: missing life section")

    matches = [
        node for node in life
        if node.tag == "imgdir"
        and child_value(node, "type") == "n"
        and child_value(node, "id") == npc_id
    ]
    if len(matches) != 1:
        raise RuntimeError(f"{path}: expected exactly one NPC {npc_id}, found {len(matches)}")
    return matches[0]


def apply_fix(fix: Fix) -> bool:
    path = fix.path
    node = find_life_node(path, fix.npc_id)

    x = int(child_value(node, "x") or "999999999")
    rx0 = int(child_value(node, "rx0") or "999999999")
    rx1 = int(child_value(node, "rx1") or "999999999")

    if x != fix.x:
        raise RuntimeError(f"{path}: NPC {fix.npc_id} x changed: expected {fix.x}, found {x}")
    if (rx0, rx1) == (fix.good_rx0, fix.good_rx1):
        print(f"already fixed: map {fix.map_id} NPC {fix.npc_id}")
        return False
    if (rx0, rx1) != (fix.bad_rx0, fix.bad_rx1):
        raise RuntimeError(
            f"{path}: NPC {fix.npc_id} range changed unexpectedly: "
            f"expected bad {fix.bad_rx0}..{fix.bad_rx1}, found {rx0}..{rx1}"
        )

    text = path.read_text(encoding="utf-8")
    marker = f'<string name="id" value="{fix.npc_id}"/>'
    marker_pos = text.find(marker)
    if marker_pos < 0:
        raise RuntimeError(f"{path}: text marker for NPC {fix.npc_id} not found")

    block_start = text.rfind("<imgdir name=", 0, marker_pos)
    block_end = text.find("</imgdir>", marker_pos)
    if block_start < 0 or block_end < 0:
        raise RuntimeError(f"{path}: could not isolate XML block for NPC {fix.npc_id}")
    block_end += len("</imgdir>")
    block = text[block_start:block_end]

    old_rx0 = f'<int name="rx0" value="{fix.bad_rx0}"/>'
    old_rx1 = f'<int name="rx1" value="{fix.bad_rx1}"/>'
    new_rx0 = f'<int name="rx0" value="{fix.good_rx0}"/>'
    new_rx1 = f'<int name="rx1" value="{fix.good_rx1}"/>'

    if block.count(old_rx0) != 1 or block.count(old_rx1) != 1:
        raise RuntimeError(f"{path}: expected bad range text not uniquely present in NPC {fix.npc_id} block")

    patched = block.replace(old_rx0, new_rx0, 1).replace(old_rx1, new_rx1, 1)
    path.write_text(text[:block_start] + patched + text[block_end:], encoding="utf-8")
    print(f"fixed: map {fix.map_id} NPC {fix.npc_id}: {fix.bad_rx0}..{fix.bad_rx1} -> {fix.good_rx0}..{fix.good_rx1}")
    return True


def main() -> None:
    changed = 0
    for fix in FIXES:
        changed += int(apply_fix(fix))
    print(f"EverLeaf NPC spawn fixes complete: {changed} file-node changes applied.")


if __name__ == "__main__":
    main()
