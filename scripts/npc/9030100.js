/*
 * EverLeaf Free Market Utility Hub
 * Uses the existing storage NPC in the Free Market entrance so players
 * get useful services without adding extra map clutter.
 */

var status = -1;
var FREE_MARKET = 910000000;
var GENERAL_STORE_NPC = 2100004;

function start() {
    action(1, 0, 0);
}

function action(mode, type, selection) {
    if (mode != 1) {
        cm.dispose();
        return;
    }

    status++;

    if (status == 0) {
        cm.sendSimple(
            "Welcome to the #bEverLeaf Free Market#k. What do you need?" +
            "#b\r\n#L0#Storage" +
            "\r\n#L1#General supplies" +
            "\r\n#L2#Instant Travel" +
            "\r\n#L3#Return to previous location"
        );
        return;
    }

    if (status == 1) {
        if (selection == 0) {
            cm.getPlayer().getStorage().sendStorage(cm.getClient(), 9030100);
            cm.dispose();
            return;
        }

        if (selection == 1) {
            // Ariant's real general store: basic potions, antidotes, town-return
            // scrolls and starter ammunition only. Do not expose the weapon shop
            // or progression gear through this convenience hub.
            cm.openShopNPC(GENERAL_STORE_NPC);
            cm.dispose();
            return;
        }

        if (selection == 2) {
            cm.dispose();
            cm.openNpc(9000020);
            return;
        }

        if (selection == 3) {
            returnToPreviousLocation();
            return;
        }
    }

    cm.dispose();
}

function returnToPreviousLocation() {
    var savedMap = cm.getPlayer().peekSavedLocation("FREE_MARKET");

    if (savedMap == -1 || savedMap == FREE_MARKET) {
        cm.sendOk(
            "I don't have a previous Free Market return location saved for you.\r\n\r\n" +
            "Use the #bTRADE#k button from a normal map to save your location before entering the Free Market."
        );
        cm.dispose();
        return;
    }

    var returnMap = cm.getPlayer().getSavedLocation("FREE_MARKET");
    if (returnMap == -1 || returnMap == FREE_MARKET) {
        cm.sendOk("Your saved Free Market return location is no longer available. Please use #bInstant Travel#k or #b@unstuck#k if you need help getting back to a town.");
        cm.dispose();
        return;
    }

    cm.warp(returnMap);
    cm.dispose();
}
