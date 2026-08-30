/*
 * EverLeaf Free Market Utility Hub
 * Uses the existing storage NPC in the Free Market entrance so players
 * get useful services without adding extra map clutter.
 *
 * Vote Point policy:
 * - convenience/cosmetics/account-friendly utility only
 * - no direct boss gear, Chaos Scrolls, White Scrolls, EXP multipliers,
 *   damage/stat boosts, or other competitive power
 * - Pet Vac will join this exchange after its server-authoritative
 *   entitlement system is implemented and audited
 */

var status = -1;
var FREE_MARKET = 910000000;
var GENERAL_STORE_NPC = 2100004;

var mainChoice = -1;
var voteChoice = -1;

var MAPLE_LEAF = 4001126;
var SAFETY_CHARM = 5130000;
var HIRED_MERCHANT = 5030000;

var VOTE_LEAF_COST = 1;
var VOTE_LEAF_QTY = 10;
var VOTE_CHARM_COST = 2;
var VOTE_CHARM_QTY = 5;
var VOTE_MERCHANT_COST = 3;
var VOTE_MERCHANT_DAYS = 7;
var VOTE_CHAIR_COST = 1;

// Stock-v83 chairs only. Keep this list cosmetic; no chairs with progression
// rewards, boss access, combat buffs, or item-generation behavior.
var voteChairs = [
    3010000, 3010001, 3010002, 3010003, 3010004,
    3010005, 3010006, 3010007, 3010008, 3010009,
    3010010, 3010011, 3010012, 3010013, 3010015,
    3010016, 3010017, 3010018, 3010019, 3010022,
    3010023, 3010024, 3010025, 3010026, 3010028
];

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
            "\r\n#L3#Return to previous location" +
            "\r\n#L4#Vote Point Exchange"
        );
        return;
    }

    if (status == 1) {
        mainChoice = selection;

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

        if (selection == 4) {
            showVoteExchange();
            return;
        }

        cm.dispose();
        return;
    }

    if (status == 2 && mainChoice == 4) {
        voteChoice = selection;
        confirmVotePurchase(selection);
        return;
    }

    if (status == 3 && mainChoice == 4) {
        completeVotePurchase(voteChoice);
        return;
    }

    cm.dispose();
}

function showVoteExchange() {
    var vp = cm.getClient().getVotePoints();
    var msg = "#eEverLeaf Vote Point Exchange#n\r\n" +
        "You currently have #r" + vp + " Vote Point" + (vp == 1 ? "" : "s") + "#k.\r\n\r\n" +
        "Voting should provide useful convenience and cosmetic choices without becoming mandatory for character power.\r\n" +
        "#b#L0#" + VOTE_LEAF_QTY + " Maple Leaves - " + VOTE_LEAF_COST + " VP#l" +
        "\r\n#L1#" + VOTE_CHARM_QTY + " Safety Charms - " + VOTE_CHARM_COST + " VP#l" +
        "\r\n#L2#" + VOTE_MERCHANT_DAYS + "-day Hired Merchant - " + VOTE_MERCHANT_COST + " VP#l" +
        "\r\n#L3#Random cosmetic chair - " + VOTE_CHAIR_COST + " VP#l#k" +
        "\r\n\r\n#dPet Vac will be added here after its server-side entitlement and anti-abuse checks are finished.#k";
    cm.sendSimple(msg);
}

function confirmVotePurchase(selection) {
    if (selection == 0) {
        cm.sendYesNo("Exchange #r" + VOTE_LEAF_COST + " Vote Point#k for #b" + VOTE_LEAF_QTY + " #t" + MAPLE_LEAF + "##k?");
    } else if (selection == 1) {
        cm.sendYesNo("Exchange #r" + VOTE_CHARM_COST + " Vote Points#k for #b" + VOTE_CHARM_QTY + " #t" + SAFETY_CHARM + "##k?");
    } else if (selection == 2) {
        cm.sendYesNo("Exchange #r" + VOTE_MERCHANT_COST + " Vote Points#k for a #b" + VOTE_MERCHANT_DAYS + "-day #t" + HIRED_MERCHANT + "##k?");
    } else if (selection == 3) {
        cm.sendYesNo("Exchange #r" + VOTE_CHAIR_COST + " Vote Point#k for #bone random cosmetic chair#k?");
    } else {
        cm.dispose();
    }
}

