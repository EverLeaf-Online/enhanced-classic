#!/usr/bin/env python3
"""Harden PlayerShop packet boundaries, arithmetic, and take-back settlement."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "src/main/java/server/maps/PlayerShop.java"


def replace_once(text: str, old: str, new: str, label: str) -> tuple[str, bool]:
    if new in text:
        print(f"OK already fixed: {label}")
        return text, False
    if old not in text:
        raise SystemExit(f"ERROR expected PlayerShop snippet not found: {label}")
    print(f"FIXED: {label}")
    return text.replace(old, new, 1), True


def main() -> int:
    text = TARGET.read_text(encoding="utf-8")
    changed = False

    old_take_start = '''    public void takeItemBack(int slot, Character chr) {
        synchronized (items) {
            PlayerShopItem shopItem = items.get(slot);
'''
    new_take_start = '''    public void takeItemBack(int slot, Character chr) {
        synchronized (items) {
            if (slot < 0 || slot >= items.size()) {
                chr.sendPacket(PacketCreator.enableActions());
                return;
            }

            PlayerShopItem shopItem = items.get(slot);
'''
    text, did = replace_once(text, old_take_start, new_take_start, "validate take-back slot before dereference")
    changed |= did

    old_take_qty = '''                    Item iitem = shopItem.getItem().copy();
                    iitem.setQuantity((short) (shopItem.getItem().getQuantity() * shopItem.getBundles()));

                    if (!Inventory.checkSpot(chr, iitem)) {
'''
    new_take_qty = '''                    long totalQuantity = (long) shopItem.getItem().getQuantity() * shopItem.getBundles();
                    if (totalQuantity <= 0 || totalQuantity > Short.MAX_VALUE) {
                        chr.sendPacket(PacketCreator.enableActions());
                        return;
                    }
                    Item iitem = shopItem.getItem().copy();
                    iitem.setQuantity((short) totalQuantity);

                    if (!Inventory.checkSpot(chr, iitem)) {
'''
    text, did = replace_once(text, old_take_qty, new_take_qty, "use overflow-safe take-back quantity")
    changed |= did

    old_take_insert = '''                    InventoryManipulator.addFromDrop(chr.getClient(), iitem, true);
                }

                removeFromSlot(slot);
'''
    new_take_insert = '''                    if (!InventoryManipulator.addFromDrop(chr.getClient(), iitem, true)) {
                        chr.sendPacket(PacketCreator.serverNotice(1, "Unable to return that item right now. Please try again."));
                        chr.sendPacket(PacketCreator.enableActions());
                        return;
                    }
                }

                removeFromSlot(slot);
'''
    text, did = replace_once(text, old_take_insert, new_take_insert, "preserve listing when take-back insertion fails")
    changed |= did

    old_buy_start = '''            if (isVisitor(c.getPlayer())) {
                PlayerShopItem pItem = items.get(item);
                Item newItem = pItem.getItem().copy();

                newItem.setQuantity((short) ((pItem.getItem().getQuantity() * quantity)));
                if (quantity < 1 || !pItem.isExist() || pItem.getBundles() < quantity) {
                    c.sendPacket(PacketCreator.enableActions());
                    return false;
                } else if (newItem.getInventoryType().equals(InventoryType.EQUIP) && newItem.getQuantity() > 1) {
'''
    new_buy_start = '''            if (isVisitor(c.getPlayer())) {
                if (item < 0 || item >= items.size()) {
                    c.sendPacket(PacketCreator.enableActions());
                    return false;
                }

                PlayerShopItem pItem = items.get(item);
                if (quantity < 1 || !pItem.isExist() || pItem.getBundles() < quantity) {
                    c.sendPacket(PacketCreator.enableActions());
                    return false;
                }

                long totalQuantity = (long) pItem.getItem().getQuantity() * quantity;
                if (totalQuantity <= 0 || totalQuantity > Short.MAX_VALUE) {
                    c.sendPacket(PacketCreator.enableActions());
                    return false;
                }

                Item newItem = pItem.getItem().copy();
                newItem.setQuantity((short) totalQuantity);
                if (newItem.getInventoryType().equals(InventoryType.EQUIP) && newItem.getQuantity() > 1) {
'''
    text, did = replace_once(text, old_buy_start, new_buy_start, "validate buy slot and quantity before construction")
    changed |= did

    old_price = '''                    int price = (int) Math.min((float) pItem.getPrice() * quantity, Integer.MAX_VALUE);

                    if (c.getPlayer().getMeso() >= price) {
'''
    new_price = '''                    long grossPrice = (long) pItem.getPrice() * quantity;
                    if (grossPrice <= 0 || grossPrice > Integer.MAX_VALUE) {
                        c.sendPacket(PacketCreator.enableActions());
                        return false;
                    }
                    int price = (int) grossPrice;

                    if (c.getPlayer().getMeso() >= price) {
'''
    text, did = replace_once(text, old_price, new_price, "use overflow-safe positive purchase price")
    changed |= did

    if changed:
        TARGET.write_text(text, encoding="utf-8")

    final = TARGET.read_text(encoding="utf-8")
    required = (
        "if (slot < 0 || slot >= items.size())",
        "long totalQuantity = (long) shopItem.getItem().getQuantity() * shopItem.getBundles();",
        "if (!InventoryManipulator.addFromDrop(chr.getClient(), iitem, true))",
        "if (item < 0 || item >= items.size())",
        "long totalQuantity = (long) pItem.getItem().getQuantity() * quantity;",
        "if (totalQuantity <= 0 || totalQuantity > Short.MAX_VALUE)",
        "long grossPrice = (long) pItem.getPrice() * quantity;",
        "if (grossPrice <= 0 || grossPrice > Integer.MAX_VALUE)",
    )
    for fragment in required:
        if fragment not in final:
            raise SystemExit(f"ERROR PlayerShop invariant missing: {fragment}")

    forbidden = (
        "newItem.setQuantity((short) ((pItem.getItem().getQuantity() * quantity)))",
        "iitem.setQuantity((short) (shopItem.getItem().getQuantity() * shopItem.getBundles()))",
        "int price = (int) Math.min((float) pItem.getPrice() * quantity, Integer.MAX_VALUE);",
    )
    for fragment in forbidden:
        if fragment in final:
            raise SystemExit(f"ERROR unsafe PlayerShop pattern remains: {fragment}")

    print("EverLeaf PlayerShop transaction integrity hardening: PASS")
    print("  buy and take-back slots validated before dereference")
    print("  buy and take-back quantities use checked long arithmetic")
    print("  purchase price uses checked long arithmetic")
    print("  take-back listing survives final inventory insertion failure")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
