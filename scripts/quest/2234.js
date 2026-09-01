/*
 * Captain Al's Passing of Knowledge - Enjoy the Entitlement! (2234)
 * QuestInfo requires total Rep >= 2,000 and current Rep < 500.
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

    if (totalRep < 2000 || currentRep >= 500) {
        qm.sendNext("The final mission isn't complete yet. Build your total Rep to at least 2,000, then use an Entitlement until your current Rep is below 500. Your current Rep is " + currentRep + " and your total Rep is " + totalRep + ".");
        qm.dispose();
        return;
    }

    qm.forceCompleteQuest();
    qm.sendNext("Well done. You've built more than 2,000 total Rep and used your Entitlement wisely. You've completed my Family lessons.");
    qm.dispose();
}
