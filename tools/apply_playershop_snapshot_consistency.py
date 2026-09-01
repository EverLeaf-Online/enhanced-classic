#!/usr/bin/env python3
"""Make PlayerShop public list snapshots structurally detached from live mutable state."""
from pathlib import Path

from apply_shop_listing_source_integrity import main as apply_listing_source_integrity

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "src/main/java/server/maps/PlayerShop.java"


def replace_once(text: str, old: str, new: str, label: str) -> tuple[str, bool]:
    if new in text:
        print(f"OK already fixed: {label}")
        return text, False
    if old not in text:
        raise SystemExit(f"ERROR expected PlayerShop snapshot snippet not found: {label}")
    print(f"FIXED: {label}")
    return text.replace(old, new, 1), True


def main() -> int:
    text = TARGET.read_text(encoding="utf-8")
    changed = False

    text, did = replace_once(
        text,
        '''    public List<PlayerShopItem> getItems() {\n        synchronized (items) {\n            return Collections.unmodifiableList(items);\n        }\n    }\n''',
        '''    public List<PlayerShopItem> getItems() {\n        synchronized (items) {\n            return Collections.unmodifiableList(new ArrayList<>(items));\n        }\n    }\n''',
        "return detached PlayerShop item-list snapshot",
    )
    changed |= did

    text, did = replace_once(
        text,
        '''    public List<SoldItem> getSold() {\n        synchronized (sold) {\n            return Collections.unmodifiableList(sold);\n        }\n    }\n''',
        '''    public List<SoldItem> getSold() {\n        synchronized (sold) {\n            return Collections.unmodifiableList(new ArrayList<>(sold));\n        }\n    }\n''',
        "return detached PlayerShop sold-list snapshot",
    )
    changed |= did

    if changed:
        TARGET.write_text(text, encoding="utf-8")

    final = TARGET.read_text(encoding="utf-8")
    required = (
        "return Collections.unmodifiableList(new ArrayList<>(items));",
        "return Collections.unmodifiableList(new ArrayList<>(sold));",
    )
    for fragment in required:
        if fragment not in final:
            raise SystemExit(f"ERROR PlayerShop snapshot invariant missing: {fragment}")

    forbidden = (
        "return Collections.unmodifiableList(items);",
        "return Collections.unmodifiableList(sold);",
    )
    for fragment in forbidden:
        if fragment in final:
            raise SystemExit(f"ERROR live PlayerShop list view remains: {fragment}")

    if apply_listing_source_integrity() != 0:
        raise SystemExit("ERROR shop listing source integrity transform failed")

    print("EverLeaf PlayerShop snapshot consistency hardening: PASS")
    print("  getItems returns a detached list structure captured under lock")
    print("  getSold returns a detached list structure captured under lock")
    print("  readers cannot structurally iterate the live mutable backing lists after lock release")
    print("  shop listing source integrity transform composed into PlayerShop production chain")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
