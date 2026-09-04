#!/usr/bin/env python3
"""Remove Empress mob-skill references that stock v83 cannot execute safely.

EverLeaf authors the Chief Knight/Shinsoo/Cygnus progression as explicit event
phases instead of relying on newer SUMMON MobSkill levels. Any source skill pair
that is not already present in stock-v83 MobSkill data is removed as well.

Run after staging the Empress server XML and before enabling the content.
"""
from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MOB_DIR = ROOT / "wz/Mob.wz"
ENCOUNTER_MOBS = range(8850000, 8850012)

# CI established that only 100/1 from the source-repack reference set exists in
# stock v83. The following pairs are therefore stripped until they are either
# deliberately ported and tested or replaced by EverLeaf-authored mechanics.
# 146 / 170 are unsupported MobSkill types in the current server. 200/221 and
# 200/224 are newer SUMMON levels and are replaced by deterministic event phases.
REMOVE_PAIRS = {
    (100, 25),
    (114, 42),
    (120, 19),
    (146, 1),
    (146, 2),
    (170, 5),
    (200, 221),
    (200, 224),
}


def pair_for(node: ET.Element) -> tuple[int, int] | None:
    values: dict[str, str] = {}
    for child in node:
        if child.tag in {"int", "short", "long"}:
            name = child.attrib.get("name")
            value = child.attrib.get("value")
            if name in {"skill", "level"} and value is not None:
                values[name] = value
    if "skill" not in values or "level" not in values:
        return None
    try:
        return int(values["skill"]), int(values["level"])
    except ValueError:
        return None


def sanitize(path: Path) -> int:
    tree = ET.parse(path)
    root = tree.getroot()
    removed = 0

    for parent in root.iter():
        for child in list(parent):
            if child.tag != "imgdir":
                continue
            pair = pair_for(child)
            if pair in REMOVE_PAIRS:
                parent.remove(child)
                removed += 1

    if removed:
        try:
            ET.indent(tree, space="  ")
        except AttributeError:
            pass
        tree.write(path, encoding="utf-8", xml_declaration=True)
    return removed


def main() -> int:
    total = 0
    missing: list[int] = []
    for mob_id in ENCOUNTER_MOBS:
        path = MOB_DIR / f"{mob_id}.img.xml"
        if not path.is_file():
            missing.append(mob_id)
            continue
        count = sanitize(path)
        total += count
        print(f"{mob_id}: removed {count} incompatible MobSkill reference(s)")

    if missing:
        print(f"[FAIL] encounter XML is not fully staged; missing mobs: {missing}")
        return 1

    print(f"Removed {total} incompatible Empress MobSkill reference(s).")
    print("Chief Knight/Shinsoo/Cygnus phase progression is handled by EmpressBattle.js.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
