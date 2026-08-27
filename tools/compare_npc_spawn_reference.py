#!/usr/bin/env python3
"""Compare selected EverLeaf NPC life nodes with the older Maple83 reference.

This diagnostic is intentionally read-only. It downloads only XML source data
from the public reference repository and prints exact spawn/range fields so
reviewers can distinguish true regressions from intentional Cosmic changes.
"""

from __future__ import annotations

import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REFERENCE_BASE = "https://raw.githubusercontent.com/jonnylin13/Maple83/master/wz/Map.wz/Map"

TARGETS = (
    ("Map6", "600000000", "9201053"),
    ("Map6", "600000000", "9100109"),
    ("Map6", "670010600", "9201045"),
)

FIELDS = ("x", "y", "cy", "fh", "rx0", "rx1", "f", "hide", "mobTime")


def direct_imgdir(root: ET.Element, name: str) -> ET.Element | None:
    for child in root:
        if child.tag == "imgdir" and child.attrib.get("name") == name:
            return child
    return None


def child_value(node: ET.Element, name: str) -> str | None:
    for child in node:
        if child.attrib.get("name") == name:
            return child.attrib.get("value")
    return None


def find_npc(root: ET.Element, npc_id: str) -> ET.Element:
    life = direct_imgdir(root, "life")
    if life is None:
        raise RuntimeError("map has no life section")
    matches = [
        node for node in life
        if node.tag == "imgdir"
        and child_value(node, "type") == "n"
        and child_value(node, "id") == npc_id
    ]
    if len(matches) != 1:
        raise RuntimeError(f"expected one NPC {npc_id}, found {len(matches)}")
    return matches[0]


def snapshot(node: ET.Element) -> dict[str, str | None]:
    return {field: child_value(node, field) for field in FIELDS}


def load_reference(bucket: str, map_id: str) -> ET.Element:
    url = f"{REFERENCE_BASE}/{bucket}/{map_id}.img.xml"
    req = urllib.request.Request(url, headers={"User-Agent": "EverLeaf-NPC-Audit/1.0"})
    with urllib.request.urlopen(req, timeout=30) as response:
        return ET.fromstring(response.read())


def main() -> None:
    cache: dict[tuple[str, str], ET.Element] = {}
    for bucket, map_id, npc_id in TARGETS:
        local_path = ROOT / "wz" / "Map.wz" / "Map" / bucket / f"{map_id}.img.xml"
        current_root = ET.parse(local_path).getroot()
        key = (bucket, map_id)
        if key not in cache:
            cache[key] = load_reference(bucket, map_id)
        reference_root = cache[key]

        current = snapshot(find_npc(current_root, npc_id))
        reference = snapshot(find_npc(reference_root, npc_id))
        print(f"map={map_id} npc={npc_id}")
        print("  current:   " + " ".join(f"{k}={current[k]}" for k in FIELDS))
        print("  reference: " + " ".join(f"{k}={reference[k]}" for k in FIELDS))
        changed = [k for k in FIELDS if current[k] != reference[k]]
        print("  changed:   " + (", ".join(changed) if changed else "none"))


if __name__ == "__main__":
    main()
