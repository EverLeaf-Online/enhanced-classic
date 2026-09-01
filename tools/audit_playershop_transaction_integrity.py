#!/usr/bin/env python3
"""Audit PlayerShop packet-boundary and transaction arithmetic hardening."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "src/main/java/server/maps/PlayerShop.java"


def main() -> int:
    text = TARGET.read_text(encoding="utf-8")

    required = (
        "if (slot < 0 || slot >= items.size())",
        "long totalQuantity = (long) shopItem.getItem().getQuantity() * shopItem.getBundles();",
        "if (!InventoryManipulator.addFromDrop(chr.getClient(), iitem, true))",
        "if (item < 0 || item >= items.size())",
        "if (quantity < 1 || !pItem.isExist() || pItem.getBundles() < quantity)",
        "long totalQuantity = (long) pItem.getItem().getQuantity() * quantity;",
        "if (totalQuantity <= 0 || totalQuantity > Short.MAX_VALUE)",
        "newItem.setQuantity((short) totalQuantity);",
        "long grossPrice = (long) pItem.getPrice() * quantity;",
        "if (grossPrice <= 0 || grossPrice > Integer.MAX_VALUE)",
    )
    for fragment in required:
        if fragment not in text:
            raise SystemExit(f"FAIL PlayerShop invariant missing: {fragment}")

    forbidden = (
        "newItem.setQuantity((short) ((pItem.getItem().getQuantity() * quantity)))",
        "iitem.setQuantity((short) (shopItem.getItem().getQuantity() * shopItem.getBundles()))",
        "int price = (int) Math.min((float) pItem.getPrice() * quantity, Integer.MAX_VALUE);",
    )
    for fragment in forbidden:
        if fragment in text:
            raise SystemExit(f"FAIL unsafe PlayerShop pattern remains: {fragment}")

    buy_slot = text.index("if (item < 0 || item >= items.size())")
    buy_deref = text.index("PlayerShopItem pItem = items.get(item);", buy_slot)
    buy_validate = text.index("if (quantity < 1 || !pItem.isExist() || pItem.getBundles() < quantity)", buy_deref)
    buy_multiply = text.index("long totalQuantity = (long) pItem.getItem().getQuantity() * quantity;", buy_validate)
    buy_guard = text.index("if (totalQuantity <= 0 || totalQuantity > Short.MAX_VALUE)", buy_multiply)
    buy_cast = text.index("newItem.setQuantity((short) totalQuantity);", buy_guard)
    if not buy_slot < buy_deref < buy_validate < buy_multiply < buy_guard < buy_cast:
        raise SystemExit("FAIL PlayerShop buy validation ordering is unsafe")

    take_slot = text.index("if (slot < 0 || slot >= items.size())")
    take_deref = text.index("PlayerShopItem shopItem = items.get(slot);", take_slot)
    take_add = text.index("if (!InventoryManipulator.addFromDrop(chr.getClient(), iitem, true))", take_deref)
    take_remove = text.index("removeFromSlot(slot);", take_add)
    if not take_slot < take_deref < take_add < take_remove:
        raise SystemExit("FAIL PlayerShop take-back insertion/removal ordering is unsafe")

    print("EverLeaf PlayerShop transaction integrity audit: PASS")
    print("  forged buy/take-back slot indices fail closed")
    print("  quantity arithmetic is range checked before short casts")
    print("  purchase price arithmetic is range checked before int cast")
    print("  failed take-back insertion preserves shop stock")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
