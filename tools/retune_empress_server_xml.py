#!/usr/bin/env python3
"""Retune imported Empress mob XML for EverLeaf's level-180 progression bridge.

Run only after tools/stage_empress_server_xml.py has staged the selected server
XML package. The source repack gives the Chief Knights/Shinsoo/Cygnus roughly
2.1B HP each and contains several level values that do not make sense in v83.
This transform replaces only the small set of combat fields below.
"""
from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MOB_DIR = ROOT / "wz/Mob.wz"

# Provisional pre-alpha values. These are deliberately below the source repack's
# 2.1B-per-body values and should be tuned with private 3/6/12-player telemetry.
TARGETS = {
    8850000: dict(level=185, maxHP=120_000_000, exp=1_000_000, PADamage=2500, MADamage=2300),
    8850001: dict(level=185, maxHP=120_000_000, exp=1_000_000, PADamage=2500, MADamage=2300),
    8850002: dict(level=185, maxHP=120_000_000, exp=1_000_000, PADamage=2500, MADamage=2300),
    8850003: dict(level=185, maxHP=120_000_000, exp=1_000_000, PADamage=2500, MADamage=2300),
    8850004: dict(level=185, maxHP=120_000_000, exp=1_000_000, PADamage=2500, MADamage=2300),
    8850005: dict(level=190, maxHP=180_000_000, exp=1_500_000, PADamage=3200, MADamage=3000),
    8850006: dict(level=190, maxHP=180_000_000, exp=1_500_000, PADamage=3200, MADamage=3000),
    8850007: dict(level=190, maxHP=180_000_000, exp=1_500_000, PADamage=3200, MADamage=3000),
    8850008: dict(level=190, maxHP=180_000_000, exp=1_500_000, PADamage=3200, MADamage=3000),
    8850009: dict(level=190, maxHP=180_000_000, exp=1_500_000, PADamage=3200, MADamage=3000),
    8850010: dict(level=195, maxHP=250_000_000, exp=0, PADamage=3500, MADamage=3300),
    8850011: dict(level=200, maxHP=800_000_000, exp=10_000_000, PADamage=4200, MADamage=4000),
}

# The repack's 8610013 level value is anomalous between level-180 and level-184
# Stronghold mobs. Normalize it to the expected progression step.
FIELD_FIXES = {
    8610013: dict(level=182),
}


def info_node(root: ET.Element) -> ET.Element:
    for node in root.iter("imgdir"):
        if node.attrib.get("name") == "info":
            return node
    raise ValueError("mob XML has no info node")


def set_value(info: ET.Element, key: str, value: int) -> None:
    for child in info:
        if child.attrib.get("name") == key and child.tag in {"int", "long", "short"}:
            child.set("value", str(value))
            return
    ET.SubElement(info, "int", {"name": key, "value": str(value)})


def retune(mob_id: int, values: dict[str, int]) -> None:
    path = MOB_DIR / f"{mob_id}.img.xml"
    if not path.is_file():
        raise FileNotFoundError(f"missing staged mob XML: {path.relative_to(ROOT)}")
    tree = ET.parse(path)
    info = info_node(tree.getroot())
    for key, value in values.items():
        set_value(info, key, value)
    try:
        ET.indent(tree, space="  ")
    except AttributeError:
        pass
    tree.write(path, encoding="utf-8", xml_declaration=True)
    print(f"retuned {mob_id}: {values}")


def main() -> int:
    for mob_id, values in FIELD_FIXES.items():
        retune(mob_id, values)
    for mob_id, values in TARGETS.items():
        retune(mob_id, values)
    print("EverLeaf Empress mob retune complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
