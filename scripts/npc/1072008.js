/**
 Author: xQuasar
 NPC: Kyrin - Pirate Job Advancer
 Inside Test Room
 **/

var status;

function start() {
    status = -1;
    action(1, 0, 0);
}

function action(mode, type, selection) {
    if (mode == -1) {
        cm.dispose();
    } else {
        if (mode == 0 && type > 0) {
            cm.dispose();
            return;
        }
        if (mode == 1) {
            status++;
        } else {
            status--;
        }

        if (status == 0) {
            if (cm.getMapId() == 108000502) {
                if (!cm.haveItem(4031856, 15)) {
                    cm.sendSimple("You still need #b15 #t4031856##k to complete this job advancement test.\r\n\r\n#b#L1#Leave the test room.#l");
                } else {
                    status++;
                    cm.sendNext("You collected all #b15 #t4031856##k. The test is complete, and I'll return you to Kyrin.");
                }
            } else if (cm.getMapId() == 108000501) {
                if (!cm.haveItem(4031857, 15)) {
                    cm.sendSimple("You still need #b15 #t4031857##k to complete this job advancement test.\r\n\r\n#b#L1#Leave the test room.#l");
                } else {
                    status++;
                    cm.sendNext("You collected all #b15 #t4031857##k. The test is complete, and I'll return you to Kyrin.");
                }
            } else {
                cm.sendOk("This job advancement NPC was opened from an unexpected map. Use #b@unstuck#k if you are trapped, and please report the map in EverLeaf's bug-report channel.");
                cm.dispose();
            }
        } else if (status == 1) {   // thanks Lame for noticing players getting stuck in area in certain scenarios
            cm.removeAll(4031856);
            cm.removeAll(4031857);
            cm.warp(120000101, 0);
            cm.dispose();
        } else if (status == 2) {
            cm.warp(120000101, 0);
            cm.dispose();
        }
    }
}
