/*
	This file is part of the OdinMS Maple Story Server
    Copyright (C) 2008 Patrick Huy <patrick.huy@frz.cc>
		       Matthias Butz <matze@odinms.de>
		       Jan Christian Meyer <vimes@odinms.de>

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as
    published by the Free Software Foundation version 3 as published by
    the Free Software Foundation. You may not use, modify or distribute
    this program under any other version of the GNU Affero General Public
    License.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */
package client.processor.npc;

import client.Character;
import client.Client;
import client.autoban.AutobanFactory;
import client.inventory.Inventory;
import client.inventory.InventoryType;
import client.inventory.Item;
import client.inventory.manipulator.InventoryManipulator;
import client.inventory.manipulator.KarmaManipulator;
import config.YamlConfig;
import constants.id.ItemId;
import constants.inventory.ItemConstants;
import net.packet.InPacket;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import server.ItemInformationProvider;
import server.Storage;
import tools.PacketCreator;

/**
 * @author Matze
 * @author Ronan - inventory concurrency protection on storing items
 */
public class StorageProcessor {
    private static final Logger log = LoggerFactory.getLogger(StorageProcessor.class);

    public static void storageAction(InPacket p, Client c) {
        ItemInformationProvider ii = ItemInformationProvider.getInstance();
        Character chr = c.getPlayer();
        Storage storage = chr.getStorage();
        String gmBlockedStorageMessage = "You cannot use the storage as a GM of this level.";

        byte mode = p.readByte();

        if (c.tryacquireClient()) {
            try {
                switch (mode) {
                case 4: { // Take out
                    byte type = p.readByte();
                    byte slot = p.readByte();
                    if (slot < 0 || slot > storage.getSlots()) { // removal starts at zero
                        AutobanFactory.PACKET_EDIT.alert(c.getPlayer(), c.getPlayer().getName() + " tried to packet edit with storage.");
                        log.warn("Chr {} tried to work with storage slot {}", c.getPlayer().getName(), slot);
                        c.disconnect(true, false);
                        return;
                    }

                    slot = storage.getSlot(InventoryType.getByType(type), slot);
                    Item item = storage.getItem(slot);

                    if (hasGMRestrictions(chr)) {
                        chr.dropMessage(1, gmBlockedStorageMessage);
                        log.info(String.format("GM %s blocked from using storage", chr.getName()));
                        chr.sendPacket(PacketCreator.enableActions());
                        return;
                    }

                    if (item != null) {
                        if (ii.isPickupRestricted(item.getItemId()) && chr.haveItemWithId(item.getItemId(), true)) {
                            c.sendPacket(PacketCreator.getStorageError((byte) 0x0C));
                            return;
                        }

                        int takeoutFee = storage.getTakeOutFee();
                        if (chr.getMeso() < takeoutFee) {
                            c.sendPacket(PacketCreator.getStorageError((byte) 0x0B));
                            return;
                        }

                        if (!InventoryManipulator.checkSpace(c, item.getItemId(), item.getQuantity(), item.getOwner())) {
                            c.sendPacket(PacketCreator.getStorageError((byte) 0x0A));
                            return;
                        }

                        // Keep the original storage object untouched until the inventory
                        // transfer succeeds. Withdrawal-only karma changes apply to a copy
                        // so a failed add can restore the exact original item.
                        Item transferItem = item.copy();
                        KarmaManipulator.toggleKarmaFlagToUntradeable(transferItem);

                        if (!storage.takeOut(item)) {
                            c.sendPacket(PacketCreator.enableActions());
                            return;
                        }

                        if (!InventoryManipulator.addFromDrop(c, transferItem, false)) {
                            // Space was checked above, but another inventory mutation or an
                            // unexpected add failure must not delete the storage item.
                            if (!storage.store(item)) {
                                log.error("CRITICAL: failed to restore storage item {} for chr {} after inventory add failure",
                                        item.getItemId(), chr.getName());
                            }
                            c.sendPacket(PacketCreator.enableActions());
                            return;
                        }

                        chr.gainMeso(-takeoutFee, false);
                        chr.setUsedStorage();

                        String itemName = ii.getName(item.getItemId());
                        log.debug("Chr {} took out {}x {} ({})", c.getPlayer().getName(), item.getQuantity(), itemName, item.getItemId());

                        storage.sendTakenOut(c, item.getInventoryType());
                    }
                    break;
                }
                case 5: { // Store
                    short slot = p.readShort();
                    int itemId = p.readInt();
                    short quantity = p.readShort();
                    InventoryType invType = ItemConstants.getInventoryType(itemId);
                    Inventory inv = chr.getInventory(invType);
                    if (slot < 1 || slot > inv.getSlotLimit()) { // player inv starts at one
                        AutobanFactory.PACKET_EDIT.alert(c.getPlayer(),
                                c.getPlayer().getName() + " tried to packet edit with storage.");
                        log.warn("Chr {} tried to store item at slot {}", c.getPlayer().getName(), slot);
                        c.disconnect(true, false);
                        return;
                    }

                    if (hasGMRestrictions(chr)) {
                        chr.dropMessage(1, gmBlockedStorageMessage);
                        log.info(String.format("GM %s blocked from using storage", chr.getName()));
                        chr.sendPacket(PacketCreator.enableActions());
                        return;
                    }

                    if (quantity < 1) {
                        c.sendPacket(PacketCreator.enableActions());
                        return;
                    }
                    if (storage.isFull()) {
                        c.sendPacket(PacketCreator.getStorageError((byte) 0x11));
                        return;
                    }
                    int storeFee = storage.getStoreFee();
                    if (chr.getMeso() < storeFee) {
                        c.sendPacket(PacketCreator.getStorageError((byte) 0x0B));
                    } else {
                        Item item;

                        inv.lockInventory(); // thanks imbee for pointing a dupe within storage
                        try {
                            item = inv.getItem(slot);
                            if (item != null && item.getItemId() == itemId
                                    && (item.getQuantity() >= quantity || ItemConstants.isRechargeable(itemId))) {
                                if (ItemId.isWeddingRing(itemId) || ItemId.isWeddingToken(itemId)) {
                                    c.sendPacket(PacketCreator.enableActions());
                                    return;
                                }

                                if (ItemConstants.isRechargeable(itemId)) {
                                    quantity = item.getQuantity();
                                }

                                InventoryManipulator.removeFromSlot(c, invType, slot, quantity, false);
                            } else {
                                c.sendPacket(PacketCreator.enableActions());
                                return;
                            }

                            item = item.copy(); // thanks Robin Schulz & BHB88 for noticing a inventory glitch when storing items
                        } finally {
                            inv.unlockInventory();
                        }

                        item.setQuantity(quantity);
                        Item rollbackItem = item.copy();
                        KarmaManipulator.toggleKarmaFlagToUntradeable(item);

                        if (!storage.store(item)) {
                            // The storage can become full between the optimistic pre-check
                            // and the locked store operation. Restore the removed inventory
                            // item instead of silently deleting it, and do not charge a fee.
                            if (!InventoryManipulator.addFromDrop(c, rollbackItem, false)) {
                                log.error("CRITICAL: failed to restore inventory item {} for chr {} after storage store race",
                                        rollbackItem.getItemId(), chr.getName());
                            }
                            c.sendPacket(PacketCreator.getStorageError((byte) 0x11));
                            return;
                        }

                        chr.gainMeso(-storeFee, false, true, false);
                        chr.setUsedStorage();

                        String itemName = ii.getName(item.getItemId());
                        log.debug("Chr {} stored {}x {} ({})", c.getPlayer().getName(), item.getQuantity(), itemName, item.getItemId());
                        storage.sendStored(c, ItemConstants.getInventoryType(itemId));
                    }
                    break;
                }
                case 6: // Arrange items
                    if (YamlConfig.config.server.USE_STORAGE_ITEM_SORT) {
                        storage.arrangeItems(c);
                    }
                    c.sendPacket(PacketCreator.enableActions());
                    break;
                case 7: { // Mesos
                    int meso = p.readInt();
                    int storageMesos = storage.getMeso();
                    int playerMesos = chr.getMeso();

                    if (hasGMRestrictions(chr)) {
                        chr.dropMessage(1, gmBlockedStorageMessage);
                        log.info(String.format("GM %s blocked from using storage", chr.getName()));
                        chr.sendPacket(PacketCreator.enableActions());
                        return;
                    }

                    if (meso == 0) {
                        c.sendPacket(PacketCreator.enableActions());
                        return;
                    }

                    long newStorageMesos = (long) storageMesos - meso;
                    long newPlayerMesos = (long) playerMesos + meso;
                    if (newStorageMesos < 0 || newStorageMesos > Integer.MAX_VALUE
                            || newPlayerMesos < 0 || newPlayerMesos > Integer.MAX_VALUE) {
                        log.warn("Chr {} attempted invalid storage meso transfer: delta={}, player={}, storage={}",
                                chr.getName(), meso, playerMesos, storageMesos);
                        c.sendPacket(PacketCreator.enableActions());
                        return;
                    }

                    storage.setMeso((int) newStorageMesos);
                    chr.gainMeso(meso, false, true, false);
                    chr.setUsedStorage();
                    log.debug("Chr {} {} {} mesos", c.getPlayer().getName(), meso > 0 ? "took out" : "stored", Math.abs((long) meso));
                    storage.sendMeso(c);
                    break;
                }
                case 8: // Close (unless the player decides to enter cash shop)
                    storage.close();
                    break;
                }
            } finally {
                c.releaseClient();
            }
        }
    }

    private static boolean hasGMRestrictions(Character character) {
        return character.isGM() && character.gmLevel() < YamlConfig.config.server.MINIMUM_GM_LEVEL_TO_USE_STORAGE;
    }
}