#!/usr/bin/env python3
"""Make Hired Merchant stock reads and persistence snapshots concurrency-safe."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "src/main/java/server/maps/HiredMerchant.java"


def replace_once(text: str, old: str, new: str, label: str) -> tuple[str, bool]:
    if new in text:
        print(f"OK already fixed: {label}")
        return text, False
    if old not in text:
        raise SystemExit(f"ERROR expected merchant snapshot snippet not found: {label}")
    print(f"FIXED: {label}")
    return text.replace(old, new, 1), True


def main() -> int:
    text = TARGET.read_text(encoding="utf-8")
    changed = False

    old_get = '''    public List<PlayerShopItem> getItems() {
        synchronized (items) {
            return Collections.unmodifiableList(items);
        }
    }
'''
    new_get = '''    public List<PlayerShopItem> getItems() {
        synchronized (items) {
            return Collections.unmodifiableList(new ArrayList<>(items));
        }
    }
'''
    text, did = replace_once(text, old_get, new_get, "return a detached merchant list snapshot")
    changed |= did

    old_snapshot = '''        for (PlayerShopItem pItems : getItems()) {
            Item newItem = pItems.getItem();
            short newBundle = pItems.getBundles();

            if (shutdown) { //is "shutdown" really necessary?
                newItem.setQuantity(pItems.getItem().getQuantity());
            } else {
                newItem.setQuantity(pItems.getItem().getQuantity());
            }
            if (newBundle > 0) {
                itemsWithType.add(new Pair<>(newItem, newItem.getInventoryType()));
                bundles.add(newBundle);
            }
        }
'''
    new_snapshot = '''        synchronized (items) {
            for (PlayerShopItem pItems : items) {
                short newBundle = pItems.getBundles();
                if (newBundle > 0) {
                    Item newItem = pItems.getItem().copy();
                    newItem.setQuantity(pItems.getItem().getQuantity());
                    itemsWithType.add(new Pair<>(newItem, newItem.getInventoryType()));
                    bundles.add(newBundle);
                }
            }
        }
'''
    text, did = replace_once(text, old_snapshot, new_snapshot, "capture merchant persistence snapshot under stock lock")
    changed |= did

    if changed:
        TARGET.write_text(text, encoding="utf-8")

    final = TARGET.read_text(encoding="utf-8")
    required = (
        "return Collections.unmodifiableList(new ArrayList<>(items));",
        "synchronized (items) {\n            for (PlayerShopItem pItems : items)",
        "Item newItem = pItems.getItem().copy();",
        "short newBundle = pItems.getBundles();",
    )
    for fragment in required:
        if fragment not in final:
            raise SystemExit(f"ERROR merchant snapshot invariant missing: {fragment}")

    forbidden = (
        "return Collections.unmodifiableList(items);",
        "for (PlayerShopItem pItems : getItems())",
        "Item newItem = pItems.getItem();",
    )
    for fragment in forbidden:
        if fragment in final:
            raise SystemExit(f"ERROR unsafe merchant snapshot pattern remains: {fragment}")

    print("EverLeaf merchant snapshot consistency hardening: PASS")
    print("  getItems returns a detached list snapshot")
    print("  persistence captures bundle counts while holding the stock lock")
    print("  persistence copies mutable Item objects while holding the stock lock")
    print("  database work occurs after the stock snapshot is complete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
