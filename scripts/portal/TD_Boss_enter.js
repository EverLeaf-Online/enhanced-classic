/* @author RonanLana */

function enter(pi) {
    var stage = ((Math.floor(pi.getMapId() / 100)) % 10) - 1;
    var em = pi.getEventManager("TD_Battle" + stage);
    if (em == null) {
        pi.playerMessage(5, "This Temple of Time boss battle is temporarily unavailable because its event could not be loaded. Please report this in EverLeaf's bug-report channel.");
        return false;
    }

    if (pi.getParty() == null) {
        pi.playerMessage(5, "You need a party to start this boss battle.");
        return false;
    } else if (!pi.isLeader()) {
        pi.playerMessage(5, "Only your party leader can start this boss battle. Have the leader enter the portal first.");
        return false;
    } else {
        var eli = em.getEligibleParty(pi.getParty());
        if (eli.size() > 0) {
            if (!em.startInstance(pi.getParty(), pi.getPlayer().getMap(), 1)) {
                pi.playerMessage(5, "A boss battle is already active in this channel. Try another channel or wait for the current battle to finish.");
                return false;
            }
        } else {
            pi.playerMessage(5, "Your party is not currently eligible. You need at least 2 eligible party members together in this map before the leader enters.");
            return false;
        }

        pi.playPortalSound();
        return true;
    }
}