function completeVotePurchase(selection) {
    if (selection == 0) {
        if (!hasVotePoints(VOTE_LEAF_COST)) return;
        if (!cm.canHold(MAPLE_LEAF, VOTE_LEAF_QTY)) {
            cm.sendOk("Please make enough room in your ETC inventory first.");
            cm.dispose();
            return;
        }
        cm.getClient().useVotePoints(VOTE_LEAF_COST);
        cm.gainItem(MAPLE_LEAF, VOTE_LEAF_QTY);
        purchaseSuccess(VOTE_LEAF_COST, VOTE_LEAF_QTY + " Maple Leaves");
        return;
    }

    if (selection == 1) {
        if (!hasVotePoints(VOTE_CHARM_COST)) return;
        if (!cm.canHold(SAFETY_CHARM, VOTE_CHARM_QTY)) {
            cm.sendOk("Please make enough room in your Cash inventory first.");
            cm.dispose();
            return;
        }
        cm.getClient().useVotePoints(VOTE_CHARM_COST);
        cm.gainItem(SAFETY_CHARM, VOTE_CHARM_QTY);
        purchaseSuccess(VOTE_CHARM_COST, VOTE_CHARM_QTY + " Safety Charms");
        return;
    }

    if (selection == 2) {
        if (!hasVotePoints(VOTE_MERCHANT_COST)) return;
        const InventoryType = Java.type('client.inventory.InventoryType');
        if (cm.haveItem(HIRED_MERCHANT, 1)) {
            cm.sendOk("You already have a Hired Merchant. Use or remove it before purchasing another one.");
            cm.dispose();
            return;
        }
        if (cm.getPlayer().getInventory(InventoryType.CASH).isFull(1)) {
            cm.sendOk("Please make room in your Cash inventory first.");
            cm.dispose();
            return;
        }
        cm.getClient().useVotePoints(VOTE_MERCHANT_COST);
        cm.gainItem(HIRED_MERCHANT, 1, false, true, 1000 * 60 * 60 * 24 * VOTE_MERCHANT_DAYS);
        purchaseSuccess(VOTE_MERCHANT_COST, VOTE_MERCHANT_DAYS + "-day Hired Merchant");
        return;
    }

    if (selection == 3) {
        if (!hasVotePoints(VOTE_CHAIR_COST)) return;
        const InventoryType = Java.type('client.inventory.InventoryType');
        if (cm.getPlayer().getInventory(InventoryType.SETUP).isFull(1)) {
            cm.sendOk("Please make room in your Setup inventory first.");
            cm.dispose();
            return;
        }
        var chair = voteChairs[Math.floor(Math.random() * voteChairs.length)];
        cm.getClient().useVotePoints(VOTE_CHAIR_COST);
        cm.gainItem(chair, 1, true);
        purchaseSuccess(VOTE_CHAIR_COST, "cosmetic chair #" + chair);
        return;
    }

    cm.dispose();
}

function hasVotePoints(cost) {
    var vp = cm.getClient().getVotePoints();
    if (vp < cost) {
        cm.sendOk("You need #r" + cost + " Vote Point" + (cost == 1 ? "" : "s") + "#k for that exchange. You currently have #b" + vp + "#k.");
        cm.dispose();
        return false;
    }
    return true;
}

function purchaseSuccess(cost, reward) {
    cm.sendOk("Exchange complete.\r\n\r\n#r-" + cost + " Vote Point" + (cost == 1 ? "" : "s") + "#k\r\n#b+" + reward + "#k\r\n\r\nRemaining Vote Points: #e" + cm.getClient().getVotePoints() + "#n");
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
