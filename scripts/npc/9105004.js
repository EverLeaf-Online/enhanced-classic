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

/* 
 * @Author Ronan
 * Snow Spirit
	Maplemas PQ coordinator
 */

var prizeTree = [[[2000002, 1002850], [20, 1]], [[2000006, 1012011], [20, 1]]];

var state;
var status;
var gift;
var pqType;

function start() {
    pqType = ((cm.getMapId() / 10) % 10) + 1;
    state = (cm.getMapId() % 10 > 0) ? 1 : 0;
    status = -1;
    action(1, 0, 0);
}

function action(mode, type, selection) {
    if (mode == -1) {
        cm.dispose();
    } else {
        if (mode == 0 && type > 0) {
            cm.dispose();
            return;
        }
        if (mode == 1) {
            status++;
        } else {
            status--;
        }

        if (state > 0) {
            insidePqAction(mode, type, selection);
        } else {
            recruitPqAction(mode, type, selection);
        }
    }
}

function recruitPqAction(mode, type, selection) {
    if (status == 0) {
        em = cm.getEventManager("HolidayPQ_" + pqType);
        if (em == null) {
            cm.sendOk("The Holiday Party Quest service could not be loaded. Please report this in EverLeaf's bug-report channel and include Holiday PQ " + pqType + ".");
            cm.dispose();
            return;
        } else if (cm.isUsingOldPqNpcStyle()) {
            action(1, 0, 0);
            return;
        }

        cm.sendSimple("#e#b<Party Quest: Holiday>\r\n#k#n" + em.getProperty("party") + "\r\n\r\nWork with your party to protect Happyville's snowman and defeat Scrooge. Have your #bparty leader#k speak to me when everyone is ready.#b\r\n#L0#Enter the Holiday Party Quest#l\r\n#L1#" + (cm.getPlayer().isRecvPartySearchInviteEnabled() ? "Disable" : "Enable") + " Party Search#l\r\n#L2#Show Holiday Party Quest details#l");
    } else if (status == 1) {
        if (selection == 0) {
            if (cm.getParty() == null) {
                cm.sendOk("You need to be in a party to enter the Holiday Party Quest.");
                cm.dispose();
            } else if (!cm.isLeader()) {
                cm.sendOk("Your party leader must speak to me to start the Holiday Party Quest.");
                cm.dispose();
            } else {
                var eli = em.getEligibleParty(cm.getParty());
                if (eli.size() > 0) {
                    if (!em.startInstance(cm.getParty(), cm.getPlayer().getMap(), pqType)) {
                        cm.sendOk("Another party is already running this Holiday Party Quest in the current channel. Please try another channel or wait for them to finish.");
                    }
                } else {
                    cm.sendOk("Your party cannot enter yet. Make sure the party size is valid, every member is eligible, and all required members are standing here before the leader tries again.");
                }

                cm.dispose();
            }
        } else if (selection == 1) {
            var psState = cm.getPlayer().toggleRecvPartySearchInvite();
            cm.sendOk("Party Search is now #b" + (psState ? "enabled" : "disabled") + "#k for your character.");
            cm.dispose();
        } else {
            cm.sendOk("#e#b<Party Quest: Holiday>#k#n\r\n\r\nProtect the Happyville snowman from Scrooge's forces. Defeated enemies can drop Snow Vigor; bring the real Snow Vigor to the snowman to help it grow. Some drops are fake and will damage the snowman instead, so your party must work together carefully.");
            cm.dispose();
        }
    }
}

