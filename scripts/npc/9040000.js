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
 * @npc: Shuang
 * @map: Victoria Road: Excavation Site<Camp> (101030104)
 * @func: Start Guild PQ
 */

var status = 0;
var sel;
var em = null;

function findLobby(guild) {
    for (var iterator = em.getInstances().iterator(); iterator.hasNext();) {
        var lobby = iterator.next();

        if (lobby.getIntProperty("guild") == guild) {
            if (lobby.getIntProperty("canJoin") == 1) {
                return lobby;
            } else {
                return null;
            }
        }
    }

    return null;
}

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
            em = cm.getEventManager("GuildQuest");
            if (em == null) {
                cm.sendOk("The Guild Quest service could not be loaded. Please report this in EverLeaf's bug-report channel and mention Sharenian Ruins.");
                cm.dispose();
                return;
            }

            cm.sendSimple("#e#b<Guild Quest: Sharenian Ruins>\r\n#k#n" + em.getProperty("party") + "\r\n\r\nThe path to Sharenian starts here. What would you like to do?#b\r\n#L0#Register my guild for the Guild Quest#l\r\n#L1#Join my guild's active Guild Quest lobby#l\r\n#L2#Show Guild Quest details and team requirements#l");
        } else if (status == 1) {
            sel = selection;
            if (selection == 0) {
                if (!cm.isGuildLeader()) {
                    cm.sendOk("Only your #bguild master or junior master#k can register the guild for Sharenian Ruins.");
                    cm.dispose();
                } else {
                    if (em.isQueueFull()) {
                        cm.sendOk("This channel's Guild Quest queue is full. Please try another channel or wait for a queued guild to finish.");
                        cm.dispose();
                    } else {
                        var qsize = em.getQueueSize();
                        cm.sendYesNo(((qsize > 0) ? "There are currently #r" + qsize + "#k guild(s) ahead of you in this channel's queue.\r\n\r\n" : "") + "Register your guild for this channel's Guild Quest queue?");
                    }
                }
            } else if (selection == 1) {
                if (cm.getPlayer().getGuildId() > 0) {
                    var eim = findLobby(cm.getPlayer().getGuildId());
                    if (eim == null) {
                        cm.sendOk("Your guild does not currently have an open Guild Quest lobby on this channel. Check with your guild leader to confirm the assigned channel and whether strategy time is still open.");
                    } else {
                        if (cm.isLeader()) {
                            em.getEligibleParty(cm.getParty());
                            eim.registerParty(cm.getPlayer());
                        } else {
                            eim.registerPlayer(cm.getPlayer());
                        }
                    }
                } else {
                    cm.sendOk("You must belong to a guild before you can enter the Guild Quest.");
                }

                cm.dispose();
            } else {
                var reqStr = "";
                reqStr += "\r\n\r\n    Recommended team coverage:\r\n\r\n";
                reqStr += "     - 1 member #rlevel 30 or below#k.\r\n";
                reqStr += "     - 1 #rThief#k with Dark Sight and strong Haste.\r\n";
                reqStr += "     - 1 #rMagician#k with Teleport.\r\n";
                reqStr += "     - 1 #rlong-range attacker#k such as Bowman, Assassin, or Gunslinger.\r\n";
                reqStr += "     - 1 member with strong mobility/jumping skills.\r\n";

                cm.sendOk("#e#b<Guild Quest: Sharenian Ruins>#k#n\r\nWork with your guild to recover the Rubian from Sharenian. The quest contains combat, movement challenges, and puzzles, so bringing a varied team is strongly recommended. Successful clears award Guild Points and other rewards." + reqStr);
                cm.dispose();
            }
        } else if (status == 2) {
            if (sel == 0) {
                var entry = em.addGuildToQueue(cm.getPlayer().getGuildId(), cm.getPlayer().getId());
                if (entry > 0) {
                    cm.sendOk("Your guild is now registered in this channel's Guild Quest queue.\r\n\r\n#rImportant:#k the registering leader must remain available on this channel when the guild is called for strategy time. If the leader is absent when called, the registration may be skipped and the next guild will be selected.");
                } else if (entry == 0) {
                    cm.sendOk("This channel's Guild Quest queue became full before your registration completed. Please try another channel or wait and try again.");
                } else {
                    cm.sendOk("Your guild is already queued for a Guild Quest. Please wait for that registration to finish before registering again.");
                }
            }

            cm.dispose();
        }
    }
}