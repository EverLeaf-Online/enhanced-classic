/*
 * EverLeaf Maple Leaf Exchange
 *
 * Maple Leaves are an earnable secondary currency. This shop is a deliberate
 * sink for cosmetics and convenience/low-mid progression only. It never
 * converts Leaves into NX and never sells Chaos Scrolls, White Scrolls, or
 * endgame equipment.
 */

var status = -1;
var selection = -1;

var MAPLE_LEAF = 4001126;
var AP_RESET = 5050000;
var SAFETY_CHARM = 5130000;
var HIRED_MERCHANT = 5030000;

var AP_RESET_LEAVES = 15;
var CHARM_LEAVES = 25;
var CHARM_QTY = 5;
var CHAIR_LEAVES = 30;
var MERCHANT_LEAVES = 40;
var MERCHANT_MESO = 500000;
var MERCHANT_DAYS = 7;
var MAPLE_WEAPON_LEAVES = 60;
var MAPLE_WEAPON_MESO = 1000000;

var chairs = [
    3010000, 3010001, 3010002, 3010003, 3010004,
    3010005, 3010006, 3010007, 3010008, 3010009,
    3010010, 3010011, 3010012, 3010013, 3010015,
    3010016, 3010017, 3010018, 3010019, 3010022,
    3010023, 3010024, 3010025, 3010026, 3010028,
    3010040, 3010041, 3010043, 3010045, 3010046,
    3010047, 3010057, 3010058, 3010060, 3010061
];

// Classic Maple weapons only. These are leveling/collection pieces rather than
// endgame equipment, and the meso component keeps Leaves as a sink rather than
// a free gear faucet.
var mapleWeapons = [
    1302020, 1302030, 1302032, 1302039,
    1312032, 1322025, 1322045,
    1332025, 1332055,
    1372031, 1372034,
    1382009, 1382012,
    1402039, 1412011, 1412027,
    1422014, 1422029,
    1432012, 1432040,
    1442024, 1442051,
    1452022, 1452045,
    1462019, 1462040,
    1472032, 1472055,
    1482021, 1492021
];

function start() {
    action(1, 0, 0);
}

function action(mode, type, sel) {
    if (mode != 1) {
        cm.dispose();
        return;
    }

    status++;

    if (status == 0) {
        var leaves = cm.getItemQuantity(MAPLE_LEAF);
        cm.sendSimple(
            "#eEverLeaf Maple Leaf Exchange#n\r\n" +
            "You have #r" + leaves + " Maple Leaves#k.\r\n\r\n" +
            "Leaves are earned through normal play and are meant for convenience, cosmetics, and leveling support.\r\n" +
            "#b#L0#1 AP Reset - " + AP_RESET_LEAVES + " Leaves#l" +
            "\r\n#L1#" + CHARM_QTY + " Safety Charms - " + CHARM_LEAVES + " Leaves#l" +
            "\r\n#L2#Random cosmetic chair - " + CHAIR_LEAVES + " Leaves#l" +
            "\r\n#L3#" + MERCHANT_DAYS + "-day Hired Merchant - " + MERCHANT_LEAVES + " Leaves + " + cm.numberWithCommas(MERCHANT_MESO) + " mesos#l" +
            "\r\n#L4#Random classic Maple weapon - " + MAPLE_WEAPON_LEAVES + " Leaves + " + cm.numberWithCommas(MAPLE_WEAPON_MESO) + " mesos#l#k" +
            "\r\n\r\n#dChaos Scrolls, White Scrolls, NX, and endgame gear are intentionally not sold here.#k"
        );
        return;
    }

    if (status == 1) {
        selection = sel;
        if (selection == 0) {
            cm.sendYesNo("Exchange #r" + AP_RESET_LEAVES + " Maple Leaves#k for #b1 #t" + AP_RESET + "##k?");
        } else if (selection == 1) {
            cm.sendYesNo("Exchange #r" + CHARM_LEAVES + " Maple Leaves#k for #b" + CHARM_QTY + " #t" + SAFETY_CHARM + "##k?");
        } else if (selection == 2) {
            cm.sendYesNo("Exchange #r" + CHAIR_LEAVES + " Maple Leaves#k for #bone random cosmetic chair#k?");
        } else if (selection == 3) {
            cm.sendYesNo("Exchange #r" + MERCHANT_LEAVES + " Maple Leaves#k and #r" + cm.numberWithCommas(MERCHANT_MESO) + " mesos#k for a #b" + MERCHANT_DAYS + "-day #t" + HIRED_MERCHANT + "##k?");
        } else if (selection == 4) {
            cm.sendYesNo("Exchange #r" + MAPLE_WEAPON_LEAVES + " Maple Leaves#k and #r" + cm.numberWithCommas(MAPLE_WEAPON_MESO) + " mesos#k for #bone random classic Maple weapon#k?");
        } else {
            cm.dispose();
        }
        return;
    }

    if (status == 2) {
        completeExchange(selection);
        return;
    }

    cm.dispose();
}

