#!/usr/bin/env python3
"""Static EverLeaf audit for item/equipment safety and data integrity.

Release-facing checks cover packet guards, canonical equipment requirement
validation, and the v83 Character.wz equipment corpus. Empress-development
content is outside this audit.
"""

from __future__ import annotations

import re
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ITEM_CONSTANTS = ROOT / "src/main/java/constants/inventory/ItemConstants.java"
EQUIP_REQUIREMENTS = ROOT / "src/main/java/constants/inventory/EquipmentRequirements.java"
ITEM_INFO = ROOT / "src/main/java/server/ItemInformationProvider.java"
SCROLL_HANDLER = ROOT / "src/main/java/net/server/channel/handlers/ScrollHandler.java"
ITEM_MOVE_HANDLER = ROOT / "src/main/java/net/server/channel/handlers/ItemMoveHandler.java"
CHARACTER_WZ = ROOT / "wz/Character.wz"

EQUIP_FILE_RE = re.compile(r"^(01\d{6})\.img\.xml$")
ROOT_NAME_RE = re.compile(r'<imgdir\s+name="(01\d{6})\.img">')
REQ_FIELDS = ("reqJob", "reqLevel", "reqSTR", "reqDEX", "reqINT", "reqLUK", "reqPOP")
STAT_REQ_FIELDS = ("reqSTR", "reqDEX", "reqINT", "reqLUK")
VALID_REQ_JOB_BITS = 0x1F


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def require_fragment(text: str, fragment: str, label: str) -> None:
    if fragment not in text:
        print(f"ERROR {label}: missing required guard: {fragment}")
        raise SystemExit(1)


def audit_item_family_guards() -> None:
    text = read(ITEM_CONSTANTS)
    require_fragment(text, "return itemId >= 2030000 && itemId < 2040000;", "ItemConstants.isTownScroll")
    require_fragment(text, "return itemId / 10000 == 207;", "throwing-star family")
    require_fragment(text, "return itemId / 10000 == 233;", "bullet family")
    require_fragment(text, "return scrollId > 2048999 && scrollId < 2049004;", "Clean Slate family")
    require_fragment(text, "return scrollId >= 2049100 && scrollId <= 2049103;", "Chaos Scroll family")


def audit_scroll_packet_guards() -> None:
    text = read(SCROLL_HANDLER)
    required = (
        "if (toScroll == null)",
        "if (scroll == null || scroll.getQuantity() < 1)",
        "if (wscroll == null || wscroll.getQuantity() < 1)",
        "if (!canScroll(scroll.getItemId(), toScroll.getItemId()))",
        "useInventory.lockInventory();",
    )
    for fragment in required:
        require_fragment(text, fragment, "ScrollHandler")

    if text.index("if (toScroll == null)") > text.index("byte oldLevel = toScroll.getLevel();"):
        raise SystemExit("ERROR ScrollHandler target validation occurs after equipment dereference")
    if text.index("if (scroll == null || scroll.getQuantity() < 1)") > text.index("ii.scrollEquipWithId"):
        raise SystemExit("ERROR ScrollHandler scroll validation occurs after scroll application")


def audit_inventory_move_guards() -> None:
    text = read(ITEM_MOVE_HANDLER)
    required = (
        "type == null",
        "type == InventoryType.UNDEFINED",
        "type == InventoryType.CANHOLD",
        "type == InventoryType.EQUIPPED",
        "if (action == 0 && quantity <= 0)",
        "if (type != InventoryType.EQUIP)",
        "candidate instanceof Equip equip",
        "EquipmentRequirements.canEquipForJob(chr.getJob(), stats.getOrDefault(\"reqJob\", 0))",
        "c.sendPacket(PacketCreator.enableActions());",
    )
    for fragment in required:
        require_fragment(text, fragment, "ItemMoveHandler")

    type_guard = text.index("if (type == null")
    first_manipulator = min(
        text.index("InventoryManipulator.unequip"),
        text.index("InventoryManipulator.equip"),
        text.index("InventoryManipulator.drop"),
        text.index("InventoryManipulator.move"),
    )
    if type_guard > first_manipulator:
        raise SystemExit("ERROR ItemMoveHandler inventory-type validation occurs after mutation")

    job_guard = text.index("EquipmentRequirements.canEquipForJob")
    equip_mutation = text.index("InventoryManipulator.equip(c, src, action)")
    if job_guard > equip_mutation:
        raise SystemExit("ERROR ItemMoveHandler reqJob validation occurs after equip mutation")


def audit_canonical_requirement_guards() -> None:
    helper = read(EQUIP_REQUIREMENTS)
    for fragment in (
        "warrior=1, magician=2, bowman=4, thief=8, pirate=16",
        "if (reqJobMask == 0)",
        "if (job == Job.GM || job == Job.SUPERGM)",
        "int familyMask = 1 << (niche - 1);",
        "return (reqJobMask & familyMask) != 0;",
    ):
        require_fragment(helper, fragment, "EquipmentRequirements")

    provider = read(ITEM_INFO)
    canonical_guard = "!EquipmentRequirements.canEquipForJob(chr.getJob(), equipStats.getOrDefault(\"reqJob\", 0))"
    require_fragment(provider, "import constants.inventory.EquipmentRequirements;", "ItemInformationProvider")
    if provider.count(canonical_guard) < 2:
        raise SystemExit("ERROR canonical reqJob validation is not present in both canWearEquipment paths")
    if "//Removed job check. Shouldn't really be needed." in provider:
        raise SystemExit("ERROR stale single-item reqJob bypass remains")
    if "Really hard check, and not really needed in this one" in provider:
        raise SystemExit("ERROR stale collection reqJob bypass remains")

    require_fragment(provider, "getEquipLevelReq(equip.getItemId())", "ItemInformationProvider reqLevel")
    for field in ("reqDEX", "reqSTR", "reqLUK", "reqINT", "reqPOP"):
        require_fragment(provider, f'get("{field}")', f"ItemInformationProvider {field}")


