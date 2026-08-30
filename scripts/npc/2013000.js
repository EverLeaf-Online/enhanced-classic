/*
    This file is part of the HeavenMS MapleStory Server
    Copyleft (L) 2016 - 2019 RonanLana

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

/**
 * @author: Ronan
 * @npc: Wonky
 * @map: 200080101 - Orbis - The Unknown Tower
 * @func: Orbis PQ
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

        if (cm.getMapId() == 200080101) {
            if (status == 0) {
                em = cm.getEventManager("OrbisPQ");
                if (em == null) {
                    cm.sendOk("The Tower of Goddess Party Quest is temporarily unavailable because its event could not be loaded. Please report this in EverLeaf's bug-report channel.");
                    cm.dispose();
                    return;
                } else if (cm.isUsingOldPqNpcStyle()) {
                    action(1, 0, 0);
                    return;
                }

                cm.sendSimple("#e#b<Party Quest: Tower of Goddess>\r\n#k#n" + em.getProperty("party") + "\r\n\r\nAssemble an eligible party to reclaim the Tower of Goddess. Keep everyone together at the entrance and have the #bparty leader#k speak with me when you're ready.#b\r\n#L0#Enter the Tower of Goddess Party Quest.\r\n#L1#" + (cm.getPlayer().isRecvPartySearchInviteEnabled() ? "Disable" : "Enable") + " Party Search invitations.\r\n#L2#Tell me about the Party Quest.\r\n#L3#Exchange Goddess Feathers for a Goddess Wristband.");
            } else if (status == 1) {
                if (selection == 0) {
                    if (cm.getParty() == null) {
                        cm.sendOk("You need to be in a party before you can enter the Tower of Goddess.");
                        cm.dispose();
                    } else if (!cm.isLeader()) {
                        cm.sendOk("Only your party leader can start this Party Quest. Have the leader speak with me once everyone is ready.");
                        cm.dispose();
                    } else {
                        var eli = em.getEligibleParty(cm.getParty());
                        if (eli.size() > 0) {
                            if (!em.startInstance(cm.getParty(), cm.getPlayer().getMap(), 1)) {
                                cm.sendOk("Another party is already running the Tower of Goddess in this channel. Try another channel or wait for the current group to finish.");
                            }
                        } else {
                            cm.sendOk("Your party is not currently eligible to enter. Check the required party size and levels, and make sure every participating member is together at the entrance. Party Search can help if you still need members.");
                        }

                        cm.dispose();
                    }
                } else if (selection == 1) {
                    var psState = cm.getPlayer().toggleRecvPartySearchInvite();
                    cm.sendOk("Party Search invitations are now #b" + (psState ? "enabled" : "disabled") + "#k. Talk to me whenever you want to change this setting.");
                    cm.dispose();
                } else if (selection == 2) {
                    cm.sendOk("#e#b<Party Quest: Tower of Goddess>#k#n\r\nThe goddess has disappeared and Papa Pixie has taken over the sanctuary. Your party must solve the tower's cooperative stages, defeat Papa Pixie, and rescue the goddess. A party containing all five Explorer job archetypes can receive an additional blessing inside the challenge.");
                    cm.dispose();
                } else {
                    cm.sendSimple("Exchange #b10 #t4001158##k for a Goddess Wristband.#b\r\n#L0#Exchange 10 #t4001158# for #t1082232#.");
                }
            } else if (status == 2) {
                if (selection == 0) {
                    if (cm.haveItem(1082232)) {
                        cm.sendOk("You already have a Goddess Wristband.");
                    } else if (!cm.haveItem(4001158, 10)) {
                        cm.sendOk("You need #b10 #t4001158##k for this exchange.");
                    } else {
                        cm.gainItem(1082232, 1);
                        cm.gainItem(4001158, -10);
                    }
                    cm.dispose();
                }
            }
        } else {
            if (status == 0) {
                cm.sendYesNo("Leave the Tower of Goddess Party Quest? Your current rescue-mission progress will be abandoned.");
            } else if (status == 1) {
                cm.warp(920011200);
                cm.dispose();
            }
        }
    }
}