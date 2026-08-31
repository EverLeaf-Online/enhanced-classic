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
import client.command.CommandsExecutor;
import net.AbstractPacketHandler;
import net.packet.InPacket;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import server.ChatLogger;
import tools.PacketCreator;

public final class GeneralChatHandler extends AbstractPacketHandler {
    private static final Logger log = LoggerFactory.getLogger(GeneralChatHandler.class);
    private static final long GENERAL_CHAT_MIN_INTERVAL_MS = 100L;

    @Override
    public void handlePacket(InPacket p, Client c) {
        String s = p.readString();
        Character chr = c.getPlayer();

        // EverLeaf keeps a small server-authoritative flood guard, but the old
        // 200 ms gate was aggressive enough to eat legitimate fast chat. A
        // 100 ms interval still caps accepted general-chat packets at roughly
        // 10/s per character while making normal conversation feel immediate.
        if (chr.getAutobanManager().getLastSpam(7) + GENERAL_CHAT_MIN_INTERVAL_MS > currentServerTime()) {
            c.sendPacket(PacketCreator.enableActions());
            return;
        }
        if (s.length() > Byte.MAX_VALUE && !chr.isGM()) {
            AutobanFactory.PACKET_EDIT.alert(c.getPlayer(), c.getPlayer().getName() + " tried to packet edit in General Chat.");
            log.warn("Chr {} tried to send text with length of {}", c.getPlayer().getName(), s.length());
            c.disconnect(true, false);
            return;
        }
        char heading = s.charAt(0);
        if (CommandsExecutor.isCommand(c, s)) {
            CommandsExecutor.getInstance().handle(c, s);
        } else if (heading != '/') {
            int show = p.readByte();
            if (chr.getMap().isMuted() && !chr.isGM()) {
                chr.dropMessage(5, "The map you are in is currently muted. Please try again later.");
                return;
            }

            if (!chr.isHidden()) {
                chr.getMap().broadcastMessage(PacketCreator.getChatText(chr.getId(), s, chr.getWhiteChat(), show));
                ChatLogger.log(c, "General", s);
            } else {
                chr.getMap().broadcastGMMessage(PacketCreator.getChatText(chr.getId(), s, chr.getWhiteChat(), show));
                ChatLogger.log(c, "GM General", s);
            }

            chr.getAutobanManager().spam(7);
        }
    }
}