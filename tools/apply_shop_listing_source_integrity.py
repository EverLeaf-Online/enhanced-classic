#!/usr/bin/env python3
"""Harden PlayerShop/HiredMerchant listing source validation and rollback."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
HANDLER = ROOT / "src/main/java/net/server/channel/handlers/PlayerInteractionHandler.java"
PLAYER_SHOP = ROOT / "src/main/java/server/maps/PlayerShop.java"
HIRED = ROOT / "src/main/java/server/maps/HiredMerchant.java"


def add_rollback_helper(path: Path, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    marker = "public boolean removeItem(PlayerShopItem item)"
    if marker in text:
        print(f"OK already fixed: {label} rollback helper")
        return

    old = """    public boolean addItem(PlayerShopItem item) {
        synchronized (items) {
            if (items.size() >= 16) {
                return false;
            }

            items.add(item);
            return true;
        }
    }
"""
    new = old + """
    public boolean removeItem(PlayerShopItem item) {
        synchronized (items) {
            return items.remove(item);
        }
    }
"""
    if old not in text:
        raise SystemExit(f"ERROR expected {label} addItem snippet not found")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")
    print(f"FIXED: {label} rollback helper")


def patch_handler() -> None:
    text = HANDLER.read_text(encoding="utf-8")
    marker = "Invalid inventory type for shop listing"
    if marker in text:
        print("OK already fixed: shop listing source integrity")
        return

    pattern = re.compile(
        r"            \} else if \(mode == Action\.ADD_ITEM\.getCode\(\) \|\| mode == Action\.PUT_ITEM\.getCode\(\)\) \{.*?\n            \} else if \(mode == Action\.REMOVE_ITEM\.getCode\(\)\) \{",
        re.S,
    )
    match = pattern.search(text)
    if not match:
        raise SystemExit("ERROR shop listing handler block not found")

    replacement = r'''            } else if (mode == Action.ADD_ITEM.getCode() || mode == Action.PUT_ITEM.getCode()) {
                if (isTradeOpen(chr)) {
                    return;
                }

                InventoryType ivType = InventoryType.getByType(p.readByte());
                short slot = p.readShort();
                short bundles = p.readShort();
                short perBundle = p.readShort();
                int price = p.readInt();

                if (ivType == null || ivType == InventoryType.UNDEFINED || ivType == InventoryType.CANHOLD || ivType == InventoryType.EQUIPPED) {
                    AutobanFactory.PACKET_EDIT.alert(chr, chr.getName() + " sent an invalid inventory type for shop listing.");
                    log.warn("Chr {} sent Invalid inventory type for shop listing: {}", chr.getName(), ivType);
                    c.sendPacket(PacketCreator.enableActions());
                    return;
                }

                if (bundles <= 0 || perBundle <= 0 || price <= 0) {
                    AutobanFactory.PACKET_EDIT.alert(chr, chr.getName() + " tried to packet edit a shop listing.");
                    log.warn("Chr {} sent invalid shop listing values. perBundle: {}, bundles: {}, price: {}", chr.getName(), perBundle, bundles, price);
                    c.sendPacket(PacketCreator.enableActions());
                    return;
                }

                PlayerShop shop = chr.getPlayerShop();
                HiredMerchant merchant = chr.getHiredMerchant();
                boolean playerShopOwner = shop != null && shop.isOwner(chr);
                boolean merchantOwner = merchant != null && merchant.isOwner(chr);
                if (!playerShopOwner && !merchantOwner) {
                    c.sendPacket(PacketCreator.serverNotice(1, "You can't sell without owning a shop."));
                    c.sendPacket(PacketCreator.enableActions());
                    return;
                }
                if (playerShopOwner && shop.isOpen()) {
                    c.sendPacket(PacketCreator.serverNotice(1, "You can't sell it anymore."));
                    c.sendPacket(PacketCreator.enableActions());
                    return;
                }
                if (merchantOwner && merchant.isOpen()) {
                    c.sendPacket(PacketCreator.serverNotice(1, "You can't sell it anymore."));
                    c.sendPacket(PacketCreator.enableActions());
                    return;
                }
                if (merchantOwner && ivType == InventoryType.CASH && merchant.isPublished()) {
                    c.sendPacket(PacketCreator.serverNotice(1, "Cash items are only allowed to be sold when first opening the store."));
                    c.sendPacket(PacketCreator.enableActions());
                    return;
                }

                Inventory inv = chr.getInventory(ivType);
                Item sourceItem;
                Item sellItem;
                short listingBundles = bundles;
                short listingPerBundle = perBundle;
                short removeQuantity;

                inv.lockInventory();
                try {
                    sourceItem = inv.getItem(slot);
                    if (sourceItem == null || sourceItem.isUntradeable()) {
                        c.sendPacket(PacketCreator.serverNotice(1, "Could not perform shop operation with that item."));
                        c.sendPacket(PacketCreator.enableActions());
                        return;
                    }
                    if (ItemInformationProvider.getInstance().isUnmerchable(sourceItem.getItemId())) {
                        if (ItemConstants.isPet(sourceItem.getItemId())) {
                            c.sendPacket(PacketCreator.serverNotice(1, "Pets are not allowed to be sold on the Player Store."));
                        } else {
                            c.sendPacket(PacketCreator.serverNotice(1, "Cash items are not allowed to be sold on the Player Store."));
                        }
                        c.sendPacket(PacketCreator.enableActions());
                        return;
                    }

                    if (ItemConstants.isRechargeable(sourceItem.getItemId())) {
                        listingPerBundle = 1;
                        listingBundles = 1;
                        removeQuantity = sourceItem.getQuantity();
                    } else {
                        long totalQuantity = (long) listingPerBundle * listingBundles;
                        if (totalQuantity <= 0 || totalQuantity > 2000 || totalQuantity > sourceItem.getQuantity() || totalQuantity > Short.MAX_VALUE) {
                            AutobanFactory.PACKET_EDIT.alert(chr, chr.getName() + " tried to packet edit a shop listing quantity.");
                            log.warn("Chr {} sent invalid shop listing quantity. perBundle: {}, bundles: {}, total: {}", chr.getName(), listingPerBundle, listingBundles, totalQuantity);
                            c.sendPacket(PacketCreator.enableActions());
                            return;
                        }
                        removeQuantity = (short) totalQuantity;
                    }

                    sellItem = sourceItem.copy();
                    if (!ItemConstants.isRechargeable(sourceItem.getItemId())) {
                        sellItem.setQuantity(listingPerBundle);
                    }
                } finally {
                    inv.unlockInventory();
                }

                PlayerShopItem shopItem = new PlayerShopItem(sellItem, listingBundles, price);
                boolean admitted = playerShopOwner ? shop.addItem(shopItem) : merchant.addItem(shopItem);
                if (!admitted) {
                    c.sendPacket(PacketCreator.serverNotice(1, "You can't sell it anymore."));
                    c.sendPacket(PacketCreator.enableActions());
                    return;
                }

                boolean removed = false;
                inv.lockInventory();
                try {
                    Item currentItem = inv.getItem(slot);
                    if (currentItem == sourceItem && currentItem.getItemId() == sourceItem.getItemId() && currentItem.getQuantity() >= removeQuantity) {
                        InventoryManipulator.removeFromSlot(c, ivType, slot, removeQuantity, true);
                        removed = true;
                    }
                } catch (RuntimeException ex) {
                    log.warn("Chr {} shop listing source removal failed for item {} in slot {}", chr.getName(), sourceItem.getItemId(), slot, ex);
                } finally {
                    inv.unlockInventory();
                }

                if (!removed) {
                    boolean rolledBack = playerShopOwner ? shop.removeItem(shopItem) : merchant.removeItem(shopItem);
                    if (!rolledBack) {
                        log.error("Failed to roll back shop listing for chr {} item {} after source revalidation failure", chr.getName(), sourceItem.getItemId());
                    }
                    c.sendPacket(PacketCreator.serverNotice(1, "Your inventory changed before the listing completed. Please try again."));
                    c.sendPacket(PacketCreator.enableActions());
                    return;
                }

                if (playerShopOwner) {
                    c.sendPacket(PacketCreator.getPlayerShopItemUpdate(shop));
                } else {
                    c.sendPacket(PacketCreator.updateHiredMerchant(merchant, chr));

                    if (YamlConfig.config.server.USE_ENFORCE_MERCHANT_SAVE) {
                        chr.saveCharToDB(false);
                    }

                    try {
                        merchant.saveItems(false);   // thanks Masterrulax for realizing yet another dupe with merchants/Fredrick
                    } catch (SQLException ex) {
                        log.error("Failed to persist Hired Merchant listing for chr {} item {}", chr.getName(), sourceItem.getItemId(), ex);
                    }
                }
            } else if (mode == Action.REMOVE_ITEM.getCode()) {'''

    text = text[:match.start()] + replacement + text[match.end():]
    HANDLER.write_text(text, encoding="utf-8")
    print("FIXED: shop listing source integrity")


def main() -> int:
    add_rollback_helper(PLAYER_SHOP, "PlayerShop")
    add_rollback_helper(HIRED, "HiredMerchant")
    patch_handler()

    handler = HANDLER.read_text(encoding="utf-8")
    player_shop = PLAYER_SHOP.read_text(encoding="utf-8")
    hired = HIRED.read_text(encoding="utf-8")
    required = (
        (handler, "ivType == null || ivType == InventoryType.UNDEFINED || ivType == InventoryType.CANHOLD || ivType == InventoryType.EQUIPPED"),
        (handler, "long totalQuantity = (long) listingPerBundle * listingBundles;"),
        (handler, "Item currentItem = inv.getItem(slot);"),
        (handler, "currentItem == sourceItem"),
        (handler, "shop.removeItem(shopItem) : merchant.removeItem(shopItem)"),
        (player_shop, "public boolean removeItem(PlayerShopItem item)"),
        (hired, "public boolean removeItem(PlayerShopItem item)"),
    )
    for data, fragment in required:
        if fragment not in data:
            raise SystemExit(f"ERROR shop listing source invariant missing: {fragment}")

    print("EverLeaf shop listing source integrity hardening: PASS")
    print("  invalid/non-player inventory types fail closed before inventory lookup")
    print("  listing quantity multiplication uses checked long arithmetic")
    print("  source item is revalidated under inventory lock before removal")
    print("  changed/stale source state rolls the newly admitted listing back")
    print("  PlayerShop and HiredMerchant rollback helpers synchronize on stock")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
