#!/usr/bin/env python3
"""Harden Hired Merchant purchase quantity validation against short overflow/wrap."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "src/main/java/server/maps/HiredMerchant.java"


def main() -> int:
    text = TARGET.read_text(encoding="utf-8")

    old = '''            PlayerShopItem pItem = items.get(item);
            Item newItem = pItem.getItem().copy();

            newItem.setQuantity((short) ((pItem.getItem().getQuantity() * quantity)));
            if (quantity < 1 || !pItem.isExist() || pItem.getBundles() < quantity) {
                c.sendPacket(PacketCreator.enableActions());
                return;
            } else if (newItem.getInventoryType().equals(InventoryType.EQUIP) && newItem.getQuantity() > 1) {
'''
    new = '''            PlayerShopItem pItem = items.get(item);
            if (quantity < 1 || !pItem.isExist() || pItem.getBundles() < quantity) {
                c.sendPacket(PacketCreator.enableActions());
                return;
            }

            long totalQuantity = (long) pItem.getItem().getQuantity() * quantity;
            if (totalQuantity <= 0 || totalQuantity > Short.MAX_VALUE) {
                c.sendPacket(PacketCreator.enableActions());
                return;
            }

            Item newItem = pItem.getItem().copy();
            newItem.setQuantity((short) totalQuantity);
            if (newItem.getInventoryType().equals(InventoryType.EQUIP) && newItem.getQuantity() > 1) {
'''

    if new in text:
        print("OK already fixed: merchant purchase quantity arithmetic")
    elif old in text:
        text = text.replace(old, new, 1)
        TARGET.write_text(text, encoding="utf-8")
        print("FIXED: merchant purchase quantity arithmetic")
    else:
        raise SystemExit("ERROR expected Hired Merchant purchase quantity block not found")

    final = TARGET.read_text(encoding="utf-8")
    required = (
        "if (quantity < 1 || !pItem.isExist() || pItem.getBundles() < quantity)",
        "long totalQuantity = (long) pItem.getItem().getQuantity() * quantity;",
        "if (totalQuantity <= 0 || totalQuantity > Short.MAX_VALUE)",
        "newItem.setQuantity((short) totalQuantity);",
    )
    for fragment in required:
        if fragment not in final:
            raise SystemExit(f"ERROR merchant purchase quantity invariant missing: {fragment}")

    forbidden = (
        "newItem.setQuantity((short) ((pItem.getItem().getQuantity() * quantity)))",
        "newItem.setQuantity((short) (pItem.getItem().getQuantity() * quantity))",
    )
    for fragment in forbidden:
        if fragment in final:
            raise SystemExit("ERROR unchecked short quantity multiplication remains in Hired Merchant purchase path")

    print("EverLeaf merchant purchase quantity hardening: PASS")
    print("  bundle count validated before item-quantity construction")
    print("  item quantity multiplication promoted to long")
    print("  non-positive and >Short.MAX_VALUE totals fail closed")
    print("  short cast occurs only after range validation")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
