/*
 * Captain Al's Passing of Knowledge - Raise the Rep! (2233)
 * Complete after the player reaches 1,000 current Family Rep.
 */

function end(mode, type, selection) {
    var familyEntry = qm.getPlayer().getFamilyEntry();

    if (familyEntry == null) {
        qm.sendNext("You need to be part of a Family before you can build up Rep. Come back after you've established your Family.");
        qm.dispose();
        return;
    }

    if (familyEntry.getReputation() < 1000) {
        qm.sendNext("You haven't reached 1,000 Rep yet. Keep supporting your Juniors and come back when your current Rep reaches at least 1,000.");
        qm.dispose();
        return;
    }

    qm.gainExp(2400);
    qm.forceCompleteQuest();
    qm.sendNext("Excellent. You've reached 1,000 Rep and proven that you know how to support your Family. You're ready for the next lesson.");
    qm.dispose();
}
