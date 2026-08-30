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
 * @npc: Agent Meow
 * @map: 970030000 - Hidden Street - Exclusive Training Center
 * @func: Boss Rush PQ
 */

var status = 0;
var state;
var em = null;

function onRestingSpot() {
    return cm.getMapId() >= 970030001 && cm.getMapId() <= 970030010;
}

function isFinalBossDone() {
    return cm.getMapId() >= 970032700 && cm.getMapId() < 970032800 && cm.getMap().getMonsters().isEmpty();
}

function detectTeamLobby(team) {
    var midLevel = 0;

    for (var i = 0; i < team.size(); i++) {
        var player = team.get(i);
        midLevel += player.getLevel();
    }
    midLevel = Math.floor(midLevel / team.size());

    var lobby;  // teams low level can be allocated at higher leveled lobbys
    if (midLevel <= 20) {
        lobby = 0;
    } else if (midLevel <= 40) {
        lobby = 1;
    } else if (midLevel <= 60) {
        lobby = 2;
    } else if (midLevel <= 80) {
        lobby = 3;
    } else if (midLevel <= 90) {
        lobby = 4;
    } else if (midLevel <= 100) {
        lobby = 5;
    } else if (midLevel <= 110) {
        lobby = 6;
    } else {
        lobby = 7;
    }

    return lobby;
}

function getActiveInstanceOrRecover() {
    var eim = cm.getEventInstance();
    if (eim != null) {
        return eim;
    }

    cm.sendOk("Your Boss Rush instance is no longer active. I will return you to the Exclusive Training Center lobby.");
    cm.warp(970030000);
    cm.dispose();
    return null;
}

function start() {
    status = -1;
    state = (cm.getMapId() >= 970030001 && cm.getMapId() <= 970042711) ? (!onRestingSpot() ? (isFinalBossDone() ? 3 : 1) : 2) : 0;
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
            if (state == 3) {
                var completionEim = getActiveInstanceOrRecover();
                if (completionEim == null) {
                    return;
                }

                if (completionEim.getProperty("clear") == null) {
                    completionEim.clearPQ();
                    completionEim.setProperty("clear", "true");
                }

                if (cm.isEventLeader()) {
                    cm.sendOk("Your party has defeated every Boss Rush opponent. Congratulations! I will prepare your completion reward and return you to the lobby.");
                } else {
                    cm.sendOk("You defeated every Boss Rush opponent. Congratulations! I will prepare your completion reward and return you to the lobby.");
                }
            } else if (state == 2) {
                var restingEim = getActiveInstanceOrRecover();
                if (restingEim == null) {
                    return;
                }

                if (cm.isEventLeader()) {
                    if (restingEim.isEventTeamTogether()) {
                        cm.sendYesNo("Your party is together at the rest area. Are you ready to continue to the next Boss Rush stage?");
                    } else {
                        cm.sendOk("Please wait for your party to reassemble before proceeding.");
                        cm.dispose();
                    }
                } else {
                    cm.sendOk("Wait for your party leader to continue. If you want to stop here, use the exit portal to leave and claim the reward for the progress you made.");
                    cm.dispose();
                }
            } else if (state == 1) {
                cm.sendYesNo("Do you want to abandon this Boss Rush attempt and return to the lobby?");
            } else {
                em = cm.getEventManager("BossRushPQ");
                if (em == null) {
                    cm.sendOk("Boss Rush is temporarily unavailable. Please report this in EverLeaf's bug-report channel if the problem continues.");
                    cm.dispose();
                    return;
                } else if (cm.isUsingOldPqNpcStyle()) {
                    action(1, 0, 0);
                    return;
                }

                cm.sendSimple("#e#b<Party Quest: Boss Rush>#k#n\r\n" + em.getProperty("party") + "\r\n\r\nChallenge a sequence of bosses with a party of up to six players. Your #bparty leader#k must start the run.#b\r\n#L0#Enter Boss Rush with my party.\r\n#L1#" + (cm.getPlayer().isRecvPartySearchInviteEnabled() ? "Disable" : "Enable") + " Party Search.\r\n#L2#Tell me more about Boss Rush.");
            }
        } else if (status == 1) {
            if (state == 3) {
                var rewardEim = getActiveInstanceOrRecover();
                if (rewardEim == null) {
                    return;
                }

                if (!rewardEim.giveEventReward(cm.getPlayer(), 6)) {
                    cm.sendOk("You need at least one free slot in your EQUIP, USE, SET-UP, and ETC inventories before I can give you the Boss Rush reward.");
                    cm.dispose();
                    return;
                }

                cm.warp(970030000);
                cm.dispose();
            } else if (state == 2) {
                var continueEim = getActiveInstanceOrRecover();
                if (continueEim == null) {
                    return;
                }

                var restSpot = ((cm.getMapId() - 1) % 5) + 1;
                continueEim.restartEventTimer(restSpot * 4 * 60000);  // adds (restspot number * 4) minutes
                continueEim.warpEventTeam(970030100 + continueEim.getIntProperty("lobby") + (500 * restSpot));

                cm.dispose();
            } else if (state == 1) {
                cm.warp(970030000);
                cm.dispose();
            } else {
                if (selection == 0) {
                    if (cm.getParty() == null) {
                        cm.sendOk("Create or join a party before starting Boss Rush. A solo player can create a one-person party.");
                        cm.dispose();
                    } else if (!cm.isLeader()) {
                        cm.sendOk("Your party leader must talk to me to start Boss Rush.");
                        cm.dispose();
                    } else {
                        var eli = em.getEligibleParty(cm.getParty());
                        if (eli.size() > 0) {
                            var lobby = detectTeamLobby(eli), i;
                            for (i = lobby; i < 8; i++) {
                                if (em.startInstance(i, cm.getParty(), cm.getPlayer().getMap(), 1)) {
                                    break;
                                }
                            }

                            if (i == 8) {
                                cm.sendOk("All suitable Boss Rush lobbies in this channel are currently occupied. Try another channel or wait for a run to finish.");
                            }
                        } else {
                            cm.sendOk("Your party cannot start Boss Rush yet. Make sure every participating member is eligible and standing in this lobby with the party leader.");
                        }

                        cm.dispose();
                    }
                } else if (selection == 1) {
                    var psState = cm.getPlayer().toggleRecvPartySearchInvite();
                    cm.sendOk("Party Search is now #b" + (psState ? "enabled" : "disabled") + "#k for your character.");
                    cm.dispose();
                } else {
                    cm.sendOk("#e#b<Party Quest: Boss Rush>#k#n\r\nFight through consecutive bosses, with rest areas between sections. Rewards improve with the progress your team reaches, and completing the full run awards the highest reward tier.\r\n\r\nBoss Rush supports multiple level-based lobbies in the same channel so several groups can run it independently.");
                    cm.dispose();
                }
            }
        }
    }
}
