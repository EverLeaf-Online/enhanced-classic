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
import client.autoban.AutobanFactory;
import net.AbstractPacketHandler;
import net.packet.InPacket;
import net.server.Server;
import tools.PacketCreator;

/**
 * @author Matze
 */
public final class ChangeChannelHandler extends AbstractPacketHandler {

    @Override
    public final void handlePacket(InPacket p, Client c) {
        int channel = p.readByte() + 1;
        p.readInt();
        Character chr = c.getPlayer();
        chr.getAutobanManager().setTimestamp(6, Server.getInstance().getCurrentTimestamp(), 3);

        if (Server.getInstance().getChannel(c.getWorld(), channel) == null) {
            c.sendPacket(PacketCreator.enableActions());
            return;
        }

        if (c.getChannel() == channel) {
            AutobanFactory.GENERAL.alert(chr, "CCing to same channel.");
            c.disconnect(false, false);
            return;
        } else if (chr.getCashShop().isOpened()
                || chr.getMiniGame() != null
                || chr.getPlayerShop() != null
                || chr.getHiredMerchant() != null
                || chr.getTrade() != null
                || chr.getShop() != null) {
            c.sendPacket(PacketCreator.enableActions());
            return;
        }

        // Storage is account/world state and may survive the Character object during
        // a server transition. Always invalidate any stale UI/session before moving.
        if (chr.getStorage() != null) {
            chr.getStorage().close();
        }

        c.changeChannel(channel);
    }
}
