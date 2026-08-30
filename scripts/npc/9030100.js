/*
 * EverLeaf Free Market Utility Hub
 * Uses the existing storage NPC in the Free Market entrance so players
 * get useful services without adding extra map clutter.
 */

var status = -1;

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
            "\r\n#L2#Instant Travel"
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
            // Reuse an existing general-store inventory rather than creating
            // a progression-bypassing remote shop.
            cm.openShopNPC(2100002);
            cm.dispose();
            return;
        }

        if (selection == 2) {
            cm.dispose();
            cm.openNpc(9000020);
            return;
        }
    }

    cm.dispose();
}
