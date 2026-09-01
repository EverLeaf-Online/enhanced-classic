#!/usr/bin/env python3
"""Apply canonical EverLeaf equipment-requirement enforcement.

The packet handler already rejects packet-edited reqJob violations, but the shared
ItemInformationProvider.canWearEquipment() paths historically had their job checks
commented out. Enforce the same WZ reqJob mask in the canonical validator so every
caller receives the same protection, while retaining the packet-layer check as
defense in depth.
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "src/main/java/server/ItemInformationProvider.java"


def replace_once(text: str, old: str, new: str, label: str) -> tuple[str, bool]:
    if new in text:
        print(f"OK already fixed: {label}")
        return text, False
    if old not in text:
        raise SystemExit(f"ERROR expected equipment-requirement snippet not found: {label}")
    print(f"FIXED: {label}")
    return text.replace(old, new, 1), True


def main() -> int:
    text = TARGET.read_text(encoding="utf-8")
    changed = False

    old_import = "import constants.inventory.EquipSlot;\nimport constants.inventory.ItemConstants;"
    new_import = "import constants.inventory.EquipSlot;\nimport constants.inventory.EquipmentRequirements;\nimport constants.inventory.ItemConstants;"
    text, did = replace_once(text, old_import, new_import, "EquipmentRequirements import")
    changed |= did

    old_collection = """            /*
             int reqJob = getEquipStats(equip.getItemId()).get(\"reqJob\");
             if (reqJob != 0) {
             Really hard check, and not really needed in this one
             Gm's should just be GM job, and players cannot change jobs.
             }*/
            if (reqLevel > chr.getLevel()) {
"""
    new_collection = """            Map<String, Integer> equipStats = getEquipStats(equip.getItemId());
            if (equipStats == null || !EquipmentRequirements.canEquipForJob(chr.getJob(), equipStats.getOrDefault(\"reqJob\", 0))) {
                continue;
            }
            if (reqLevel > chr.getLevel()) {
"""
    text, did = replace_once(text, old_collection, new_collection, "collection equip reqJob enforcement")
    changed |= did

    old_single = """        int i = 0; //lol xD
        //Removed job check. Shouldn't really be needed.
        if (reqLevel > chr.getLevel()) {
"""
    new_single = """        Map<String, Integer> equipStats = getEquipStats(equip.getItemId());
        if (equipStats == null || !EquipmentRequirements.canEquipForJob(chr.getJob(), equipStats.getOrDefault(\"reqJob\", 0))) {
            equip.wear(false);
            return false;
        }

        int i = 0; //lol xD
        if (reqLevel > chr.getLevel()) {
"""
    text, did = replace_once(text, old_single, new_single, "single equip reqJob enforcement")
    changed |= did

    if changed:
        TARGET.write_text(text, encoding="utf-8")

    final = TARGET.read_text(encoding="utf-8")
    required = (
        "import constants.inventory.EquipmentRequirements;",
        "!EquipmentRequirements.canEquipForJob(chr.getJob(), equipStats.getOrDefault(\"reqJob\", 0))",
        "Map<String, Integer> equipStats = getEquipStats(equip.getItemId());",
    )
    for fragment in required:
        if fragment not in final:
            raise SystemExit(f"ERROR equipment requirement invariant missing: {fragment}")

    if final.count("!EquipmentRequirements.canEquipForJob(chr.getJob(), equipStats.getOrDefault(\"reqJob\", 0))") < 2:
        raise SystemExit("ERROR expected reqJob enforcement in both canWearEquipment paths")
    if "//Removed job check. Shouldn't really be needed." in final:
        raise SystemExit("ERROR stale single-item job bypass comment remains")
    if "Really hard check, and not really needed in this one" in final:
        raise SystemExit("ERROR stale collection job bypass remains")

    print("EverLeaf canonical equipment requirement fixes: PASS")
    print("  collection canWearEquipment reqJob: enforced")
    print("  single-item canWearEquipment reqJob: enforced")
    print("  ItemMoveHandler reqJob gate remains defense in depth")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
