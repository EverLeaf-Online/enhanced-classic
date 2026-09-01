var status = -1;
var route = "";

var MAP_MUSHROOM_TOWN = 10000;
var MAP_LITH_HARBOR = 104000000;
var MAP_EVAN_START = 100030100; // Utah's House - Small Attic
var BEGINNERS_GUIDE = 4161001;
var EVAN_BEGINNER_JOB = 2001;

function isFreshBeginner() {
    return cm.getPlayer().getMapId() == MAP_MUSHROOM_TOWN
        && cm.getJobId() == 0
        && cm.getPlayer().getLevel() == 1
        && cm.getPlayer().getExp() == 0;
}

function finishEvanConversion() {
    // Keep the critical path minimal: once the job changes, move the player to
    // the native Evan start map immediately. Cleanup/save must never strand a
    // converted Evan on Maple Island if a secondary operation fails.
    cm.changeJobById(EVAN_BEGINNER_JOB);
    cm.warp(MAP_EVAN_START, 0);

    try {
        var guideCount = cm.itemQuantity(BEGINNERS_GUIDE);
        if (guideCount > 0) {
            cm.gainItem(BEGINNERS_GUIDE, -guideCount);
        }
    } catch (cleanupError) {
        // Non-critical cleanup. The character is already an Evan in the correct map.
    }

    try {
        cm.getPlayer().saveCharToDB(false);
    } catch (saveError) {
        // Normal channel autosave/logout persistence remains as a fallback.
    }

    cm.dispose();
}

function start() {
    status = -1;

    if (isFreshBeginner()) {
        route = "fresh";
        cm.sendSimple(
            "Welcome to EverLeaf. Before you continue, choose how you want this character to begin.\r\n\r\n"
            + "#L0##bBegin as an Evan (Dragon Master).#k#l\r\n"
            + "#L1#Skip the Maple Island tutorial and go to Lith Harbor.#l\r\n"
            + "#L2#Stay on Maple Island and continue the normal tutorial.#l"
        );
        return;
    }

    route = "skip";
    cm.sendYesNo("Would you like to skip the tutorials and head straight to Lith Harbor?");
}

function action(mode, type, selection) {
    if (mode == -1) {
        cm.dispose();
        return;
    }

    status++;

    if (route == "fresh") {
        if (mode != 1) {
            cm.dispose();
            return;
        }

        if (selection == 0) {
            route = "evanConfirm";
            cm.sendYesNo(
                "You will become an #bEvan#k and begin the Dragon Master story at Utah's House. "
                + "This choice is permanent for this character.\r\n\r\n"
                + "Begin your Evan journey now?"
            );
            return;
        }

        if (selection == 1) {
            cm.warp(MAP_LITH_HARBOR, 0);
            cm.dispose();
            return;
        }

        cm.sendOk("Enjoy the Maple Island tutorial. If you change your mind while you are still a fresh Level 1 Beginner with no EXP, speak with Heena before progressing.");
        cm.dispose();
        return;
    }

    if (route == "evanConfirm") {
        if (mode != 1) {
            cm.sendOk("No changes were made to your character.");
            cm.dispose();
            return;
        }

        if (!isFreshBeginner()) {
            cm.sendOk("Only a brand-new Level 1 Beginner with no EXP can choose the Evan path here.");
            cm.dispose();
            return;
        }

        finishEvanConversion();
        return;
    }

    if (route == "skip") {
        if (mode == 1) {
            cm.warp(MAP_LITH_HARBOR, 0);
        }
        cm.dispose();
    }
}
