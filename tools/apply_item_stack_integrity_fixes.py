#!/usr/bin/env python3
"""Apply deterministic EverLeaf item-stack integrity fixes.

Stack merges must not collapse items with different expiration timestamps into a
single stack. Doing so can silently extend or shorten timed items. This transform
also fails closed when WZ slotMax data resolves to zero/negative values, avoiding
non-progressing stack loops on malformed item data. Capacity preflight mirrors
those same expiration rules for item-object transfer paths.
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "src/main/java/client/inventory/manipulator/InventoryManipulator.java"
TRANSFER_CALLERS = (
    ROOT / "src/main/java/server/maps/PlayerShop.java",
    ROOT / "src/main/java/server/maps/HiredMerchant.java",
    ROOT / "src/main/java/client/processor/npc/StorageProcessor.java",
    ROOT / "src/main/java/client/processor/npc/DueyProcessor.java",
)


def replace_once(text: str, old: str, new: str, label: str) -> tuple[str, bool]:
    if new in text:
        print(f"OK already fixed: {label}")
        return text, False
    if old not in text:
        raise SystemExit(f"ERROR expected item-stack snippet not found: {label}")
    print(f"FIXED: {label}")
    return text.replace(old, new, 1), True


def patch_transfer_callers() -> None:
    replacements = {
        "PlayerShop.java": (
            "InventoryManipulator.checkSpace(c, newItem.getItemId(), newItem.getQuantity(), newItem.getOwner())",
            "InventoryManipulator.checkSpace(c, newItem.getItemId(), newItem.getQuantity(), newItem.getOwner(), newItem.getExpiration())",
        ),
        "HiredMerchant.java": (
            "InventoryManipulator.checkSpace(c, newItem.getItemId(), newItem.getQuantity(), newItem.getOwner())",
            "InventoryManipulator.checkSpace(c, newItem.getItemId(), newItem.getQuantity(), newItem.getOwner(), newItem.getExpiration())",
        ),
        "StorageProcessor.java": (
            "InventoryManipulator.checkSpace(c, item.getItemId(), item.getQuantity(), item.getOwner())",
            "InventoryManipulator.checkSpace(c, item.getItemId(), item.getQuantity(), item.getOwner(), item.getExpiration())",
        ),
        "DueyProcessor.java": (
            "InventoryManipulator.checkSpace(c, dpItem.getItemId(), dpItem.getQuantity(), dpItem.getOwner())",
            "InventoryManipulator.checkSpace(c, dpItem.getItemId(), dpItem.getQuantity(), dpItem.getOwner(), dpItem.getExpiration())",
        ),
    }
    for path in TRANSFER_CALLERS:
        text = path.read_text(encoding="utf-8")
        old, new = replacements[path.name]
        text, changed = replace_once(text, old, new, f"{path.name} expiration-aware capacity preflight")
        if changed:
            path.write_text(text, encoding="utf-8")


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

    old_check_sig = """    public static boolean checkSpace(Client c, int itemid, int quantity, String owner) {
        ItemInformationProvider ii = ItemInformationProvider.getInstance();
"""
    new_check_sig = """    public static boolean checkSpace(Client c, int itemid, int quantity, String owner) {
        return checkSpace(c, itemid, quantity, owner, -1L);
    }

    public static boolean checkSpace(Client c, int itemid, int quantity, String owner, long expiration) {
        ItemInformationProvider ii = ItemInformationProvider.getInstance();
"""
    text, did = replace_once(text, old_check_sig, new_check_sig, "expiration-aware checkSpace overload")
    changed |= did

    old_check_slot = """        if (!type.equals(InventoryType.EQUIP)) {
            short slotMax = ii.getSlotMax(c, itemid);
            List<Item> existing = inv.listById(itemid);

            final int numSlotsNeeded;
"""
    new_check_slot = """        if (!type.equals(InventoryType.EQUIP)) {
            short slotMax = ii.getSlotMax(c, itemid);
            if (slotMax <= 0) {
                return false;
            }
            long stackExpiration = !ItemConstants.isPermanentItem(itemid)
                    ? expiration
                    : ItemConstants.isPet(itemid) ? Long.MAX_VALUE : -1L;
            List<Item> existing = inv.listById(itemid);

            final int numSlotsNeeded;
"""
    text, did = replace_once(text, old_check_slot, new_check_slot, "checkSpace slotMax + expiration normalization")
    changed |= did

    old_check_merge = """                        if (oldQ < slotMax && owner.equals(eItem.getOwner())) {
                            short newQ = (short) Math.min(oldQ + quantity, slotMax);
"""
    new_check_merge = """                        if (oldQ < slotMax
                                && owner.equals(eItem.getOwner())
                                && eItem.getExpiration() == stackExpiration) {
                            short newQ = (short) Math.min(oldQ + quantity, slotMax);
"""
    text, did = replace_once(text, old_check_merge, new_check_merge, "checkSpace expiration-compatible stacking")
    changed |= did

    if changed:
        TARGET.write_text(text, encoding="utf-8")

    patch_transfer_callers()

    final = TARGET.read_text(encoding="utf-8")
    required = (
        "if (slotMax <= 0)",
        "ItemConstants.isPet(itemId) ? Long.MAX_VALUE : -1L",
        "eItem.getExpiration() == stackExpiration",
        "item.getExpiration() == eItem.getExpiration()",
        "checkSpace(Client c, int itemid, int quantity, String owner, long expiration)",
    )
    for fragment in required:
        if fragment not in final:
            raise SystemExit(f"ERROR item-stack invariant missing: {fragment}")
    if final.count("if (slotMax <= 0)") < 3:
        raise SystemExit("ERROR expected slotMax fail-closed guards in addById, addFromDrop, and checkSpace")

    for path in TRANSFER_CALLERS:
        caller = path.read_text(encoding="utf-8")
        if "getExpiration())" not in caller:
            raise SystemExit(f"ERROR {path.name} is not using expiration-aware capacity preflight")

    print("EverLeaf item stack integrity fixes: PASS")
    print("  timed stacks merge only with identical expirations")
    print("  capacity preflight mirrors timed-stack expiration semantics")
    print("  permanent item expiration normalization mirrors Item.setExpiration")
    print("  malformed zero/negative slotMax values fail closed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