function insidePqAction(mode, type, selection) {
    var eim = cm.getEventInstance();
    if (eim == null) {
        cm.sendOk("Your Holiday Party Quest instance is no longer active. If you are stuck in this map, use #b@unstuck#k. If this keeps happening, please report it in EverLeaf's bug-report channel.");
        cm.dispose();
        return;
    }

    var difficulty = eim.getIntProperty("level");
    var stg = eim.getIntProperty("statusStg1");

    var mapobj = eim.getInstanceMap(889100001 + 10 * (difficulty - 1));
    if (mapobj == null) {
        cm.sendOk("This Holiday Party Quest map could not be loaded. Please use #b@unstuck#k if necessary and report the issue in EverLeaf's bug-report channel.");
        cm.dispose();
        return;
    }

    if (status == 0) {
        if (stg == -1) {
            cm.sendNext("#b#h0##k, this is where Happyville builds its giant snowman. Scrooge's forces are attacking it now. Defeat them, collect real Snow Vigor, and drop it on the snowman to help it grow before time runs out. Be careful: some enemies drop fake Snow Vigor that makes the snowman melt faster.");
        } else if (stg == 0) {
            if (cm.getMap().getMonsterById(9400321 + 5 * difficulty) == null) {
                cm.sendNext("Keep defeating Scrooge's underlings and feeding the snowman real Snow Vigor. Scrooge will appear once the snowman has recovered enough.");
                cm.dispose();
            } else {
                cm.sendNext("The snowman has recovered and Scrooge is preparing to appear. Stay ready and keep your party together.");
            }
        } else {
            if (!eim.isEventCleared()) {
                cm.sendNext("Scrooge is still alive. Defeat him to complete the Holiday Party Quest.");
                cm.dispose();
            } else {
                cm.sendNext("You defeated Scrooge and protected Happyville. Nice work!");
            }
        }
    } else if (status == 1) {
        const LifeFactory = Java.type('server.life.LifeFactory');
        const Point = Java.type('java.awt.Point');

        if (stg == -1) {
            if (!cm.isEventLeader()) {
                cm.sendOk("Your party leader must speak to me to begin the snowman-defense stage.");
                cm.dispose();
                return;
            }

            mapobj.allowSummonState(true);
            var snowman = LifeFactory.getMonster(9400317 + (5 * difficulty));
            mapobj.spawnMonsterOnGroundBelow(snowman, new Point(-180, 15));
            eim.setIntProperty("snowmanLevel", 1);
            eim.dropMessage(5, "The snowman has appeared. Protect it and bring it real Snow Vigor!");

            eim.setIntProperty("statusStg1", 0);
            cm.dispose();

        } else if (stg == 0) {
            if (!cm.isEventLeader()) {
                cm.sendOk("Your party leader must speak to me to advance to the Scrooge battle.");
                cm.dispose();
                return;
            }

            mapobj.broadcastStringMessage(5, "The snowman reaches full strength and Scrooge appears!");
            eim.getEm().getIv().invokeFunction("snowmanHeal", eim);

            var boss = LifeFactory.getMonster(9400318 + difficulty);
            mapobj.spawnMonsterOnGroundBelow(boss, new Point(-180, 15));
            eim.setProperty("spawnedBoss", "true");

            eim.setIntProperty("statusStg1", 1);
            cm.dispose();
        } else {
            gift = cm.haveItem(4032092, 1);
            if (gift) {
                var optStr = generateSelectionMenu(generatePrizeString());
                cm.sendSimple("You brought a #b#t4032092##k. Choose your Maplemas gift:\r\n\r\n" + optStr);
            } else if (eim.gridCheck(cm.getPlayer()) == -1) {
                cm.sendNext("Your Holiday Party Quest reward is ready.");
            } else {
                cm.sendOk("Happy Maplemas!");
                cm.dispose();
            }
        }

    } else if (status == 2) {
        if (gift) {
            var selItems = prizeTree[selection];
            if (cm.canHoldAll(selItems[0], selItems[1])) {
                cm.gainItem(4032092, -1);
                cm.gainItem(selItems[0][0], selItems[1][0]);

                if (selection == 1) {
                    var rnd = (Math.random() * 9) | 0;
                    cm.gainItem(selItems[0][1] + rnd, selItems[1][1]);
                } else {
                    cm.gainItem(selItems[0][1], selItems[1][1]);
                }
            } else {
                cm.sendOk("You need enough free space in both your #bEQUIP#k and #bUSE#k inventories before claiming this reward.");
            }
        } else {
            if (eim.giveEventReward(cm.getPlayer(), difficulty)) {
                eim.gridInsert(cm.getPlayer(), 1);
            } else {
                cm.sendOk("You need enough free space in your #bEQUIP#k, #bUSE#k, and #bETC#k inventories before claiming the Party Quest reward.");
            }
        }

        cm.dispose();
    }
}

function generatePrizeString() {
    var strTree = [];

    for (var i = 0; i < prizeTree.length; i++) {
        var items = prizeTree[i][0];
        var qtys = prizeTree[i][1];

        var strSel = "";
        for (var j = 0; j < items.length; j++) {
            strSel += ("#i" + items[j] + "# #t" + items[j] + "#" + (qtys[j] > 1 ? (" : " + qtys[j]) : ""));
        }

        strTree.push(strSel);
    }

    return strTree;
}

function generateSelectionMenu(array) {
    var menu = "";
    for (var i = 0; i < array.length; i++) {
        menu += "#L" + i + "#" + array[i] + "#l\r\n";
    }
    return menu;
}