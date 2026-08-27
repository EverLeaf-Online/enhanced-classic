#!/usr/bin/env python3
"""Compare one EverLeaf map against an older v83 reference map.

Reports NPC life-node field changes and object-layer differences without editing
anything. Intended for screenshot-driven map audits where the map looks visually
wrong even though every spawn record is structurally valid.
"""

from __future__ import annotations

import argparse
import json
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CURRENT_ROOT = ROOT / "wz" / "Map.wz" / "Map"

LIFE_FIELDS = ("id", "type", "x", "y", "fh", "cy", "rx0", "rx1", "f", "hide", "mobTime", "limitedname")
OBJ_FIELDS = ("x", "y", "z", "zM", "oS", "l0", "l1", "l2", "f")


def child_value(node: ET.Element, name: str) -> str | None:
    for child in node:
        if child.attrib.get("name") == name:
            return child.attrib.get("value")
    return None


def find_map(root: Path, map_id: str) -> Path:
    matches = list(root.glob(f"Map*/{map_id}.img.xml"))
    if len(matches) != 1:
        raise SystemExit(f"expected one map {map_id} under {root}, found {len(matches)}")
    return matches[0]


def life_records(path: Path) -> list[dict[str, str | None]]:
    root = ET.parse(path).getroot()
    life = next((c for c in root if c.tag == "imgdir" and c.attrib.get("name") == "life"), None)
    if life is None:
        return []
    out = []
    for node in life:
        if node.tag != "imgdir":
            continue
        out.append({field: child_value(node, field) for field in LIFE_FIELDS})
    return out


def object_records(path: Path) -> list[tuple[str | None, ...]]:
    root = ET.parse(path).getroot()
    out: list[tuple[str | None, ...]] = []
    for layer in root:
        if layer.tag != "imgdir" or not layer.attrib.get("name", "").isdigit():
            continue
        obj = next((c for c in layer if c.tag == "imgdir" and c.attrib.get("name") == "obj"), None)
        if obj is None:
            continue
        for node in obj:
            if node.tag == "imgdir":
                out.append(tuple(child_value(node, field) for field in OBJ_FIELDS))
    return out


def key_life(record: dict[str, str | None]) -> tuple[str | None, str | None]:
    return (record.get("type"), record.get("id"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("map_id")
    parser.add_argument("reference_root", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    current_path = find_map(CURRENT_ROOT, args.map_id)
    reference_path = find_map(args.reference_root.resolve(), args.map_id)

    current_life = life_records(current_path)
    reference_life = life_records(reference_path)

    current_by_key: dict[tuple[str | None, str | None], list[dict[str, str | None]]] = {}
    reference_by_key: dict[tuple[str | None, str | None], list[dict[str, str | None]]] = {}
    for record in current_life:
        current_by_key.setdefault(key_life(record), []).append(record)
    for record in reference_life:
        reference_by_key.setdefault(key_life(record), []).append(record)

    life_diffs = []
    for key in sorted(set(current_by_key) | set(reference_by_key), key=str):
        cur = current_by_key.get(key, [])
        ref = reference_by_key.get(key, [])
        if cur == ref:
            continue
        life_diffs.append({"key": key, "current": cur, "reference": ref})

    current_objects = Counter(object_records(current_path))
    reference_objects = Counter(object_records(reference_path))
    extra_objects = []
    missing_objects = []
    for record, count in (current_objects - reference_objects).items():
        extra_objects.append({"count": count, "record": dict(zip(OBJ_FIELDS, record))})
    for record, count in (reference_objects - current_objects).items():
        missing_objects.append({"count": count, "record": dict(zip(OBJ_FIELDS, record))})

    payload = {
        "mapId": args.map_id,
        "currentLifeCount": len(current_life),
        "referenceLifeCount": len(reference_life),
        "lifeDifferences": life_diffs,
        "currentObjectCount": sum(current_objects.values()),
        "referenceObjectCount": sum(reference_objects.values()),
        "extraCurrentObjects": extra_objects,
        "missingReferenceObjects": missing_objects,
    }

    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"Map {args.map_id}: life current={len(current_life)} reference={len(reference_life)}; object current={sum(current_objects.values())} reference={sum(reference_objects.values())}")
        print(f"Life differences: {len(life_diffs)}; extra current objects: {len(extra_objects)}; missing reference objects: {len(missing_objects)}")
        for diff in life_diffs:
            print(f"[LIFE] {diff['key']}\n  current={diff['current']}\n  reference={diff['reference']}")
        for item in extra_objects:
            print(f"[EXTRA_OBJECT x{item['count']}] {item['record']}")
        for item in missing_objects:
            print(f"[MISSING_OBJECT x{item['count']}] {item['record']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
