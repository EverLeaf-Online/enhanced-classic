function enter(pi) {
    if (pi.isQuestCompleted(2331)) {
        pi.openNpc(1300013);
        return false;
    }

    if (pi.isQuestCompleted(2333) && pi.isQuestStarted(2331) && !pi.hasItem(4001318)) {
        pi.getPlayer().message("You've lost the Royal Seal. I'll replace it so you can continue the quest.");
        if (pi.canHold(4001318)) {
            pi.gainItem(4001318, 1);
        } else {
            pi.getPlayer().message("Your ETC inventory is full. Free a slot, then try again to receive the Royal Seal.");
            return false;
        }
    }

    if (pi.isQuestCompleted(2333)) {
        pi.playPortalSound();
        pi.warp(106021600, 1);
        return true;
    } else if (pi.isQuestStarted(2332) && pi.hasItem(4032388)) {
        pi.forceCompleteQuest(2332, 1300002);
        pi.getPlayer().message("You've found the princess!");
        pi.giveCharacterExp(4400, pi.getPlayer());

        return startPrimeMinisterBattle(pi);
    } else if (pi.isQuestStarted(2333) || (pi.isQuestCompleted(2332) && !pi.isQuestStarted(2333))) {
        return startPrimeMinisterBattle(pi);
    } else {
        pi.getPlayer().message("The door is locked. Continue the Mushroom Kingdom questline to gain access.");
        return false;
    }
}

function startPrimeMinisterBattle(pi) {
    var em = pi.getEventManager("MK_PrimeMinister");
    if (em == null) {
        pi.playerMessage(5, "The Prime Minister battle is temporarily unavailable. Please report this in EverLeaf's bug-report channel.");
        return false;
    }

    var party = pi.getPlayer().getParty();
    if (party != null) {
        var eligible = em.getEligibleParty(party);
        if (eligible.size() <= 0) {
            pi.playerMessage(5, "Your party is not eligible to enter. Make sure all required members are present on this map and meet the battle requirements.");
            return false;
        }

        if (em.startInstance(party, pi.getMap(), 1)) {
            pi.playPortalSound();
            return true;
        }
    } else {
        if (em.startInstance(pi.getPlayer())) {
            pi.playPortalSound();
            return true;
        }
    }

    pi.playerMessage(5, "Another party is already challenging the Prime Minister in this channel. Try another channel or wait for the current battle to finish.");
    return false;
}
