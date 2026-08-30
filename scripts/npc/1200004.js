/**
 ----------------------------------------------------------------------------------
 Whale Between Lith Harbor and Rien.

 1200004 Puro - Lith Harbor -> Rien

 Credits to: MapleSanta
 ----------------------------------------------------------------------------------
 **/

const PersonalTravelService = Java.type('server.travel.PersonalTravelService');

var RIDE_SECONDS = 60;
var FIRST_SHIP_MAP = 200090060;
var SHIP_COUNT = 10;
var status = -1;

function start() {
    status = -1;
    action(1, 0, 0);
}

function action(mode, type, selection) {
    if (mode == -1) {
        cm.dispose();
        return;
    }

    if (mode == 0) {
        if (status > 0) {
            cm.sendNext("OK. If you ever change your mind, please let me know.");
        }
        cm.dispose();
        return;
    }

    status++;
    if (status == 0) {
        cm.sendYesNo("Are you thinking about leaving Victoria Island and heading to Rien? I can take you from #bLith Harbor#k to #bRien#k for a #bfee of 800#k Mesos. Would you like to go now? It'll take about a minute to get there.");
        return;
    }

    if (cm.getMeso() < 800) {
        cm.sendNext("Hmm... Are you sure you have #b800#k Mesos? Check your Inventory and make sure you have enough. You must pay the fee or I can't let you get on...");
        cm.dispose();
        return;
    }

    var shipMap = -1;
    for (var i = 0; i < SHIP_COUNT; i++) {
        var candidate = FIRST_SHIP_MAP + i;
        if (cm.getPlayerCount(candidate) == 0) {
            shipMap = candidate;
            break;
        }
    }

    if (shipMap == -1) {
        cm.sendNext("All of the ships are in use right now. Please try again in a moment.");
        cm.dispose();
        return;
    }

    cm.gainMeso(-800);
    cm.warp(shipMap, 0);
    PersonalTravelService.begin(cm.getPlayer(), RIDE_SECONDS);
    cm.dispose();
}
