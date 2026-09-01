#!/usr/bin/env python3
"""Apply deterministic EverLeaf item-stack integrity fixes.

Stack merges must not collapse items with different expiration timestamps into a
single stack. Doing so can silently extend or shorten timed items. This transform
also fails closed when WZ slotMax data resolves to zero/negative values, avoiding
non-progressing stack loops on malformed item data.
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "src/main/java/client/inventory/manipulator/InventoryManipulator.java"


def replace_once(text: str, old: str, new: str, label: str) -> tuple[str, bool]:
    if new in text:
        print(f"OK already fixed: {label}")
        return text, False
    if old not in text:
        raise SystemExit(f"ERROR expected item-stack snippet not found: {label}")
    print(f"FIXED: {label}")
    return text.replace(old, new, 1), True


def main() -> int:
    text = TARGET.read_text(encoding="utf-8")
    changed = False

    old_add = """        if (!type.equals(InventoryType.EQUIP)) {
            short slotMax = ii.getSlotMax(c, itemId);
            List<Item> existing = inv.listById(itemId);
            if (!ItemConstants.isRechargeable(itemId) && petid == -1) {
"""
    new_add = """        if (!type.equals(InventoryType.EQUIP)) {
            short slotMax = ii.getSlotMax(c, itemId);
            if (slotMax <= 0) {
                log.warn(\"Refusing to add item {} with invalid slotMax {}\", itemId, slotMax);
                c.sendPacket(PacketCreator.enableActions());
                return false;
            }
            long stackExpiration = !ItemConstants.isPermanentItem(itemId)
                    ? expiration
                    : ItemConstants.isPet(itemId) ? Long.MAX_VALUE : -1L;
            List<Item> existing = inv.listById(itemId);
            if (!ItemConstants.isRechargeable(itemId) && petid == -1) {
"""
    text, did = replace_once(text, old_add, new_add, "addById slotMax + expiration normalization")
    changed |= did

    old_add_merge = """                            if (oldQ < slotMax && ((eItem.getOwner().equals(owner) || owner == null) && eItem.getFlag() == flag)) {
                                short newQ = (short) Math.min(oldQ + quantity, slotMax);
"""
    new_add_merge = """                            if (oldQ < slotMax
                                    && (eItem.getOwner().equals(owner) || owner == null)
                                    && eItem.getFlag() == flag
                                    && eItem.getExpiration() == stackExpiration) {
                                short newQ = (short) Math.min(oldQ + quantity, slotMax);
"""
    text, did = replace_once(text, old_add_merge, new_add_merge, "addById expiration-compatible stacking")
    changed |= did

    old_drop = """        if (!type.equals(InventoryType.EQUIP)) {
            short slotMax = ii.getSlotMax(c, itemid);
            List<Item> existing = inv.listById(itemid);
            if (!ItemConstants.isRechargeable(itemid) && petId == -1) {
"""
    new_drop = """        if (!type.equals(InventoryType.EQUIP)) {
            short slotMax = ii.getSlotMax(c, itemid);
            if (slotMax <= 0) {
                log.warn(\"Refusing to add dropped item {} with invalid slotMax {}\", itemid, slotMax);
                c.sendPacket(PacketCreator.enableActions());
                return false;
            }
            List<Item> existing = inv.listById(itemid);
            if (!ItemConstants.isRechargeable(itemid) && petId == -1) {
"""
    text, did = replace_once(text, old_drop, new_drop, "addFromDrop slotMax guard")
    changed |= did

    old_drop_merge = """                            if (oldQ < slotMax && item.getFlag() == eItem.getFlag() && item.getOwner().equals(eItem.getOwner())) {
                                short newQ = (short) Math.min(oldQ + quantity, slotMax);
"""
    new_drop_merge = """                            if (oldQ < slotMax
                                    && item.getFlag() == eItem.getFlag()
                                    && item.getOwner().equals(eItem.getOwner())
                                    && item.getExpiration() == eItem.getExpiration()) {
                                short newQ = (short) Math.min(oldQ + quantity, slotMax);
"""
    text, did = replace_once(text, old_drop_merge, new_drop_merge, "addFromDrop expiration-compatible stacking")
    changed |= did

    if changed:
        TARGET.write_text(text, encoding="utf-8")

    final = TARGET.read_text(encoding="utf-8")
    required = (
        "if (slotMax <= 0)",
        "ItemConstants.isPet(itemId) ? Long.MAX_VALUE : -1L",
        "eItem.getExpiration() == stackExpiration",
        "item.getExpiration() == eItem.getExpiration()",
    )
    for fragment in required:
        if fragment not in final:
            raise SystemExit(f"ERROR item-stack invariant missing: {fragment}")
    if final.count("if (slotMax <= 0)") < 2:
        raise SystemExit("ERROR expected slotMax fail-closed guards in addById and addFromDrop")

    print("EverLeaf item stack integrity fixes: PASS")
    print("  timed stacks merge only with identical expirations")
    print("  permanent item expiration normalization mirrors Item.setExpiration")
    print("  malformed zero/negative slotMax values fail closed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
