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

import client.Client;
import net.AbstractPacketHandler;
import net.packet.InPacket;
import server.maps.Reactor;
import tools.PacketCreator;

import java.awt.Point;

/**
 * @author Lerk
 */
public final class ReactorHitHandler extends AbstractPacketHandler {
    @Override
    public final void handlePacket(InPacket p, Client c) {
        int oid = p.readInt();
        int charPos = p.readInt();
        short stance = p.readShort();
        p.skip(4);
        int skillid = p.readInt();
        Reactor reactor = c.getPlayer().getMap().getReactorByOid(oid);
        if (reactor == null || !isNearby(c, reactor)) {
            c.sendPacket(PacketCreator.enableActions());
            return;
        }

        reactor.hitReactor(true, charPos, stance, skillid, c);
    }

    private static boolean isNearby(Client c, Reactor reactor) {
        Point playerPos = c.getPlayer().getPosition();
        Point reactorPos = reactor.getPosition();
        return Math.abs(reactorPos.x - playerPos.x) <= 1200
                && Math.abs(reactorPos.y - playerPos.y) <= 800;
    }
}
