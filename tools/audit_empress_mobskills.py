#!/usr/bin/env python3
"""Audit MobSkill compatibility for EverLeaf's imported Empress encounter.

The source repack references a mixture of stock-v83 skills, newer skill types,
and high SUMMON levels. This audit distinguishes them so the encounter cannot
be enabled with a mob skill that the v83 server cannot interpret.
"""
from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MOB_DIR = ROOT / "wz/Mob.wz"
MOBSKILL = ROOT / "wz/Skill.wz/MobSkill.img.xml"
MOBSKILL_TYPE = ROOT / "src/main/java/server/life/MobSkillType.java"

# Exact source-repack references discovered from 8850000-8850011.
SOURCE_REQUIRED = {
    (100, 1),
    (100, 25),
    (114, 42),
    (120, 19),
    (146, 1),
    (146, 2),
    (170, 5),
    (200, 221),
    (200, 224),
}
ENCOUNTER_MOBS = range(8850000, 8850012)


def parse_supported_types() -> set[int]:
    text = MOBSKILL_TYPE.read_text(encoding="utf-8-sig", errors="replace")
    return {int(v) for v in re.findall(r"^[ \t]*[A-Z0-9_]+\((\d+)\)[,;]", text, re.MULTILINE)}


def parse_stock_pairs() -> set[tuple[int, int]]:
    tree = ET.parse(MOBSKILL)
    root = tree.getroot()
    pairs: set[tuple[int, int]] = set()
    for skill in root.findall("imgdir"):
        try:
            skill_id = int(skill.attrib.get("name", ""))
        except ValueError:
            continue
        level_dir = next((c for c in skill.findall("imgdir") if c.attrib.get("name") == "level"), None)
        if level_dir is None:
            continue
        for level in level_dir.findall("imgdir"):
            try:
                pairs.add((skill_id, int(level.attrib.get("name", ""))))
            except ValueError:
                pass
    return pairs


def staged_references() -> dict[int, set[tuple[int, int]]]:
    out: dict[int, set[tuple[int, int]]] = {}
    for mob_id in ENCOUNTER_MOBS:
        path = MOB_DIR / f"{mob_id}.img.xml"
        if not path.is_file():
            continue
        tree = ET.parse(path)
        refs: set[tuple[int, int]] = set()
        for node in tree.getroot().iter("imgdir"):
            # Monster skill entries conventionally contain int children named
            # 'skill' and 'level'. Keep this deliberately schema-light.
            ints = {c.attrib.get("name"): c.attrib.get("value") for c in node if c.tag in {"int", "short", "long"}}
            if "skill" in ints and "level" in ints:
                try:
                    refs.add((int(ints["skill"]), int(ints["level"])))
                except (TypeError, ValueError):
                    pass
        out[mob_id] = refs
    return out


def main() -> int:
    supported = parse_supported_types()
    stock = parse_stock_pairs()
    unsupported_types = sorted(p for p in SOURCE_REQUIRED if p[0] not in supported)
    missing_stock = sorted(p for p in SOURCE_REQUIRED if p[0] in supported and p not in stock)
    available = sorted(p for p in SOURCE_REQUIRED if p in stock and p[0] in supported)

    print("EverLeaf Empress MobSkill audit")
    print(f"Source references: {len(SOURCE_REQUIRED)}")
    print(f"Stock-v83 compatible now: {available}")
    print(f"Supported type but missing stock level: {missing_stock}")
    print(f"Unsupported v83 skill types (must be removed/replaced): {unsupported_types}")

    staged = staged_references()
    if not staged:
        print("No Empress encounter mob XML staged; compatibility findings are planning-only.")
        return 0

    failures: list[str] = []
    for mob_id, refs in staged.items():
        for pair in sorted(refs):
            skill_id, level = pair
            if skill_id not in supported:
                failures.append(f"mob {mob_id} references unsupported MobSkill type {skill_id} level {level}")
            elif pair not in stock:
                failures.append(f"mob {mob_id} references missing MobSkill {skill_id} level {level}")

    if failures:
        for failure in failures:
            print(f"[FAIL] {failure}")
        print("Run the Empress mob-skill compatibility transform/import before enabling content.")
        return 1

    print("Staged Empress mob-skill references are v83-compatible: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
