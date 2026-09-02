/*
 * Mushroom Castle barrier/vine investigation helper.
 *
 * NPC 1300014 is intentionally hidden on the relevant maps and is opened by
 * the investigate1/investigate2 scripted portals. This restores the retail
 * quest interaction without introducing any new warp or reward path.
 */
var status = -1;
var quest = 0;

function start() {
    action(1, 0, 0);
}

function action(mode, type, selection) {
    if (mode == -1) {
        cm.dispose();
        return;
    }
    if (mode == 0) {
        cm.dispose();
        return;
    }

    status++;

    if (status == 0) {
        if (cm.isQuestStarted(2314)) {
            quest = 2314;
            cm.sendNext("This is a powerful magical barrier. Mushroom spores have been converted into a strong form of magic, so brute force will not work. I should report this to the Minister of Home Affairs.");
        } else if (cm.isQuestStarted(2322)) {
            quest = 2322;
            cm.sendNext("The castle wall is completely tangled in thick vines. I cannot enter this way. I should report what I found before trying anything else.");
        } else {
            cm.sendOk("There is something unusual about this barrier. I should continue the Mushroom Kingdom investigation before trying to force my way through.");
            cm.dispose();
        }
        return;
    }

    if (status == 1) {
        if (quest == 2314 && cm.isQuestStarted(2314)) {
            cm.forceCompleteQuest(2314);
            cm.playerMessage(5, "Investigation complete. Return to the Minister of Home Affairs.");
        } else if (quest == 2322 && cm.isQuestStarted(2322)) {
            cm.playerMessage(5, "Return and report what you found at the castle wall.");
        }
        cm.dispose();
    }
}
