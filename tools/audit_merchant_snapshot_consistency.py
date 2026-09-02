#!/usr/bin/env python3
"""Audit Hired Merchant stock snapshot consistency."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "src/main/java/server/maps/HiredMerchant.java"


def main() -> int:
    text = TARGET.read_text(encoding="utf-8")

    required = (
        "return Collections.unmodifiableList(new ArrayList<>(items));",
        "synchronized (items) {\n            for (PlayerShopItem pItems : items)",
        "short newBundle = pItems.getBundles();",
        "Item newItem = pItems.getItem().copy();",
        "itemsWithType.add(new Pair<>(newItem, newItem.getInventoryType()));",
        "bundles.add(newBundle);",
    )
    for fragment in required:
        if fragment not in text:
            raise SystemExit(f"FAIL merchant snapshot invariant missing: {fragment}")

    forbidden = (
        "return Collections.unmodifiableList(items);",
        "for (PlayerShopItem pItems : getItems())",
        "Item newItem = pItems.getItem();",
    )
    for fragment in forbidden:
        if fragment in text:
            raise SystemExit(f"FAIL unsafe merchant snapshot pattern remains: {fragment}")

    lock = text.index("synchronized (items) {\n            for (PlayerShopItem pItems : items)")
    copy = text.index("Item newItem = pItems.getItem().copy();", lock)
    db = text.index("try (Connection con = DatabaseConnection.getConnection())", copy)
    if not lock < copy < db:
        raise SystemExit("FAIL merchant snapshot must be copied under lock before database work")

    print("EverLeaf merchant snapshot consistency audit: PASS")
    print("  public item iteration uses detached list structure")
    print("  persistence bundle counts captured under stock lock")
    print("  mutable items copied under stock lock")
    print("  SQL begins only after point-in-time snapshot capture")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
