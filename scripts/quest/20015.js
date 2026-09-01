/*
 * Greetings From the Young Empress (20015)
 * Required Noblesse tutorial bridge between the early Ereve training quests
 * and Neinheart's Black Mage explanation (20016).
 */

var status = -1;

function start(mode, type, selection) {
    if (mode == -1) {
        qm.dispose();
        return;
    }

    if (mode == 0) {
        if (status <= 0) {
            qm.dispose();
            return;
        }
        status--;
    } else {
        status++;
    }

    if (status == 0) {
        qm.sendNext("Welcome, #h0#. Thank you for answering the call to become one of my Knights. I am still young, but with courageous people like you beside me, I believe we can protect Maple World.");
    } else if (status == 1) {
        qm.sendNextPrev("Please stay with us and grow into a dependable Knight. My tactician, #p1101002#, will explain our situation and help guide your training.");
    } else if (status == 2) {
        qm.forceStartQuest();
        qm.forceCompleteQuest();
        qm.sendPrev("Go speak with #p1101002# now. He can be stern, but everything he asks of you is meant to prepare you for what lies ahead.");
    } else {
        qm.dispose();
    }
}
