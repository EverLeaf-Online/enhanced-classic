#!/usr/bin/env python3
"""Apply deterministic Duey settlement-integrity fixes.

This closes normal error-path loss/orphan cases without pretending the live player
inventory and SQL mailbox are one crash-atomic durability domain.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "src/main/java/client/processor/npc/DueyProcessor.java"


def replace_once(text: str, old: str, new: str, label: str) -> tuple[str, bool]:
    if new in text:
        print(f"OK already fixed: {label}")
        return text, False
    if old not in text:
        raise SystemExit(f"ERROR expected Duey settlement snippet not found: {label}")
    print(f"FIXED: {label}")
    return text.replace(old, new, 1), True


def main() -> int:
    text = TARGET.read_text(encoding="utf-8")
    changed = False

    old_helper = """    private static int addPackageItemFromInventory(int packageId, Client c, byte invTypeId, short itemPos, short amount) {
        if (invTypeId > 0) {
            ItemInformationProvider ii = ItemInformationProvider.getInstance();

            InventoryType invType = InventoryType.getByType(invTypeId);
            Inventory inv = c.getPlayer().getInventory(invType);

            Item item;
            inv.lockInventory();
            try {
                item = inv.getItem(itemPos);
                if (item != null && item.getQuantity() >= amount) {
                    if (item.isUntradeable() || ii.isUnmerchable(item.getItemId())) {
                        return -1;
                    }

                    if (ItemConstants.isRechargeable(item.getItemId())) {
                        InventoryManipulator.removeFromSlot(c, invType, itemPos, item.getQuantity(), true);
                    } else {
                        InventoryManipulator.removeFromSlot(c, invType, itemPos, amount, true, false);
                    }

                    item = item.copy();
                } else {
                    return -2;
                }
            } finally {
                inv.unlockInventory();
            }

            KarmaManipulator.toggleKarmaFlagToUntradeable(item);
            item.setQuantity(amount);

            if (!insertPackageItem(packageId, item)) {
                return 1;
            }
        }

        return 0;
    }
"""
    new_helper = """    private static int addPackageItemFromInventory(int packageId, Client c, byte invTypeId, short itemPos, short amount) {
        if (invTypeId <= 0) {
            return 0;
        }

        ItemInformationProvider ii = ItemInformationProvider.getInstance();
        InventoryType invType = InventoryType.getByType(invTypeId);
        if (invType == null || invType == InventoryType.UNDEFINED || invType == InventoryType.EQUIPPED || invType == InventoryType.CANHOLD) {
            return -2;
        }

        Inventory inv = c.getPlayer().getInventory(invType);
        inv.lockInventory();
        try {
            Item sourceItem = inv.getItem(itemPos);
            if (sourceItem == null || amount < 1 || sourceItem.getQuantity() < amount) {
                return -2;
            }
            if (sourceItem.isUntradeable() || ii.isUnmerchable(sourceItem.getItemId())) {
                return -1;
            }

            short transferAmount = ItemConstants.isRechargeable(sourceItem.getItemId())
                    ? sourceItem.getQuantity()
                    : amount;
            Item packageItem = sourceItem.copy();
            KarmaManipulator.toggleKarmaFlagToUntradeable(packageItem);
            packageItem.setQuantity(transferAmount);

            // Persist the package payload before mutating the sender inventory.
            // If SQL persistence fails, the sender keeps the item unchanged.
            if (!insertPackageItem(packageId, packageItem)) {
                return 1;
            }

            InventoryManipulator.removeFromSlot(c, invType, itemPos, transferAmount, true, false);
            return 0;
        } finally {
            inv.unlockInventory();
        }
    }
"""
    text, did = replace_once(text, old_helper, new_helper, "persist package payload before sender item removal")
    changed |= did

    old_send = """                if (quick) {
                    InventoryManipulator.removeById(c, InventoryType.CASH, ItemId.QUICK_DELIVERY_TICKET, (short) 1, false, false);
                }

                int packageId = createPackage(sendMesos, sendMessage, c.getPlayer().getName(), recipientCid, quick);
                if (packageId == -1) {
                    c.sendPacket(PacketCreator.sendDueyMSG(DueyProcessor.Actions.TOCLIENT_SEND_ENABLE_ACTIONS.getCode()));
                    return;
                }
                c.getPlayer().gainMeso((int) -finalcost, false);

                int res = addPackageItemFromInventory(packageId, c, invTypeId, itemPos, amount);
                if (res == 0) {
                    c.sendPacket(PacketCreator.sendDueyMSG(DueyProcessor.Actions.TOCLIENT_SEND_SUCCESSFULLY_SENT.getCode()));
                } else if (res > 0) {
                    c.sendPacket(PacketCreator.sendDueyMSG(DueyProcessor.Actions.TOCLIENT_SEND_ENABLE_ACTIONS.getCode()));
                } else {
                    c.sendPacket(PacketCreator.sendDueyMSG(DueyProcessor.Actions.TOCLIENT_SEND_INCORRECT_REQUEST.getCode()));
                }

                Client rClient = null;
