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
import net.AbstractPacketHandler;
import net.packet.InPacket;
import server.maps.FieldLimit;
import server.maps.HiredMerchant;
import server.maps.MiniDungeonInfo;
import tools.PacketCreator;

/**
 * @author kevintjuh93 - :3
 */
public class RemoteStoreHandler extends AbstractPacketHandler {
    @Override
    public void handlePacket(InPacket p, Client c) {
        Character chr = c.getPlayer();
        if (!canAccessRemoteMerchant(chr)) {
            chr.dropMessage(1, "You cannot access your Merchant from this map or while another interaction is active.");
            c.sendPacket(PacketCreator.enableActions());
            return;
        }

        HiredMerchant hm = getMerchant(c);
        if (hm != null && hm.isOwner(chr)) {
            if (hm.getChannel() == c.getChannel()) {
                hm.visitShop(chr);
            } else {
                c.sendPacket(PacketCreator.remoteChannelChange((byte) (hm.getChannel() - 1)));
            }
            return;
        }

        chr.dropMessage(1, "You don't have a Merchant open.");
        c.sendPacket(PacketCreator.enableActions());
    }

    private static boolean canAccessRemoteMerchant(Character chr) {
        if (!chr.isAlive() || chr.isChangingMaps() || chr.isBanned()) {
            return false;
        }
        if (chr.getCashShop().isOpened()
                || chr.getEventInstance() != null
                || MiniDungeonInfo.isDungeonMap(chr.getMapId())
                || FieldLimit.CANNOTMIGRATE.check(chr.getMap().getFieldLimit())) {
            return false;
        }
        return chr.getTrade() == null
                && chr.getShop() == null
                && chr.getPlayerShop() == null
                && chr.getHiredMerchant() == null;
    }

    private static HiredMerchant getMerchant(Client c) {
        if (c.getPlayer().hasMerchant()) {
            return c.getWorldServer().getHiredMerchant(c.getPlayer().getId());
        }
        return null;
    }
}
