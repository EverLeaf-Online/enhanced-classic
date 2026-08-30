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
//First version thanks to Moogra

/**
 * @author: Ronan
 * @npc: Flo
 * @map: Ludibrium - Path of Time (220050300)
 * @func: Elemental Thanatos room
 */

var status = 0;
var em = null;

function start() {
    status = -1;
    action(1, 0, 0);
}

function action(mode, type, selection) {
    if (mode == -1) {
        cm.dispose();
    } else {
        if (mode == 0 && status == 0) {
            cm.dispose();
            return;
        }
        if (mode == 1) {
            status++;
        } else {
            status--;
        }

        if (status == 0) {
            if (!(cm.isQuestCompleted(6316) && (cm.isQuestStarted(6225) || cm.isQuestStarted(6315)))) {
                cm.sendOk("You are not currently on a quest that requires the Elemental Thanatos battle. Continue the appropriate Ludibrium questline and return when it sends you here.");
                cm.dispose();
                return;
            }

            em = cm.getEventManager("ElementalBattle");
            if (em == null) {
                cm.sendOk("The Elemental Thanatos battle is temporarily unavailable because its event could not be loaded. Please report this in EverLeaf's bug-report channel.");
                cm.dispose();
                return;
            } else if (cm.isUsingOldPqNpcStyle()) {
                action(1, 0, 0);
                return;
            }

            cm.sendSimple("#e#b<Party Quest: Elemental Thanatos>\r\n#k#n" + em.getProperty("party") + "\r\n\r\nTeam up with another mage whose elemental affinity complements yours. Keep your eligible party together in this map and have the #bparty leader#k speak with me when you're ready.#b\r\n#L0#Enter the Elemental Thanatos battle.\r\n#L1#" + (cm.getPlayer().isRecvPartySearchInviteEnabled() ? "Disable" : "Enable") + " Party Search invitations.\r\n#L2#Tell me how the battle works.");
        } else if (status == 1) {
            if (selection == 0) {
                if (cm.getParty() == null) {
                    cm.sendOk("You need to be in a party before you can enter the Elemental Thanatos battle.");
                    cm.dispose();
                } else if (!cm.isLeader()) {
                    cm.sendOk("Only your party leader can start this battle. Have the leader speak with me once everyone is ready.");
                    cm.dispose();
                } else {
                    var eli = em.getEligibleParty(cm.getParty());
                    if (eli.size() > 0) {
                        if (!em.startInstance(cm.getParty(), cm.getPlayer().getMap(), 1)) {
                            cm.sendOk("Another party is already fighting Elemental Thanatos in this channel. Try another channel or wait for the current battle to finish.");
                        }
                    } else {
                        cm.sendOk("Your party is not currently eligible. Make sure the required party members meet the quest and class requirements and are together in this map before the leader enters.");
                    }

                    cm.dispose();
                }
            } else if (selection == 1) {
                var psState = cm.getPlayer().toggleRecvPartySearchInvite();
                cm.sendOk("Party Search invitations are now #b" + (psState ? "enabled" : "disabled") + "#k. Talk to me whenever you want to change this setting.");
                cm.dispose();
            } else {
                cm.sendOk("#e#b<Party Quest: Elemental Thanatos>#k#n\r\nTeam up with another mage with a #rdifferent elemental affinity#k before entering. The encounter is designed around using complementary elements together.");
                cm.dispose();
            }
        }
    }
}