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
import net.server.coordinator.world.InviteCoordinator;
import net.server.coordinator.world.InviteCoordinator.InviteResult;
import net.server.coordinator.world.InviteCoordinator.InviteResultType;
import net.server.coordinator.world.InviteCoordinator.InviteType;
import net.server.world.Messenger;
import net.server.world.MessengerCharacter;
import net.server.world.World;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import server.ChatLogger;
import tools.PacketCreator;

public final class MessengerHandler extends AbstractPacketHandler {
    private static final Logger log = LoggerFactory.getLogger(MessengerHandler.class);

    @Override
    public final void handlePacket(InPacket p, Client c) {
        if (c.tryacquireClient()) {
            try {
                String input;
                byte mode = p.readByte();
                Character player = c.getPlayer();
                World world = c.getWorldServer();
                Messenger messenger = player.getMessenger();
                switch (mode) {
                    case 0x00:
                        int messengerid = p.readInt();
                        if (messenger == null) {
                            if (messengerid == 0) {
                                InviteCoordinator.removeInvite(InviteType.MESSENGER, player.getId());

                                MessengerCharacter messengerplayer = new MessengerCharacter(player, 0);
                                messenger = world.createMessenger(messengerplayer);
                                player.setMessenger(messenger);
                                player.setMessengerPosition(0);
                            } else {
                                messenger = world.getMessenger(messengerid);
                                if (messenger != null) {
                                    InviteResult inviteRes = InviteCoordinator.answerInvite(InviteType.MESSENGER, player.getId(), messengerid, true);
                                    InviteResultType res = inviteRes.result;
                                    if (res == InviteResultType.ACCEPTED) {
                                        int position = messenger.getLowestPosition();
                                        MessengerCharacter messengerplayer = new MessengerCharacter(player, position);
                                        if (messenger.getMembers().size() < 3) {
                                            player.setMessenger(messenger);
                                            player.setMessengerPosition(position);
                                            world.joinMessenger(messenger.getId(), messengerplayer, player.getName(), messengerplayer.getChannel());
                                        }
                                    } else {
                                        player.message("Could not verify your Maple Messenger accept since the invitation rescinded.");
                                    }
                                }
                            }
                        } else {
                            InviteCoordinator.answerInvite(InviteType.MESSENGER, player.getId(), messengerid, false);
                        }
                        break;
                    case 0x02:
                        player.closePlayerMessenger();
                        break;
                    case 0x03:
                        if (messenger == null) {
                            c.sendPacket(PacketCreator.messengerChat(player.getName() + " : This Maple Messenger is currently unavailable. Please quit this chat."));
                        } else if (messenger.getMembers().size() < 3) {
                            input = p.readString();
                            if (input.equalsIgnoreCase(player.getName())) {
                                c.sendPacket(PacketCreator.messengerChat(player.getName() + " : You cannot invite yourself to Maple Messenger"));
                                break;
                            }
                            Character target = c.getChannelServer().getPlayerStorage().getCharacterByName(input);
                            if (target != null) {
                                if (target.getMessenger() == null) {
                                    if (InviteCoordinator.createInvite(InviteType.MESSENGER, c.getPlayer(), messenger.getId(), target.getId())) {
                                        target.sendPacket(PacketCreator.messengerInvite(c.getPlayer().getName(), messenger.getId()));
                                        c.sendPacket(PacketCreator.messengerNote(input, 4, 1));
                                    } else {
                                        c.sendPacket(PacketCreator.messengerChat(player.getName() + " : " + input + " is already managing a Maple Messenger invitation"));
                                    }
                                } else {
                                    c.sendPacket(PacketCreator.messengerChat(player.getName() + " : " + input + " is already using Maple Messenger"));
                                }
                            } else {
                                if (world.find(input) > -1) {
                                    world.messengerInvite(c.getPlayer().getName(), messenger.getId(), input, c.getChannel());
                                } else {
                                    c.sendPacket(PacketCreator.messengerNote(input, 4, 0));
                                }
                            }
                        } else {
                            c.sendPacket(PacketCreator.messengerChat(player.getName() + " : You cannot have more than 3 people in the Maple Messenger"));
                        }
                        break;
                    case 0x05:
                        String targeted = p.readString();
                        world.declineChat(targeted, player);
                        break;
                    case 0x06:
                        if (messenger != null) {
                            if (player.getAutobanManager().getLastSpam(7) + 200 > currentServerTime()) {
                                break;
                            }
                            MessengerCharacter messengerplayer = new MessengerCharacter(player, player.getMessengerPosition());
                            input = p.readString();
                            if (input.length() > Byte.MAX_VALUE && !player.isGM()) {
                                AutobanFactory.PACKET_EDIT.alert(player, player.getName() + " tried to packet edit Maple Messenger chat.");
                                log.warn("Chr {} tried to send messenger text with length of {}", player.getName(), input.length());
                                c.disconnect(true, false);
                                return;
                            }
                            player.getAutobanManager().spam(7);
                            world.messengerChat(messenger, input, messengerplayer.getName());
                            ChatLogger.log(c, "Messenger", input);
                        }
                        break;
                }
            } finally {
                c.releaseClient();
            }
        }
    }
}
