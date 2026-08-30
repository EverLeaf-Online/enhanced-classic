/*
    This file is part of the HeavenMS MapleStory Server
    Copyleft (L) 2016 - 2019 RonanLana

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as
    published by the Free Software Foundation version 3 as published by
    the Free Software Foundation. You may not use, modify or distribute
    this program under any other version of the GNU Affero General Public
    License.
*/

/**
 * @author: Ronan
 * @npc: Charles
 * @func: Treasure PQ
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
            em = cm.getEventManager("TreasurePQ");
            if (em == null) {
                cm.sendOk("MV's Lair Party Quest is temporarily unavailable. Please report this in EverLeaf's bug-report channel.");
                cm.dispose();
                return;
            } else if (cm.isUsingOldPqNpcStyle()) {
                action(1, 0, 0);
                return;
            }

            cm.sendSimple("#e#b<Party Quest: MV's Lair>\r\n#k#n" + em.getProperty("party") + "\r\n\r\nHave your #bparty leader#k talk to me when everyone is ready.#b\r\n#L0#Enter the party quest.\r\n#L1#" + (cm.getPlayer().isRecvPartySearchInviteEnabled() ? "Disable" : "Enable") + " Party Search.\r\n#L2#Tell me about this party quest.");
        } else if (status == 1) {
            if (selection == 0) {
                if (cm.getParty() == null) {
                    cm.sendOk("You need to be in a party before entering MV's Lair.");
                    cm.dispose();
                } else if (!cm.isLeader()) {
                    cm.sendOk("Your party leader must talk to me to start MV's Lair.");
                    cm.dispose();
                } else {
                    var eligible = em.getEligibleParty(cm.getParty());
                    if (eligible.size() > 0) {
                        if (!em.startInstance(cm.getParty(), cm.getPlayer().getMap(), 1)) {
                            cm.sendOk("Another party is already running MV's Lair in this channel. Try another channel or wait for the current group to finish.");
                        }
                    } else {
                        cm.sendOk("Your party is not eligible to enter. Check the party-size and level requirements, and make sure every required member is present on this map.");
                    }
                    cm.dispose();
                }
            } else if (selection == 1) {
                var psState = cm.getPlayer().toggleRecvPartySearchInvite();
                cm.sendOk("Party Search is now #b" + (psState ? "enabled" : "disabled") + "#k.");
                cm.dispose();
            } else {
                cm.sendOk("#e#b<Party Quest: MV's Lair>#k#n\r\nForm a party to stop MV and his minions in New Leaf City. Defeat the enemies, complete the party quest, and claim the rewards in MV's treasure room.");
                cm.dispose();
            }
        }
    }
}