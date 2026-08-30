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
import server.maps.MapleMap;
import server.maps.MiniDungeonInfo;
import server.maps.Portal;
import tools.PacketCreator;

/**
 * The v83 status-bar TRADE button sends ENTER_MTS. EverLeaf repurposes that
 * button as a server-authoritative shortcut to the Free Market instead of
 * entering the legacy Maple Trading System.
 */
public final class EnterMTSHandler extends AbstractPacketHandler {
    private static final int FREE_MARKET_ENTRANCE = 910000000;

    @Override
    public void handlePacket(InPacket p, Client c) {
        Character chr = c.getPlayer();

        if (chr == null) {
            c.sendPacket(PacketCreator.enableActions());
            return;
        }

        if (!chr.isAlive()) {
            reject(chr, c, "You cannot enter the Free Market while dead.");
            return;
        }

        // Never let the shortcut tear down a transactional interaction. Closing
        // a trade/storage/shop while a client is simultaneously asking to warp
        // is exactly the kind of state race that can become a dupe or rollback.
        if (chr.getTrade() != null
                || chr.getStorage() != null
                || chr.getShop() != null
                || chr.getPlayerShop() != null
                || chr.getHiredMerchant() != null) {
            reject(chr, c, "Finish your current trade or shop interaction before entering the Free Market.");
            return;
        }

        if (chr.getEventInstance() != null) {
            reject(chr, c, "You cannot enter the Free Market while participating in an event.");
            return;
        }

        if (MiniDungeonInfo.isDungeonMap(chr.getMapId())) {
            reject(chr, c, "You cannot enter the Free Market from inside a Mini-Dungeon.");
            return;
        }

        if (FieldLimit.CANNOTMIGRATE.check(chr.getMap().getFieldLimit())) {
            reject(chr, c, "You cannot enter the Free Market from this map.");
            return;
        }

        if (chr.getMapId() == FREE_MARKET_ENTRANCE) {
            c.sendPacket(PacketCreator.enableActions());
            return;
        }

        MapleMap target = c.getChannelServer().getMapFactory().getMap(FREE_MARKET_ENTRANCE);
        if (target == null) {
            reject(chr, c, "The Free Market is temporarily unavailable. Please report this in EverLeaf's bug-report channel.");
            return;
        }

        Portal targetPortal = target.getRandomPlayerSpawnpoint();
        if (targetPortal == null) {
            reject(chr, c, "The Free Market entrance is temporarily unavailable. Please report this in EverLeaf's bug-report channel.");
            return;
        }

        chr.closePlayerInteractions();
        chr.closePartySearchInteractions();
        chr.saveLocation("FREE_MARKET");
        chr.changeMap(target, targetPortal);
    }

    private static void reject(Character chr, Client c, String message) {
        chr.dropMessage(1, message);
        c.sendPacket(PacketCreator.enableActions());
    }
}
