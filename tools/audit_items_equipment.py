#!/usr/bin/env python3
"""Static EverLeaf audit for item/equipment safety and data integrity.

This is intentionally release-facing and conservative. It validates the item-family
boundaries and scrolling safety guards used by packet handlers, then inventories the
v83 equipment data shipped in Character.wz and rejects duplicate or mismatched item
files. Empress-development content is outside this audit.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ITEM_CONSTANTS = ROOT / "src/main/java/constants/inventory/ItemConstants.java"
SCROLL_HANDLER = ROOT / "src/main/java/net/server/channel/handlers/ScrollHandler.java"
CHARACTER_WZ = ROOT / "wz/Character.wz"

EQUIP_FILE_RE = re.compile(r"^(01\d{6})\.img\.xml$")
ROOT_NAME_RE = re.compile(r'<imgdir\s+name="(01\d{6})\.img">')


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def require_fragment(text: str, fragment: str, label: str) -> None:
    if fragment not in text:
        print(f"ERROR {label}: missing required guard: {fragment}")
        raise SystemExit(1)


def audit_item_family_guards() -> None:
    text = read(ITEM_CONSTANTS)
    require_fragment(
        text,
        "return itemId >= 2030000 && itemId < 2040000;",
        "ItemConstants.isTownScroll",
    )
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

    target_guard = text.index("if (toScroll == null)")
    target_deref = text.index("byte oldLevel = toScroll.getLevel();")
    if target_guard > target_deref:
        print("ERROR ScrollHandler target validation occurs after equipment dereference")
        raise SystemExit(1)

    scroll_guard = text.index("if (scroll == null || scroll.getQuantity() < 1)")
    scroll_apply = text.index("ii.scrollEquipWithId")
    if scroll_guard > scroll_apply:
        print("ERROR ScrollHandler scroll validation occurs after scroll application")
        raise SystemExit(1)


def audit_equipment_wz() -> tuple[int, int]:
    if not CHARACTER_WZ.is_dir():
        print("ERROR Character.wz equipment data directory is missing")
        raise SystemExit(1)

    by_id: dict[int, Path] = {}
    mismatched: list[tuple[Path, str]] = []
    category_counts: dict[str, int] = {}

    for path in CHARACTER_WZ.rglob("*.img.xml"):
        match = EQUIP_FILE_RE.match(path.name)
        if not match:
            continue

        raw = match.group(1)
        item_id = int(raw)
        relative = path.relative_to(ROOT)
        previous = by_id.get(item_id)
        if previous is not None:
            print(f"ERROR duplicate equipment id {item_id}: {previous} / {relative}")
            raise SystemExit(1)
        by_id[item_id] = relative

        header = read(path)[:512]
        root_match = ROOT_NAME_RE.search(header)
        if root_match is None or root_match.group(1) != raw:
            mismatched.append((relative, raw))

        category = path.parent.name
        category_counts[category] = category_counts.get(category, 0) + 1

    if mismatched:
        print("ERROR equipment WZ filename/root-name mismatches:")
        for path, raw in mismatched[:50]:
            print(f"  {path}: expected root {raw}.img")
        if len(mismatched) > 50:
            print(f"  ... and {len(mismatched) - 50} more")
        raise SystemExit(1)

    # A release missing most equipment data should fail loudly instead of compiling
    # into a superficially healthy server.
    if len(by_id) < 1000:
        print(f"ERROR suspiciously small equipment WZ inventory: {len(by_id)} files")
        raise SystemExit(1)

    return len(by_id), len(category_counts)


def main() -> int:
    audit_item_family_guards()
    audit_scroll_packet_guards()
    equipment_count, category_count = audit_equipment_wz()

    print("EverLeaf items/equipment integrity audit: PASS")
    print("  town-scroll family: bounded to 203xxxx")
    print("  scroll target/item/White Scroll validation: present")
    print("  scroll/equipment compatibility gate: present")
    print(f"  Character.wz equipment files indexed: {equipment_count}")
    print(f"  Character.wz equipment categories indexed: {category_count}")
    print("  duplicate/mismatched equipment WZ IDs: none")
    return 0


if __name__ == "__main__":
    sys.exit(main())
