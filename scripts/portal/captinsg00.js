/* @author RonanLana */

function enter(pi) {
    if (!pi.haveItem(4000381)) {
        pi.playerMessage(5, "You need a White Essence to challenge Captain Latanica.");
        return false;
    }

    var em = pi.getEventManager("LatanicaBattle");
    if (em == null) {
        pi.playerMessage(5, "Captain Latanica is temporarily unavailable because the battle event could not be loaded. Please report this in EverLeaf's bug-report channel.");
        return false;
    }

    if (pi.getParty() == null) {
        pi.playerMessage(5, "You need a party to challenge Captain Latanica.");
        return false;
    } else if (!pi.isLeader()) {
        pi.playerMessage(5, "Only your party leader can start the Captain Latanica battle. Have the leader enter the portal first.");
        return false;
    } else {
        var eli = em.getEligibleParty(pi.getParty());
        if (eli.size() > 0) {
            if (!em.startInstance(pi.getParty(), pi.getPlayer().getMap(), 1)) {
                pi.playerMessage(5, "Captain Latanica is already being challenged in this channel. Try another channel or wait for the current battle to finish.");
                return false;
            }
        } else {
            pi.playerMessage(5, "Your party is not currently eligible for Captain Latanica. Make sure the required party members are eligible and together in this map before the leader enters.");
            return false;
        }

        pi.playPortalSound();
        return true;
    }
}
