var quantities = Array(10, 8, 6, 5, 4, 3, 2, 1, 1, 1);
var prize1 = Array(1442047, 2000000, 2000001, 2000002, 2000003, 2000004, 2000005, 2430036, 2430037, 2430038, 2430039, 2430040); //1 day
var prize2 = Array(1442047, 4080100, 4080001, 4080002, 4080003, 4080004, 4080005, 4080006, 4080007, 4080008, 4080009, 4080010, 4080011);
var prize3 = Array(1442047, 1442048, 2022070);
var prize4 = Array(1442048, 2430082, 2430072); //7 day
var prize5 = Array(1442048, 2430091, 2430092, 2430093, 2430101, 2430102); //10 day
var prize6 = Array(1442048, 1442050, 2430073, 2430074, 2430075, 2430076, 2430077); //15 day
var prize7 = Array(1442050, 3010183, 3010182, 3010053, 2430080); //20 day
var prize8 = Array(1442050, 3010178, 3010177, 3010075, 1442049, 2430053, 2430054, 2430055, 2430056, 2430103, 2430136); //30 day
var prize9 = Array(1442049, 3010123, 3010175, 3010170, 3010172, 3010173, 2430201, 2430228, 2430229); //60 day
var prize10 = Array(1442049, 3010172, 3010171, 3010169, 3010168, 3010161, 2430117, 2430118, 2430119, 2430120, 2430137); //1 year
var status = 0;

function start() {
    status = -1;
    action(1, 0, 0);
}

