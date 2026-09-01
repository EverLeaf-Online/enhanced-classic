var status = -1;
var route = "";

var MAP_MUSHROOM_TOWN = 10000;
var MAP_LITH_HARBOR = 104000000;
var BEGINNERS_GUIDE = 4161001;
var EVAN_BEGINNER_JOB = 2001;

function isFreshBeginner() {
    return cm.getPlayer().getMapId() == MAP_MUSHROOM_TOWN
        && cm.getJobId() == 0
        && cm.getPlayer().getLevel() == 1
        && cm.getPlayer().getExp() == 0;
}

function finishEvanConversion() {
    // Safety: do NOT warp into the imported v84 Evan maps until they are proven
    // compatible with the v83 client. A bad destination previously trapped the
    // character in a crash-on-login loop. Convert in-place on Mushroom Town.
    cm.changeJobById(EVAN_BEGINNER_JOB);

    try {
        var guideCount = cm.itemQuantity(BEGINNERS_GUIDE);
        if (guideCount > 0) cm.gainItem(BEGINNERS_GUIDE, -guideCount);
    } catch (cleanupError) { }
    try { cm.getPlayer().saveCharToDB(false); } catch (saveError) { }

    cm.sendOk("You are now an #bEvan#k. EverLeaf is temporarily keeping new Evans on Maple Island while the original Evan starter maps are being made v83-safe. Your character will not be sent into the unstable map data.");
    cm.dispose();
}

function start() {
    status = -1;
    if (isFreshBeginner()) {
        route = "fresh";
        cm.sendSimple(
            "Welcome to EverLeaf. Before you continue, choose how you want this character to begin.\r\n\r\n"
            + "#L0##bBegin as an Evan (Dragon Master).#k#l\r\n"
            + "#L1#Skip Maple Island and go to Lith Harbor.#l\r\n"
            + "#L2#Stay on Maple Island and continue the normal tutorial.#l"
        );
        return;
    }
    route = "skip";
    cm.sendYesNo("Would you like to skip the tutorials and head straight to Lith Harbor?");
}

function action(mode, type, selection) {
    if (mode == -1) { cm.dispose(); return; }
    status++;

    if (route == "fresh") {
        if (mode != 1) { cm.dispose(); return; }
        if (selection == 0) {
            route = "evanConfirm";
            cm.sendYesNo(
                "You will become an #bEvan#k. For safety, you will remain on Maple Island until the Evan starter-map backport is fully v83-compatible. "
                + "This choice is permanent for this character.\r\n\r\n"
                + "Become an Evan now?"
            );
            return;
        }
        if (selection == 1) { cm.warp(MAP_LITH_HARBOR, 0); cm.dispose(); return; }
        cm.sendOk("Enjoy the Maple Island tutorial.");
        cm.dispose();
        return;
    }

    if (route == "evanConfirm") {
        if (mode != 1) { cm.sendOk("No changes were made to your character."); cm.dispose(); return; }
        if (!isFreshBeginner()) { cm.sendOk("Only a brand-new Level 1 Beginner with no EXP can choose the Evan path here."); cm.dispose(); return; }
        finishEvanConversion();
        return;
    }

    if (route == "skip") {
        if (mode == 1) cm.warp(MAP_LITH_HARBOR, 0);
        cm.dispose();
    }
}
