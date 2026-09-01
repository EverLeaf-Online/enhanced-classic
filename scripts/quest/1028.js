/*
 * For a New World - To Lith Harbor! (1028)
 * Shanks has already been contacted by Lucas, so this quest path boards for
 * free, starts the quest, and sends the Beginner to Victoria Island.
 */

var status = -1;

function start(mode, type, selection) {
    if (mode == -1) {
        qm.dispose();
        return;
    }

    if (mode == 0) {
        if (status <= 0) {
            qm.sendNext("Still have something to do on Maple Island? Come back when you're ready to leave for Victoria Island.");
            qm.dispose();
            return;
        }
        status--;
    } else {
        status++;
    }

    if (status == 0) {
        qm.sendYesNo("Lucas told me you'd be coming. Since you're carrying his message, I'll take you to Victoria Island for free. Once we leave Maple Island, you won't be able to come back. Are you ready?");
    } else if (status == 1) {
        qm.forceStartQuest();
        qm.warp(104000000, 0);
        qm.dispose();
    }
}