"""
    new_send = """                int packageId = createPackage(sendMesos, sendMessage, c.getPlayer().getName(), recipientCid, quick);
                if (packageId == -1) {
                    c.sendPacket(PacketCreator.sendDueyMSG(DueyProcessor.Actions.TOCLIENT_SEND_ENABLE_ACTIONS.getCode()));
                    return;
                }

                int res = addPackageItemFromInventory(packageId, c, invTypeId, itemPos, amount);
                if (res != 0) {
                    // The package header was created, but settlement failed. Remove
                    // it before returning so invalid/failed sends cannot orphan an
                    // empty delivery. Item persistence now happens before sender
                    // inventory removal, so this path does not consume the item.
                    removePackageFromDB(packageId);
                    if (res > 0) {
                        c.sendPacket(PacketCreator.sendDueyMSG(DueyProcessor.Actions.TOCLIENT_SEND_ENABLE_ACTIONS.getCode()));
                    } else {
                        c.sendPacket(PacketCreator.sendDueyMSG(DueyProcessor.Actions.TOCLIENT_SEND_INCORRECT_REQUEST.getCode()));
                    }
                    return;
                }

                // Charge only after the package header + optional item payload are
                // successfully settled. A failed package no longer consumes mesos
                // or a Quick Delivery ticket.
                if (quick) {
                    InventoryManipulator.removeById(c, InventoryType.CASH, ItemId.QUICK_DELIVERY_TICKET, (short) 1, false, false);
                }
                c.getPlayer().gainMeso((int) -finalcost, false);
                c.sendPacket(PacketCreator.sendDueyMSG(DueyProcessor.Actions.TOCLIENT_SEND_SUCCESSFULLY_SENT.getCode()));

                Client rClient = null;
"""
    text, did = replace_once(text, old_send, new_send, "defer Duey charges and clean failed package headers")
    changed |= did

    old_create = """    public static void dueyCreatePackage(Item item, int mesos, String sender, int recipientCid) {
        int packageId = createPackage(mesos, null, sender, recipientCid, false);
        if (packageId != -1) {
            insertPackageItem(packageId, item);
        }
    }
"""
    new_create = """    public static void dueyCreatePackage(Item item, int mesos, String sender, int recipientCid) {
        int packageId = createPackage(mesos, null, sender, recipientCid, false);
        if (packageId != -1 && !insertPackageItem(packageId, item)) {
            removePackageFromDB(packageId);
            log.error(\"Removed incomplete server-created Duey package {} for receiver {}\", packageId, recipientCid);
        }
    }
"""
    text, did = replace_once(text, old_create, new_create, "clean failed server-created package payloads")
    changed |= did

    old_claim_add = """                        } else {
                            InventoryManipulator.addFromDrop(c, dpItem, false);
                        }
                    }

                    c.getPlayer().gainMeso(dp.getMesos(), false);
"""
    new_claim_add = """                        } else if (!InventoryManipulator.addFromDrop(c, dpItem, false)) {
                            c.sendPacket(PacketCreator.sendDueyMSG(Actions.TOCLIENT_RECV_NO_FREE_SLOTS.getCode()));
                            return;
                        }
                    }

                    c.getPlayer().gainMeso(dp.getMesos(), false);
"""
    text, did = replace_once(text, old_claim_add, new_claim_add, "abort claim if final inventory insertion fails")
    changed |= did

    if changed:
        TARGET.write_text(text, encoding="utf-8")

    final = TARGET.read_text(encoding="utf-8")
    required = (
        "if (invTypeId <= 0)",
        "sourceItem == null || amount < 1 || sourceItem.getQuantity() < amount",
        "if (!insertPackageItem(packageId, packageItem))",
        "InventoryManipulator.removeFromSlot(c, invType, itemPos, transferAmount, true, false);",
        "if (res != 0)",
        "removePackageFromDB(packageId);",
        "if (quick) {\n                    InventoryManipulator.removeById",
        "if (packageId != -1 && !insertPackageItem(packageId, item))",
        "else if (!InventoryManipulator.addFromDrop(c, dpItem, false))",
    )
    for fragment in required:
        if fragment not in final:
            raise SystemExit(f"ERROR Duey settlement invariant missing: {fragment}")

    print("EverLeaf Duey settlement hardening: PASS")
    print("  package payload persists before sender item removal")
    print("  failed send cleans package header")
    print("  failed send does not charge mesos/quick ticket")
    print("  rechargeable transfer quantity normalized to full stack")
    print("  final claim insertion failure leaves package unconsumed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
