/*2101017.js
 * Cesar
 * @author Jvlaple
 */

var status = 0;
const ExpeditionType = Java.type('server.expeditions.ExpeditionType');
var exped;
var expedicao;
var expedMembers;

function start() {
    action(1, 0, 0);
}

function action(mode, type, selection) {
    if (mode == -1 || mode == 0) {
        cm.dispose();
        return;
    }

    const GameConstants = Java.type('constants.game.GameConstants');
    var mapId = cm.getPlayer().getMapId();

    if (mapId == 980010100 || mapId == 980010200 || mapId == 980010300) {
        if (mapId == 980010100) {
            exped = ExpeditionType.ARIANT;
        } else if (mapId == 980010200) {
            exped = ExpeditionType.ARIANT1;
        } else {
            exped = ExpeditionType.ARIANT2;
        }

        expedicao = cm.getExpedition(exped);
        if (expedicao == null) {
            cm.sendOk("This Ariant Coliseum lobby is no longer active. Return to the main lobby and choose another arena.");
            cm.dispose();
            return;
        }

        expedMembers = expedicao.getMemberList();
        if (status == 0) {
            if (cm.isLeaderExpedition(exped)) {
                cm.sendSimple("What would you like to do?#b\r\n#L1#View current members#l\r\n#L2#Remove a member#l\r\n#L3#Start the battle#l\r\n#L4#Leave and close the arena#l");
                status = 1;
            } else {
                cm.sendOk("Current members inside this arena:\r\n#b" + cm.getExpeditionMemberNames(exped));
                cm.dispose();
            }
        } else if (status == 1) {
            if (selection == 1) {
                cm.sendOk("Current members inside this arena:\r\n#b" + cm.getExpeditionMemberNames(exped));
                cm.dispose();
            } else if (selection == 2) {
                var size = expedMembers.size();
                if (size == 1) {
                    cm.sendOk("You are currently the only player registered in this arena.");
                    cm.dispose();
                    return;
                }

                var text = "Select a member to remove from the arena:\r\n";
                text += "\r\n\t\t1. " + expedicao.getLeader().getName();
                for (var i = 1; i < size; i++) {
                    text += "\r\n#b#L" + (i + 1) + "#" + (i + 1) + ". " + expedMembers.get(i).getValue() + "#l\n";
                }
                cm.sendSimple(text);
                status = 6;
            } else if (selection == 3) {
                var memberCount = expedicao.getMembers().size();
                if (memberCount < 2) {
                    cm.sendOk("At least #b2 players#k are required to start an Ariant Coliseum battle.\r\n\r\nCurrently registered: #r" + memberCount + "#k");
                    cm.dispose();
                    return;
                }
                if (cm.getParty() != null) {
                    cm.sendOk("Leave your regular party before starting Ariant Coliseum. The arena uses its own participant group.");
                    cm.dispose();
                    return;
                }

                var errorMsg = cm.startAriantBattle(exped, mapId);
                if (errorMsg != "") {
                    cm.sendOk("The battle could not start:\r\n\r\n" + errorMsg);
                }
                cm.dispose();
            } else if (selection == 4) {
                cm.mapMessage(5, "The arena leader has closed the lobby.");
                expedicao.warpExpeditionTeam(980010000);
                cm.endExpedition(expedicao);
                cm.dispose();
            }
        } else if (status == 6) {
            if (selection > 0 && selection <= expedMembers.size()) {
                var banned = expedMembers.get(selection - 1);
                if (banned.getValue() == expedicao.getLeader().getName()) {
                    cm.sendOk("The arena leader cannot remove themselves here. Use 'Leave and close the arena' instead.");
                } else {
                    expedicao.ban(banned);
                    cm.sendOk(banned.getValue() + " has been removed from the arena.");
                }
                cm.dispose();
            } else {
                cm.sendOk("That member selection is no longer valid. Please talk to me again.");
                cm.dispose();
            }
        }
        return;
    }

    if (GameConstants.isAriantColiseumArena(mapId)) {
        if (mapId == 980010101) {
            exped = ExpeditionType.ARIANT;
        } else if (mapId == 980010201) {
            exped = ExpeditionType.ARIANT1;
        } else {
            exped = ExpeditionType.ARIANT2;
        }

        expedicao = cm.getExpedition(exped);
        if (expedicao == null) {
            cm.sendOk("This Ariant Coliseum match is no longer active. If you appear stuck, use @unstuck.");
            cm.dispose();
            return;
        }

        if (status == 0) {
            var gotTheBombs = expedicao.getProperty("gotBomb" + cm.getChar().getId());
            if (gotTheBombs != null) {
                cm.sendOk("You already received your arena supplies. Use the Element Rocks to capture Scorpios and collect Spirit Jewels.");
            } else if (cm.canHoldAll([2270002, 2100067], [50, 5])) {
                cm.sendOk("You received #b50 Element Rocks#k and #b5 Bombs#k.\r\n\r\nUse the Element Rocks to capture Scorpios for #rSpirit Jewels#k.");
                expedicao.setProperty("gotBomb" + cm.getChar().getId(), "1");
                cm.gainItem(2270002, 50);
                cm.gainItem(2100067, 5);
            } else {
                cm.sendOk("You need enough free USE inventory space to receive #b50 Element Rocks#k and #b5 Bombs#k. Clear some space and talk to me again.");
            }
            cm.dispose();
        }
        return;
    }

    cm.sendOk("Ariant Coliseum is a competitive arena for players from #bLv. 20 to Lv. 30#k. Enter through the Ariant Coliseum lobby to participate.");
    cm.dispose();
}