function completeExchange(choice) {
    if (choice == 0) {
        grantInventoryReward(AP_RESET_LEAVES, 0, AP_RESET, 1, "AP Reset");
        return;
    }

    if (choice == 1) {
        grantInventoryReward(CHARM_LEAVES, 0, SAFETY_CHARM, CHARM_QTY, CHARM_QTY + " Safety Charms");
        return;
    }

    if (choice == 2) {
        var chair = chairs[Math.floor(Math.random() * chairs.length)];
        grantInventoryReward(CHAIR_LEAVES, 0, chair, 1, "cosmetic chair #" + chair);
        return;
    }

    if (choice == 3) {
        if (cm.haveItem(HIRED_MERCHANT, 1)) {
            cm.sendOk("You already have a Hired Merchant. Use or remove it before purchasing another one.");
            cm.dispose();
            return;
        }
        if (!checkCost(MERCHANT_LEAVES, MERCHANT_MESO)) return;
        if (!cm.canHold(HIRED_MERCHANT, 1)) {
            cm.sendOk("Please make room in your Cash inventory first.");
            cm.dispose();
            return;
        }
        payCost(MERCHANT_LEAVES, MERCHANT_MESO);
        cm.gainItem(HIRED_MERCHANT, 1, false, true, 1000 * 60 * 60 * 24 * MERCHANT_DAYS);
        success(MERCHANT_LEAVES, MERCHANT_MESO, MERCHANT_DAYS + "-day Hired Merchant");
        return;
    }

    if (choice == 4) {
        var weapon = mapleWeapons[Math.floor(Math.random() * mapleWeapons.length)];
        grantInventoryReward(MAPLE_WEAPON_LEAVES, MAPLE_WEAPON_MESO, weapon, 1, "classic Maple weapon #" + weapon);
        return;
    }

    cm.dispose();
}

function grantInventoryReward(leaves, mesos, itemId, qty, description) {
    if (!checkCost(leaves, mesos)) return;
    if (!cm.canHold(itemId, qty)) {
        cm.sendOk("Please make enough room in the appropriate inventory first.");
        cm.dispose();
        return;
    }

    payCost(leaves, mesos);
    cm.gainItem(itemId, qty, true);
    success(leaves, mesos, description);
}

function checkCost(leaves, mesos) {
    if (!cm.haveItem(MAPLE_LEAF, leaves)) {
        cm.sendOk("You need #r" + leaves + " Maple Leaves#k for that exchange. You currently have #b" + cm.getItemQuantity(MAPLE_LEAF) + "#k.");
        cm.dispose();
        return false;
    }
    if (mesos > 0 && cm.getMeso() < mesos) {
        cm.sendOk("You also need #r" + cm.numberWithCommas(mesos) + " mesos#k for that exchange.");
        cm.dispose();
        return false;
    }
    return true;
}

function payCost(leaves, mesos) {
    cm.gainItem(MAPLE_LEAF, -leaves);
    if (mesos > 0) cm.gainMeso(-mesos);
}

function success(leaves, mesos, description) {
    var msg = "Exchange complete.\r\n\r\n#r-" + leaves + " Maple Leaves#k";
    if (mesos > 0) msg += "\r\n#r-" + cm.numberWithCommas(mesos) + " mesos#k";
    msg += "\r\n#b+" + description + "#k";
    msg += "\r\n\r\nRemaining Maple Leaves: #e" + cm.getItemQuantity(MAPLE_LEAF) + "#n";
    cm.sendOk(msg);
    cm.dispose();
}
