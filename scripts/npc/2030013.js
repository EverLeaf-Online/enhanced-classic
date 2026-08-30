/*
	This file is part of the OdinMS Maple Story Server
    Copyright (C) 2008 Patrick Huy <patrick.huy@frz.cc> 
                       Matthias Butz <matze@odinms.de>
                       Jan Christian Meyer <vimes@odinms.de>

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License version 3
    as published by the Free Software Foundation. You may not use, modify
    or distribute this program under any other version of the
    GNU Affero General Public License.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
*/
/*Adobis
 *
 *@author Alan (SharpAceX)
 *@author Ronan
 */

var status = 0;
var expedition;
var expedMembers;
var player;
var em;
const ExpeditionType = Java.type('server.expeditions.ExpeditionType');
const exped = ExpeditionType.ZAKUM;
var expedName = "Zakum";
var expedBoss = "Zakum";
var expedMap = "Zakum's Altar";
var expedItem = 4001017;

var list = "What would you like to do?#b\r\n\r\n#L1#View current Expedition members#l\r\n#L2#Start the fight!#l\r\n#L3#Stop the expedition.#l";

function start() {
    action(1, 0, 0);
}

function action(mode, type, selection) {

    player = cm.getPlayer();
    expedition = cm.getExpedition(exped);
    em = cm.getEventManager("ZakumBattle");

    if (mode == -1) {
        cm.dispose();
    } else {
        if (mode == 0) {
            cm.dispose();
            return;
        }

        if (status == 0) {
            if (player.getLevel() < exped.getMinLevel() || player.getLevel() > exped.getMaxLevel()) {
                cm.sendOk("You cannot enter the " + expedBoss + " expedition at your current level.\r\n\r\n#bRequired Level: " + exped.getMinLevel() + " - " + exped.getMaxLevel() + "#k\r\nYour Level: " + player.getLevel());
                cm.dispose();
            } else if (expedition == null) {
                cm.sendSimple("#e#b<Expedition: " + expedName + ">\r\n#k#n" + em.getProperty("party") + "\r\n\r\nWould you like to assemble a team to take on #r" + expedBoss + "#k?\r\n#b#L1#Let's get this going!#l\r\n#L2#No, I think I'll wait a bit...#l");
                status = 1;
            } else if (expedition.isLeader(player)) {
                if (expedition.isInProgress()) {
                    cm.sendOk("Your " + expedBoss + " expedition is already in progress. You cannot manage the roster after the battle has started.");
                    cm.dispose();
                } else {
                    cm.sendSimple(list);
                    status = 2;
                }
            } else if (expedition.isRegistering()) {
                if (expedition.contains(player)) {
                    cm.sendOk("You are already registered for this expedition.\r\n\r\nLeader: #r" + expedition.getLeader().getName() + "#k\r\nPlease wait for the leader to start the battle.");
                    cm.dispose();
                } else {
                    cm.sendOk(expedition.addMember(cm.getPlayer()));
                    cm.dispose();
                }
            } else if (expedition.isInProgress()) {
                if (expedition.contains(player)) {
                    var eim = em.getInstance(expedName + player.getClient().getChannel());
                    if (eim != null && eim.getIntProperty("canJoin") == 1) {
                        eim.registerPlayer(player);
                    } else {
                        cm.sendOk("Your expedition has already entered the " + expedBoss + " battle and late entry is now closed.");
                    }

                    cm.dispose();
                } else {
                    cm.sendOk("A " + expedBoss + " expedition is already in progress on this channel. You are not registered for that expedition.");
                    cm.dispose();
                }
            }
        } else if (status == 1) {
            if (selection == 1) {
                if (!cm.haveItem(expedItem)) {
                    cm.sendOk("You cannot create the " + expedBoss + " expedition yet.\r\n\r\nThe expedition leader must carry #b#t" + expedItem + "##k.");
                    cm.dispose();
                    return;
                }

                expedition = cm.getExpedition(exped);
                if (expedition != null) {
                    cm.sendOk("A " + expedBoss + " expedition is already being organized on this channel. Talk to me again to join it while registration is open.");
                    cm.dispose();
                    return;
                }

                var res = cm.createExpedition(exped);
                if (res == 0) {
                    cm.sendOk("The #r" + expedBoss + " Expedition#k has been created.\r\n\r\nTalk to me again to view the current team or start the fight.");
                } else if (res > 0) {
                    cm.sendOk("You have reached your entry-attempt limit for the " + expedBoss + " expedition. You can try again after the expedition-attempt reset.");
                } else {
                    cm.sendOk("The " + expedBoss + " expedition could not be created because of a server-side error. Please try again. If the problem continues, report it in EverLeaf's bug-report channel.");
                }

                cm.dispose();

            } else if (selection == 2) {
                cm.sendOk("No problem. Come back when you're ready to challenge " + expedBoss + ".");
                cm.dispose();

            }
        } else if (status == 2) {
            if (selection == 1) {
                if (expedition == null) {
                    cm.sendOk("The expedition could not be loaded. Please talk to me again. If this continues, report it in EverLeaf's bug-report channel.");
                    cm.dispose();
                    return;
                }
                expedMembers = expedition.getMemberList();
                var size = expedMembers.size();
                if (size == 1) {
                    cm.sendOk("You are currently the only member of the expedition.");
                    cm.dispose();
                    return;
                }
                var text = "The following members make up your expedition (Click on them to expel them):\r\n";
                text += "\r\n\t\t1." + expedition.getLeader().getName();
                for (var i = 1; i < size; i++) {
                    text += "\r\n#b#L" + (i + 1) + "#" + (i + 1) + ". " + expedMembers.get(i).getValue() + "#l\n";
                }
                cm.sendSimple(text);
                status = 6;
            } else if (selection == 2) {
                var min = exped.getMinSize();

                var size = expedition.getMemberList().size();
                if (size < min) {
                    cm.sendOk("The expedition cannot start yet.\r\n\r\n#bMinimum members: " + min + "#k\r\nCurrently registered: " + size);
                    cm.dispose();
                    return;
                }

                cm.sendOk("The expedition is ready. You will now be escorted to #b" + expedMap + "#k.");
                status = 4;
            } else if (selection == 3) {
                const PacketCreator = Java.type('tools.PacketCreator');
                player.getMap().broadcastMessage(PacketCreator.serverNotice(6, expedition.getLeader().getName() + " has ended the expedition."));
                cm.endExpedition(expedition);
                cm.sendOk("The expedition has been ended.");
                cm.dispose();

            }
        } else if (status == 4) {
            if (em == null) {
                cm.sendOk("The " + expedBoss + " battle event could not be initialized. Please report this in EverLeaf's bug-report channel.");
                cm.dispose();
                return;
            }

            em.setProperty("leader", player.getName());
            em.setProperty("channel", player.getClient().getChannel());
            if (!em.startInstance(expedition)) {
                cm.sendOk("The " + expedBoss + " battle could not start because this channel already has an active instance. Try another channel or wait for the current battle to finish.");
                cm.dispose();
                return;
            }

            cm.dispose();

        } else if (status == 6) {
            if (selection > 0) {
                var banned = expedMembers.get(selection - 1);
                expedition.ban(banned);
                cm.sendOk("You have removed " + banned.getValue() + " from the expedition.");
                cm.dispose();
            } else {
                cm.sendSimple(list);
                status = 2;
            }
        }
    }
}
