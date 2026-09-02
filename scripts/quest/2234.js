/*
 * Captain Al's Passing of Knowledge - Enjoy the Entitlement! (2234)
 * Complete after total Family Rep reaches 2,000 and current Rep is 500 or less.
 */

function end(mode, type, selection) {
    var familyEntry = qm.getPlayer().getFamilyEntry();

    if (familyEntry == null) {
        qm.sendNext("You need to be part of a Family before you can complete this lesson.");
        qm.dispose();
        return;
    }

    var currentRep = familyEntry.getReputation();
    var totalRep = familyEntry.getTotalReputation();

    if (totalRep < 2000 || currentRep > 500) {
        qm.sendNext("The final mission isn't complete yet. Build your total Rep to at least 2,000, then use an Entitlement until your current Rep is 500 or less. Your current Rep is " + currentRep + " and your total Rep is " + totalRep + ".");
        qm.dispose();
        return;
    }

    qm.gainExp(3000);
    qm.forceCompleteQuest();
    qm.sendNext("Well done. You've built at least 2,000 total Rep and used your Entitlement wisely. You've completed my Family lessons.");
    qm.dispose();
}
