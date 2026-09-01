#!/usr/bin/env python3
"""Apply deterministic Hired Merchant/Fredrick recovery integrity fixes."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MERCHANT = ROOT / "src/main/java/server/maps/HiredMerchant.java"
FREDRICK = ROOT / "src/main/java/client/processor/npc/FredrickProcessor.java"


def replace_once(text: str, old: str, new: str, label: str) -> tuple[str, bool]:
    if new in text:
        print(f"OK already fixed: {label}")
        return text, False
    if old not in text:
        raise SystemExit(f"ERROR expected merchant recovery snippet not found: {label}")
    print(f"FIXED: {label}")
    return text.replace(old, new, 1), True


def patch_merchant() -> None:
    text = MERCHANT.read_text(encoding="utf-8")
    changed = False

    old_take = """                    InventoryManipulator.addFromDrop(chr.getClient(), iitem, true);
                }

                removeFromSlot(slot);
"""
    new_take = """                    if (!InventoryManipulator.addFromDrop(chr.getClient(), iitem, true)) {
                        chr.sendPacket(PacketCreator.serverNotice(1, \"Unable to return that item right now. Please try again.\"));
                        chr.sendPacket(PacketCreator.enableActions());
                        return;
                    }
                }

                removeFromSlot(slot);
"""
    text, did = replace_once(text, old_take, new_take, "do not delete merchant item when owner inventory insertion fails")
    changed |= did

    old_buy = """    public void buy(Client c, int item, short quantity) {
        synchronized (items) {
            PlayerShopItem pItem = items.get(item);
            Item newItem = pItem.getItem().copy();
"""
    new_buy = """    public void buy(Client c, int item, short quantity) {
        synchronized (items) {
            if (item < 0 || item >= items.size()) {
                c.sendPacket(PacketCreator.enableActions());
                return;
            }

            PlayerShopItem pItem = items.get(item);
            Item newItem = pItem.getItem().copy();
"""
    slot_guard = "if (item < 0 || item >= items.size())"
    if slot_guard in text:
        print("OK already fixed: validate client merchant slot before dereference")
    elif old_buy in text:
        text = text.replace(old_buy, new_buy, 1)
        changed = True
        print("FIXED: validate client merchant slot before dereference")
    else:
        raise SystemExit("ERROR expected merchant recovery snippet not found: validate client merchant slot before dereference")

    old_price = """            int price = (int) Math.min((float) pItem.getPrice() * quantity, Integer.MAX_VALUE);
            if (c.getPlayer().getMeso() >= price) {
"""
    new_price = """            long grossPrice = (long) pItem.getPrice() * quantity;
            if (grossPrice <= 0 || grossPrice > Integer.MAX_VALUE) {
                c.sendPacket(PacketCreator.enableActions());
                return;
            }
            int price = (int) grossPrice;
            if (c.getPlayer().getMeso() >= price) {
"""
    text, did = replace_once(text, old_price, new_price, "use overflow-safe positive merchant purchase price")
    changed |= did

    if changed:
        MERCHANT.write_text(text, encoding="utf-8")


def patch_fredrick() -> None:
    text = FREDRICK.read_text(encoding="utf-8")
    changed = False

    old_reminders = """            for (String cname : expiredCnames) {
                ps.setString(2, cname);
                ps.executeBatch();
            }
"""
    new_reminders = """            for (String cname : expiredCnames) {
                ps.setString(2, cname);
                ps.addBatch();
            }
            ps.executeBatch();
"""
    text, did = replace_once(text, old_reminders, new_reminders, "execute Fredrick reminder deletion batch correctly")
    changed |= did

    old_withdraw = """                    chr.withdrawMerchantMesos();

                    if (deleteFredrickItems(chr.getId())) {
"""
    if old_withdraw in text:
        text = text.replace(old_withdraw, """                    if (deleteFredrickItems(chr.getId())) {
""", 1)
        changed = True
        print("FIXED: defer merchant meso withdrawal until item recovery succeeds")
    elif "chr.withdrawMerchantMesos();\n                        chr.sendPacket(PacketCreator.fredrickMessage((byte) 0x1E));" in text:
        print("OK already fixed: defer merchant meso withdrawal until item recovery succeeds")
    else:
        raise SystemExit("ERROR expected merchant recovery snippet not found: defer merchant meso withdrawal until item recovery succeeds")

    old_loop_end = """                        for (Pair<Item, InventoryType> it : items) {
                            Item item = it.getLeft();
                            InventoryManipulator.addFromDrop(chr.getClient(), item, false);
                            String itemName = ItemInformationProvider.getInstance().getName(item.getItemId());
                            log.debug(\"Chr {} gained {}x {} ({})\", chr.getName(), item.getQuantity(), itemName, item.getItemId());
                        }

                        chr.sendPacket(PacketCreator.fredrickMessage((byte) 0x1E));
                        removeFredrickLog(chr.getId());
"""
    new_loop_end = """                        for (int i = 0; i < items.size(); i++) {
                            Pair<Item, InventoryType> it = items.get(i);
                            Item item = it.getLeft();
                            if (!InventoryManipulator.addFromDrop(chr.getClient(), item, false)) {
                                List<Pair<Item, InventoryType>> remaining = new LinkedList<>();
                                List<Short> bundles = new LinkedList<>();
                                for (int j = i; j < items.size(); j++) {
                                    remaining.add(items.get(j));
                                    bundles.add((short) 1);
                                }
                                try (Connection con = DatabaseConnection.getConnection()) {
                                    ItemFactory.MERCHANT.saveItems(remaining, bundles, chr.getId(), con);
                                }
                                chr.message(\"Some merchant items could not be returned. They remain with Fredrick; clear inventory space and try again.\");
                                log.warn(\"Chr {} Fredrick recovery stopped at item {} of {}; remaining items were re-persisted\", chr.getName(), i + 1, items.size());
                                return;
                            }
                            String itemName = ItemInformationProvider.getInstance().getName(item.getItemId());
                            log.debug(\"Chr {} gained {}x {} ({})\", chr.getName(), item.getQuantity(), itemName, item.getItemId());
                        }

                        chr.withdrawMerchantMesos();
                        chr.sendPacket(PacketCreator.fredrickMessage((byte) 0x1E));
                        removeFredrickLog(chr.getId());
"""
    text, did = replace_once(text, old_loop_end, new_loop_end, "re-persist undelivered Fredrick items and withdraw mesos last")
    changed |= did

    if changed:
        FREDRICK.write_text(text, encoding="utf-8")


def main() -> int:
    patch_merchant()
    patch_fredrick()

    merchant = MERCHANT.read_text(encoding="utf-8")
    fredrick = FREDRICK.read_text(encoding="utf-8")
    required = (
        (merchant, "if (item < 0 || item >= items.size())"),
        (merchant, "long grossPrice = (long) pItem.getPrice() * quantity;"),
        (merchant, "if (!InventoryManipulator.addFromDrop(chr.getClient(), iitem, true))"),
        (fredrick, "ps.addBatch();"),
        (fredrick, "ItemFactory.MERCHANT.saveItems(remaining, bundles, chr.getId(), con);"),
        (fredrick, "chr.withdrawMerchantMesos();\n                        chr.sendPacket"),
    )
    for data, fragment in required:
        if fragment not in data:
            raise SystemExit(f"ERROR merchant recovery invariant missing: {fragment}")
    if old_withdraw_marker := "chr.withdrawMerchantMesos();\n\n                    if (deleteFredrickItems(chr.getId()))":
        if old_withdraw_marker in fredrick:
            raise SystemExit("ERROR merchant mesos are still withdrawn before Fredrick item recovery")

    print("EverLeaf merchant recovery hardening: PASS")
    print("  Hired Merchant buy slot validated before dereference")
    print("  purchase price multiplication overflow-safe and positive")
    print("  owner take-back preserves listing if inventory insertion fails")
    print("  Fredrick reminder cleanup batch executes correctly")
    print("  Fredrick undelivered items are re-persisted")
    print("  Fredrick merchant mesos withdraw only after item recovery")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
