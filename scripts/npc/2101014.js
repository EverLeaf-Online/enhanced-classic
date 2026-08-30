/*2101014.js - Lobby and Entrance
 * @author Jvlaple
 * For Jvlaple's AriantPQ
 */

var status = 0;
var arenaType;
var map;
const ExpeditionType = Java.type('server.expeditions.ExpeditionType');
var exped = ExpeditionType.ARIANT;
var exped1 = ExpeditionType.ARIANT1;
var exped2 = ExpeditionType.ARIANT2;

function start() {
    status = -1;
    action(1, 0, 0);
}

function action(mode, type, selection) {
    if (mode == -1) {
        cm.dispose();
        return;
    }
    if (mode == 0 && status == 0) {
        cm.dispose();
        return;
    }

    status += mode == 1 ? 1 : -1;

    if (cm.getPlayer().getMapId() != 980010000) {
        return;
    }

    if (cm.getLevel() > 30) {
        cm.sendOk("Ariant Coliseum is available through #rLv. 30#k.\r\n\r\nYour level: #rLv. " + cm.getLevel() + "#k");
        cm.dispose();
        return;
    }

    if (status == 0) {
        var expedicao = cm.getExpedition(exped);
        var expedicao1 = cm.getExpedition(exped1);
        var expedicao2 = cm.getExpedition(exped2);
        var channelMaps = cm.getClient().getChannelServer().getMapFactory();
        var startSnd = "Choose an Ariant Coliseum Battle Arena:\r\n\r\n#b";
        var toSnd = startSnd;

        if (expedicao == null) {
            toSnd += "#L0#Arena 1 - Empty#l\r\n";
        } else if (channelMaps.getMap(980010101).getCharacters().isEmpty()) {
            toSnd += "#L0#Arena 1 - Join " + expedicao.getLeader().getName() + "#l\r\n";
        }
        if (expedicao1 == null) {
            toSnd += "#L1#Arena 2 - Empty#l\r\n";
        } else if (channelMaps.getMap(980010201).getCharacters().isEmpty()) {
            toSnd += "#L1#Arena 2 - Join " + expedicao1.getLeader().getName() + "#l\r\n";
        }
        if (expedicao2 == null) {
            toSnd += "#L2#Arena 3 - Empty#l\r\n";
        } else if (channelMaps.getMap(980010301).getCharacters().isEmpty()) {
            toSnd += "#L2#Arena 3 - Join " + expedicao2.getLeader().getName() + "#l\r\n";
        }

        if (toSnd === startSnd) {
            cm.sendOk("All Ariant Coliseum arenas are currently occupied. Try another channel or wait for an arena to become available.");
            cm.dispose();
        } else {
            cm.sendSimple(toSnd);
        }
    } else if (status == 1) {
        arenaType = selection;
        var expedicao = fetchArenaType();
        if (expedicao === "") {
            cm.sendOk("That arena selection is invalid. Please talk to me again.");
            cm.dispose();
            return;
        }

        if (expedicao != null) {
            enterArena(-1);
        } else {
            cm.sendGetText("How many players may join this arena? Enter a number from 2 to 5.");
        }
    } else if (status == 2) {
        var players = parseInt(cm.getText());
        if (isNaN(players)) {
            cm.sendNext("Please enter a number from 2 to 5.");
            status = 0;
        } else if (players < 2 || players > 5) {
            cm.sendNext("Arena size must be between 2 and 5 players.");
            status = 0;
        } else {
            enterArena(players);
        }
    }
}

function fetchArenaType() {
    var expedicao;
    switch (arenaType) {
        case 0:
            exped = ExpeditionType.ARIANT;
            expedicao = cm.getExpedition(exped);
            map = 980010100;
            break;
        case 1:
            exped = ExpeditionType.ARIANT1;
            expedicao = cm.getExpedition(exped);
            map = 980010200;
            break;
        case 2:
            exped = ExpeditionType.ARIANT2;
            expedicao = cm.getExpedition(exped);
            map = 980010300;
            break;
        default:
            exped = null;
            map = 0;
            expedicao = "";
    }
    return expedicao;
}

function enterArena(arenaPlayers) {
    var expedicao = fetchArenaType();
    if (expedicao === "") {
        cm.sendOk("That arena selection is invalid. Please talk to me again.");
        cm.dispose();
        return;
    }

    if (expedicao == null) {
        if (arenaPlayers == -1) {
            cm.sendOk("The selected arena could not be located. Please talk to me again. If this continues, report it in EverLeaf's bug-report channel.");
            cm.dispose();
            return;
        }

        var res = cm.createExpedition(exped, true, 0, arenaPlayers);
        if (res == 0) {
            cm.warp(map, 0);
            cm.getPlayer().dropMessage("Your Ariant Coliseum arena was created. Wait here for other players to join.");
        } else if (res > 0) {
            cm.sendOk("You have reached the entry-attempt limit for Ariant Coliseum. Try again after the limit resets.");
        } else {
            cm.sendOk("The arena could not be created because of an unexpected server error. Please try again, and report it if the problem continues.");
        }
        cm.dispose();
        return;
    }

    if (playerAlreadyInLobby(cm.getPlayer())) {
        cm.sendOk("You are already registered in an Ariant Coliseum lobby.");
        cm.dispose();
        return;
    }

    var playerAdd = expedicao.addMemberInt(cm.getPlayer());
    if (playerAdd == 0) {
        cm.warp(map, 0);
    } else if (playerAdd == 3) {
        cm.sendOk("This Ariant Coliseum lobby is full. Choose another arena or try another channel.");
    } else if (playerAdd == 2) {
        cm.sendOk("The arena leader is not accepting your entry.");
    } else {
        cm.sendOk("Your arena entry could not be completed. Please try again; if this continues, report it in EverLeaf's bug-report channel.");
    }
    cm.dispose();
}

function playerAlreadyInLobby(player) {
    return (cm.getExpedition(ExpeditionType.ARIANT) != null && cm.getExpedition(ExpeditionType.ARIANT).contains(player)) ||
        (cm.getExpedition(ExpeditionType.ARIANT1) != null && cm.getExpedition(ExpeditionType.ARIANT1).contains(player)) ||
        (cm.getExpedition(ExpeditionType.ARIANT2) != null && cm.getExpedition(ExpeditionType.ARIANT2).contains(player));
}
