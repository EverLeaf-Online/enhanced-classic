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
/* Adobis
 * 
 * El Nath - The Door to Zakum (211042300)
 * 
 * Vs Zakum Recruiter NPC
 * 
 * Custom Quest 100200 = Whether you can start Zakum PQ
 * Custom Quest 100201 = Whether you have done the trials
*/

var status;
var em;
var selectedType;
var gotAllDocs;

function start() {
    status = -1;
    action(1, 0, 0);
}

function action(mode, type, selection) {
    if (mode == -1) {
        cm.dispose();
    } else {
        if (mode == 0) {
            cm.dispose();
            return;
        }
        if (mode == 1) {
            status++;
        } else {
            status--;
        }

        if (cm.haveItem(4001109, 1)) {
            cm.warp(921100000, "out00");
            cm.dispose();
            return;
        }

        if (!(cm.isQuestStarted(100200) || cm.isQuestCompleted(100200))) {
            if (cm.getPlayer().getLevel() >= 50) {
                cm.sendOk("You are high enough level to begin the Zakum pre-quests, but you still need approval from the #bChief's Residence Council#k in El Nath before Adobis can send you into the trials.");
            } else {
                cm.sendOk("The Zakum campaign begins at #blevel 50#k. Your current level is #r" + cm.getPlayer().getLevel() + "#k.");
            }

            cm.dispose();
            return;
        }

        em = cm.getEventManager("ZakumPQ");
        if (em == null) {
            cm.sendOk("The Zakum trial service could not be loaded. Please report this in EverLeaf's bug-report channel and include that you were speaking to Adobis at the Door to Zakum.");
            cm.dispose();
            return;
        }

        if (status == 0) {
            cm.sendSimple("#e#b<Party Quest: Zakum Campaign>\r\n#k#n" + em.getProperty("party") + "\r\n\r\nChoose the Zakum trial you want to attempt:#b\r\n#L0#Stage 1: Enter the Unknown Dead Mine#l\r\n#L1#Stage 2: Face the Breath of Lava#l\r\n#L2#Stage 3: Forge the Eyes of Fire#l");
        } else if (status == 1) {
            if (selection == 0) {
                if (cm.getParty() == null) {
                    cm.sendOk("You need to be in a party to enter Stage 1 of the Zakum trials.");
                    cm.dispose();
                } else if (!cm.isLeader()) {
                    cm.sendOk("Your party leader must speak to me to start Stage 1 of the Zakum trials.");
                    cm.dispose();
                } else {
                    var eli = em.getEligibleParty(cm.getParty());
                    if (eli.size() > 0) {
                        if (!em.startInstance(cm.getParty(), cm.getPlayer().getMap(), 1)) {
                            cm.sendOk("Another party is already running Stage 1 of the Zakum trials in this channel. Please try another channel or wait for them to finish.");
                        }
                    } else {
                        cm.sendOk("Your party cannot enter Stage 1 yet. Make sure every required party member is eligible and standing here at the Door to Zakum before the leader tries again.");
                    }

                    cm.dispose();
                }
            } else if (selection == 1) {
                if (cm.haveItem(4031061) && !cm.haveItem(4031062)) {
                    cm.sendYesNo("You have completed Stage 1. Would you like to attempt #bStage 2: Breath of Lava#k? If you fail, you may die.");
                } else {
                    if (cm.haveItem(4031062)) {
                        cm.sendNext("You already completed Stage 2 and have the #bBreath of Lava#k. You do not need to repeat it.");
                    } else {
                        cm.sendNext("Complete Stage 1 first and bring its proof before attempting the Breath of Lava.");
                    }

                    cm.dispose();
                }
            } else {
                if (cm.haveItem(4031061) && cm.haveItem(4031062)) {
                    if (!cm.haveItem(4000082, 30)) {
                        cm.sendOk("You have completed Stages 1 and 2. To finish Stage 3, bring #b30 #t4000082##k so I can forge #b5 #t4001017##k.");
                    } else {
                        cm.completeQuest(100201);
                        cm.gainItem(4031061, -1);
                        cm.gainItem(4031062, -1);
                        cm.gainItem(4000082, -30);

                        cm.gainItem(4001017, 5);
                        cm.sendNext("You have completed all three Zakum trials. You are now approved to challenge Zakum and have received #b5 #t4001017##k.");
                    }

                    cm.dispose();
                } else {
                    cm.sendOk("You have not completed all required earlier trials yet. Finish Stages 1 and 2 before attempting to forge the Eyes of Fire.");
                    cm.dispose();
                }
            }
        } else if (status == 2) {
            cm.warp(280020000, 0);
            cm.dispose();
        }
    }
}