def parse_info_ints(path: Path) -> dict[str, int]:
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError as exc:
        raise SystemExit(f"ERROR malformed equipment XML {path.relative_to(ROOT)}: {exc}")

    info = None
    for child in root:
        if child.tag == "imgdir" and child.attrib.get("name") == "info":
            info = child
            break
    if info is None:
        return {}

    values: dict[str, int] = {}
    for child in info:
        name = child.attrib.get("name")
        if child.tag not in {"int", "short", "long"} or not name:
            continue
        raw = child.attrib.get("value")
        if raw is None:
            continue
        try:
            values[name] = int(raw)
        except ValueError:
            raise SystemExit(f"ERROR non-integer equipment field {path.relative_to(ROOT)} {name}={raw!r}")
    return values


def audit_requirement_values(path: Path, values: dict[str, int], counts: Counter[str], maxima: dict[str, int]) -> None:
    relative = path.relative_to(ROOT)
    req_job = values.get("reqJob", 0)
    if req_job < 0 or req_job & ~VALID_REQ_JOB_BITS:
        raise SystemExit(f"ERROR invalid reqJob mask {req_job} in {relative}; expected only bits 1/2/4/8/16")

    req_level = values.get("reqLevel", 0)
    if req_level < 0 or req_level > 250:
        raise SystemExit(f"ERROR invalid reqLevel {req_level} in {relative}; EverLeaf range is 0..250")

    for field in STAT_REQ_FIELDS:
        value = values.get(field, 0)
        if value < 0 or value > 32767:
            raise SystemExit(f"ERROR invalid {field}={value} in {relative}")

    req_pop = values.get("reqPOP", 0)
    if req_pop < 0 or req_pop > 32767:
        raise SystemExit(f"ERROR invalid reqPOP={req_pop} in {relative}")

    if "gender" in values and values["gender"] not in (0, 1, 2):
        raise SystemExit(f"ERROR invalid gender={values['gender']} in {relative}")

    for field in REQ_FIELDS:
        value = values.get(field, 0)
        if value:
            counts[field] += 1
        maxima[field] = max(maxima.get(field, 0), value)
    if "gender" in values:
        counts["gender"] += 1


def audit_equipment_wz() -> tuple[int, int, Counter[str], dict[str, int]]:
    if not CHARACTER_WZ.is_dir():
        raise SystemExit("ERROR Character.wz equipment data directory is missing")

    by_id: dict[int, Path] = {}
    mismatched: list[tuple[Path, str]] = []
    category_counts: dict[str, int] = {}
    requirement_counts: Counter[str] = Counter()
    maxima: dict[str, int] = {}

    for path in CHARACTER_WZ.rglob("*.img.xml"):
        match = EQUIP_FILE_RE.match(path.name)
        if not match:
            continue

        raw = match.group(1)
        item_id = int(raw)
        relative = path.relative_to(ROOT)
        previous = by_id.get(item_id)
        if previous is not None:
            raise SystemExit(f"ERROR duplicate equipment id {item_id}: {previous} / {relative}")
        by_id[item_id] = relative

        header = read(path)[:512]
        root_match = ROOT_NAME_RE.search(header)
        if root_match is None or root_match.group(1) != raw:
            mismatched.append((relative, raw))

        category_counts[path.parent.name] = category_counts.get(path.parent.name, 0) + 1
        audit_requirement_values(path, parse_info_ints(path), requirement_counts, maxima)

    if mismatched:
        print("ERROR equipment WZ filename/root-name mismatches:")
        for path, raw in mismatched[:50]:
            print(f"  {path}: expected root {raw}.img")
        if len(mismatched) > 50:
            print(f"  ... and {len(mismatched) - 50} more")
        raise SystemExit(1)

    if len(by_id) < 1000:
        raise SystemExit(f"ERROR suspiciously small equipment WZ inventory: {len(by_id)} files")

    return len(by_id), len(category_counts), requirement_counts, maxima


def main() -> int:
    audit_item_family_guards()
    audit_scroll_packet_guards()
    audit_inventory_move_guards()
    audit_canonical_requirement_guards()
    equipment_count, category_count, requirement_counts, maxima = audit_equipment_wz()

    print("EverLeaf items/equipment integrity audit: PASS")
    print("  town-scroll family: bounded to 203xxxx")
    print("  scroll target/item/White Scroll validation: present")
    print("  scroll/equipment compatibility gate: present")
    print("  inventory type/drop quantity packet guards: present")
    print("  reqJob: packet boundary + canonical canWearEquipment enforcement")
    print("  reqLevel/STR/DEX/INT/LUK/POP: canonical enforcement present")
    print(f"  Character.wz equipment files indexed: {equipment_count}")
    print(f"  Character.wz equipment categories indexed: {category_count}")
    print("  duplicate/mismatched equipment WZ IDs: none")
    print("  requirement-bearing equips: " + ", ".join(f"{k}={requirement_counts[k]}" for k in REQ_FIELDS))
    print("  requirement maxima: " + ", ".join(f"{k}={maxima.get(k, 0)}" for k in REQ_FIELDS))
    if requirement_counts.get("gender"):
        print(f"  explicit gender-tagged equips: {requirement_counts['gender']}")
    else:
        print("  explicit gender-tagged equips: 0 (no Character.wz gender node in indexed equipment)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