function action(mode, type, selection) {
    if (mode == -1) {
        cm.dispose();
    } else {
        if (status >= 0 && mode == 0) {
            cm.dispose();
            return;
        }
        if (mode == 1) {
            status++;
        } else {
            status--;
        }
        if (status == 0) {
            cm.sendNext("Hey! EverLeaf events are a good break from regular adventuring. Want to hear what's available?");
        } else if (status == 1) {
            cm.sendSimple("What would you like to know?\r\n#L0##bWhat kind of event is it?#k#l\r\n#L1##bExplain the event games.#k#l\r\n#L2##bTake me to the active event.#k#l\r\n#L3##bExchange win certificates for rewards.#k#l");
        } else if (status == 2) {
            if (selection == 0) {
                cm.sendNext("EverLeaf staff may open surprise GM events from time to time. When an event is active, you can use this NPC to join if you meet the entry requirements.");
                cm.dispose();
            } else if (selection == 1) {
                cm.sendSimple("Choose an event for an explanation:#b\r\n#L0#Ola Ola#l\r\n#L1#Physical Fitness Test#l\r\n#L2#Snow Ball#l\r\n#L3#Coconut Harvest#l\r\n#L4#OX Quiz#l\r\n#L5#Treasure Hunt#l#k");
            } else if (selection == 2) {
                var marr = cm.getQuestRecord(100295);
                if (marr.getCustomData() == null) {
                    marr.setCustomData("0");
                }
                var dat = parseInt(marr.getCustomData());
                if (dat + 3600000 >= cm.getCurrentTime()) {
                    cm.sendNext("You joined an event within the last hour. Please wait until the one-hour entry cooldown has expired.");
                } else if (!cm.canHold(4031019)) {
                    cm.sendNext("You need at least one free ETC inventory slot before entering the event.");
                } else if (cm.getChannelServer().getEvent() > -1 && !cm.haveItem(4031019)) {
                    cm.getPlayer().saveLocation("EVENT");
                    cm.getPlayer().setChalkboard(null);
                    marr.setCustomData("" + cm.getCurrentTime());
                    cm.warp(cm.getChannelServer().getEvent(), cm.getChannelServer().getEvent() == 109080000 || cm.getChannelServer().getEvent() == 109080010 ? 0 : "join00");
                } else if (cm.getChannelServer().getEvent() <= -1) {
                    cm.sendNext("There is no GM event accepting players on this channel right now.");
                } else if (cm.haveItem(4031019)) {
                    cm.sendNext("You are already carrying a #bScroll of Secrets#k, so you cannot enter this event yet.");
                } else {
                    cm.sendNext("You cannot enter the event right now. Please try again in a moment.");
                }
                cm.dispose();
            } else if (selection == 3) {
                var selStr = "Which win certificate would you like to exchange?";
                for (var i = 0; i < quantities.length; i++) {
                    selStr += "\r\n#b#L" + i + "##t" + (4031332 + i) + "# x" + quantities[i] + "#l";
                }
                cm.sendSimple(selStr);
                status = 9;
            }
        } else if (status == 3) {
            if (selection == 0) {
                cm.sendNext("#b[Ola Ola]#k is a game where participants climb ladders to reach the top. Climb your way up and move to the next level by choosing the correct portal out of the numerous portals available. \r\n\r\nThe game consists of three levels, and the time limit is #b6 MINUTES#k. During [Ola Ola], you #bwon't be able to jump, teleport, haste, or boost your speed using potions or items#k. There are also trick portals that'll lead you to a strange place, so please be aware of those.");
                cm.dispose();
            } else if (selection == 1) {
                cm.sendNext("#b[Physical Fitness Test]#k is a race through an obstacle course much like the Forest of Patience. Reach the destination within the time limit while overcoming the obstacles.\r\n\r\nThe game consists of four levels, and the time limit is #b15 MINUTES#k. Teleport and Haste cannot be used during the event.");
                cm.dispose();
            } else if (selection == 2) {
                cm.sendNext("#b[Snow Ball]#k consists of two teams competing to roll their snowball farther and make it larger before time expires. If time expires without a finish, the team with the farther snowball wins.\r\n\r\nAttack the snowball with #bregular close-range attacks#k. Long-range attacks and skills do not work here. Touching the snowball sends you back to the starting point. You can also attack the opposing snowman to slow the other team.");
                cm.dispose();
            } else if (selection == 3) {
                cm.sendNext("#b[Coconut Harvest]#k pits two teams against each other to collect the most coconuts. The time limit is #b5 MINUTES#k, with extra time used for a tie.\r\n\r\nOnly regular close-range attacks work on the coconuts. The player landing the final hit before a coconut drops receives credit. Watch for obstacles, traps, and the hidden portal near the bottom of the map.");
                cm.dispose();
            } else if (selection == 4) {
                cm.sendNext("#b[OX Quiz]#k tests your game knowledge using X and O answer zones. Turn on the minimap with #bM#k so you can see both areas. Move to your answer before time expires and stay there until the result is shown. Players who answer incorrectly or fail to choose are eliminated.");
                cm.dispose();
            } else if (selection == 5) {
                cm.sendNext("#b[Treasure Hunt]#k gives you #r10 minutes#k to break treasure chests and find hidden treasure scrolls. Attack skills are disabled, so use regular attacks on the chests. Hidden portals and paths are scattered around the map, and some treasure can only be reached through them.");
                cm.dispose();
            }
        } else if (status == 10) {
            if (selection < 0 || selection >= quantities.length) {
                cm.sendOk("That reward selection is no longer valid. Please talk to me again.");
                cm.dispose();
                return;
            }
            var ite = 4031332 + selection;
            var quan = quantities[selection];
            var pri;
            switch (selection) {
                case 0:
                    pri = prize1;
                    break;
                case 1:
                    pri = prize2;
                    break;
                case 2:
                    pri = prize3;
                    break;
                case 3:
                    pri = prize4;
                    break;
                case 4:
                    pri = prize5;
                    break;
                case 5:
                    pri = prize6;
                    break;
                case 6:
                    pri = prize7;
                    break;
                case 7:
                    pri = prize8;
                    break;
                case 8:
                    pri = prize9;
                    break;
                case 9:
                    pri = prize10;
                    break;
                default:
                    cm.dispose();
                    return;
            }
            var rand = Math.floor(Math.random() * pri.length);
            if (!cm.haveItem(ite, quan)) {
                cm.sendOk("You need #b" + quan + " #t" + ite + "##k for this exchange.");
            } else if (cm.getInventory(1).getNextFreeSlot() <= -1 || cm.getInventory(2).getNextFreeSlot() <= -1 || cm.getInventory(3).getNextFreeSlot() <= -1 || cm.getInventory(4).getNextFreeSlot() <= -1) {
                cm.sendOk("Make at least one free slot in each non-Cash inventory tab before exchanging the certificate so the reward has somewhere to go.");
            } else {
                cm.gainItem(pri[rand], 1);
                cm.gainItem(ite, -quan);
                cm.gainMeso(100000 * selection); // legacy event reward
            }
            cm.dispose();
        }
    }
}
