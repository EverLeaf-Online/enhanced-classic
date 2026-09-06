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
import client.Skill;
import client.SkillFactory;
import client.inventory.Inventory;
import client.inventory.InventoryType;
import client.inventory.Item;
import client.inventory.manipulator.InventoryManipulator;
import net.AbstractPacketHandler;
import net.packet.InPacket;
import server.ItemInformationProvider;
import tools.PacketCreator;

import java.util.Map;

public final class SkillBookHandler extends AbstractPacketHandler {
    @Override
    public final void handlePacket(InPacket p, Client c) {
        if (!c.getPlayer().isAlive()) {
            c.sendPacket(PacketCreator.enableActions());
            return;
        }

        p.readInt();
        short slot = p.readShort();
        int itemId = p.readInt();

        boolean canuse = false;
        boolean success = false;
        int skill = 0;
        int maxlevel = 0;

        Character player = c.getPlayer();
        if (c.tryacquireClient()) {
            try {
                Inventory inv = player.getInventory(InventoryType.USE);
                Item toUse = inv.getItem(slot);
                if (toUse == null || toUse.getItemId() != itemId || toUse.getQuantity() < 1) {
                    c.sendPacket(PacketCreator.enableActions());
                    return;
                }

                Map<String, Integer> skilldata = ItemInformationProvider.getInstance()
                        .getSkillStats(toUse.getItemId(), player.getJob().getId());
                if (skilldata == null) {
                    c.sendPacket(PacketCreator.enableActions());
                    return;
                }

                skill = skilldata.getOrDefault("skillid", 0);
                maxlevel = skilldata.getOrDefault("masterLevel", 0);
                Skill skill2 = SkillFactory.getSkill(skill);
                if (skill == 0 || skill2 == null) {
                    c.sendPacket(PacketCreator.enableActions());
                    return;
                }

                int requiredSkillLevel = skilldata.getOrDefault("reqSkillLevel", 0);
                if ((player.getSkillLevel(skill2) >= requiredSkillLevel || requiredSkillLevel == 0)
                        && player.getMasterLevel(skill2) < maxlevel) {
                    inv.lockInventory();
                    try {
                        Item used = inv.getItem(slot);
                        if (used != toUse || used.getQuantity() < 1 || used.getItemId() != itemId) {
                            c.sendPacket(PacketCreator.enableActions());
                            return;
                        }

                        InventoryManipulator.removeFromSlot(c, InventoryType.USE, slot, (short) 1, false);
                    } finally {
                        inv.unlockInventory();
                    }

                    canuse = true;
                    if (ItemInformationProvider.rollSuccessChance(skilldata.getOrDefault("success", 0))) {
                        success = true;
                        player.changeSkillLevel(
                                skill2,
                                player.getSkillLevel(skill2),
                                Math.max(maxlevel, player.getMasterLevel(skill2)),
                                -1
                        );
                    }
                }
            } finally {
                c.releaseClient();
            }

            // The client uses the actual skill id and resulting mastery cap to render
            // the nearby mastery-book result animation. Historically these were left
            // at zero, which produced an invalid result packet even when the book worked.
            player.getMap().broadcastMessage(PacketCreator.skillBookResult(player, skill, maxlevel, canuse, success));
        }
    }
}
