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
 * @npc: Lakelis
 * @map: 103000000 - Kerning City
 * @func: Kerning PQ
 */

var status = 0;
var state;
var em = null;

function start() {
    status = -1;
    state = (cm.getMapId() >= 103000800 && cm.getMapId() <= 103000805) ? 1 : 0;
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
            if (state == 1) {
                cm.sendYesNo("Leave the Kerning City Party Quest and return to Kerning City? Your current PQ progress will be abandoned.");
            } else {
                em = cm.getEventManager("KerningPQ");
                if (em == null) {
                    cm.sendOk("The Kerning City Party Quest is temporarily unavailable because its event could not be loaded. Please report this in EverLeaf's bug-report channel.");
                    cm.dispose();
                    return;
                } else if (cm.isUsingOldPqNpcStyle()) {
                    action(1, 0, 0);
                    return;
                }

                cm.sendSimple("#e#b<Party Quest: 1st Accompaniment>\r\n#k#n" + em.getProperty("party") + "\r\n\r\nWork with your party to clear a series of cooperative stages. Keep all eligible members together in Kerning City and have the #bparty leader#k speak with me when you're ready.#b\r\n#L0#Enter the Kerning City Party Quest.\r\n#L1#" + (cm.getPlayer().isRecvPartySearchInviteEnabled() ? "Disable" : "Enable") + " Party Search invitations.\r\n#L2#Tell me how the Party Quest works.");
            }
        } else if (status == 1) {
            if (state == 1) {
                cm.warp(103000000);
                cm.dispose();
            } else {
                if (selection == 0) {
                    if (cm.getParty() == null) {
                        cm.sendOk("You need to be in a party before you can enter the Kerning City Party Quest.");
                        cm.dispose();
                    } else if (!cm.isLeader()) {
                        cm.sendOk("Only your party leader can start this Party Quest. Have the leader speak with me once everyone is ready.");
                        cm.dispose();
                    } else {
                        var eli = em.getEligibleParty(cm.getParty());
                        if (eli.size() > 0) {
                            if (!em.startInstance(cm.getParty(), cm.getPlayer().getMap(), 1)) {
                                cm.sendOk("Another party is already running the Kerning City Party Quest in this channel. Try another channel or wait for the current group to finish.");
                            }
                        } else {
                            cm.sendOk("Your party is not currently eligible to enter. Check the required party size and levels, and make sure every participating member is together in Kerning City. Party Search can help if you still need members.");
                        }

                        cm.dispose();
                    }
                } else if (selection == 1) {
                    var psState = cm.getPlayer().toggleRecvPartySearchInvite();
                    cm.sendOk("Party Search invitations are now #b" + (psState ? "enabled" : "disabled") + "#k. Talk to me whenever you want to change this setting.");
                    cm.dispose();
                } else {
                    cm.sendOk("#e#b<Party Quest: 1st Accompaniment>#k#n\r\nYour party must solve cooperative objectives, coordinate through several stages, defeat the final boss, and collect the required item to reach the reward and bonus areas. Stay together and follow the leader's calls.");
                    cm.dispose();
                }
            }
        }
    }
}