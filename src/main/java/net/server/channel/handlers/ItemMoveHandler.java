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
package net.server.channel.handlers;

import client.Character;
import client.Client;
import client.inventory.Equip;
import client.inventory.InventoryType;
import client.inventory.Item;
import client.inventory.manipulator.InventoryManipulator;
import constants.inventory.EquipmentRequirements;
import net.AbstractPacketHandler;
import net.packet.InPacket;
import server.ItemInformationProvider;
import tools.PacketCreator;

import java.util.Map;

/**
 * @author Matze
 */
public final class ItemMoveHandler extends AbstractPacketHandler {
    @Override
    public final void handlePacket(InPacket p, Client c) {
        Character chr = c.getPlayer();
        if (chr.getTrade() != null && chr.getTrade().isFullTrade()) {
            c.sendPacket(PacketCreator.enableActions());
            return;
        }

        if (!c.tryacquireClient()) {
            c.sendPacket(PacketCreator.enableActions());
            return;
        }

        try {
            p.skip(4);
            if (chr.getAutobanManager().getLastSpam(6) + 300 > currentServerTime()) {
                c.sendPacket(PacketCreator.enableActions());
                return;
            }

            InventoryType type = InventoryType.getByType(p.readByte());
            short src = p.readShort();     //is there any reason to use byte instead of short in src and action?
            short action = p.readShort();
            short quantity = p.readShort();

            // Client inventory-move packets should only address real inventory tabs.
            // Internal/sentinel inventory types must never reach the manipulators from
            // an untrusted packet.
            if (type == null || type == InventoryType.UNDEFINED || type == InventoryType.CANHOLD || type == InventoryType.EQUIPPED) {
                c.sendPacket(PacketCreator.enableActions());
                return;
            }
            if (action == 0 && quantity <= 0) {
                c.sendPacket(PacketCreator.enableActions());
                return;
            }

            if (src < 0 && action > 0) {
                InventoryManipulator.unequip(c, src, action);
            } else if (action < 0) {
                // Equipping must originate from the EQUIP inventory and must respect
                // the WZ reqJob mask server-side. The stock client normally enforces
                // this, but packet-edited requests cannot be trusted to do so.
                if (type != InventoryType.EQUIP) {
                    c.sendPacket(PacketCreator.enableActions());
                    return;
                }
                Item candidate = chr.getInventory(InventoryType.EQUIP).getItem(src);
                if (!(candidate instanceof Equip equip)) {
                    c.sendPacket(PacketCreator.enableActions());
                    return;
                }
                Map<String, Integer> stats = ItemInformationProvider.getInstance().getEquipStats(equip.getItemId());
                if (stats == null || !EquipmentRequirements.canEquipForJob(chr.getJob(), stats.getOrDefault("reqJob", 0))) {
                    equip.wear(false);
                    c.sendPacket(PacketCreator.enableActions());
                    return;
                }
                InventoryManipulator.equip(c, src, action);
            } else if (action == 0) {
                InventoryManipulator.drop(c, type, src, quantity);
            } else {
                InventoryManipulator.move(c, type, src, action);
            }

            chr.getAutobanManager().spam(6);
        } finally {
            c.releaseClient();
        }
    }
}
