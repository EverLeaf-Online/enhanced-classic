/*
	NPC: Blocked Entrance (portal?)
	MAP: Mushroom Castle - East Castle Tower (106021400)
*/

var status;

function start() {
    status = -1;
    action(1, 0, 0);
}

function action(mode, type, selection) {
    if (mode == -1) {
        cm.dispose();
        return;
    } else if (mode == 0 && status == 0) {
        cm.dispose();
        return;
    } else if (mode == 0) {
        status--;
    } else {
        status++;
    }

    if (cm.getMapId() == 106021402) {
        if (!cm.isQuestCompleted(2331)) {
            cm.sendOk("You cannot use this entrance yet. Continue the Mushroom Kingdom questline first.");
            cm.dispose();
            return;
        }

        if (status == 0) {
            cm.sendSimple("#L0#Enter to fight #bKing Pepe#k and #bYeti Brothers#k.#l\r\n#L1#Enter to fight #bPrime Minister#k.#l");
        } else if (status == 1) {
            if (selection == 0) {
                var pepe = cm.getEventManager("KingPepeAndYetis");
                if (pepe == null) {
                    cm.sendOk("The King Pepe battle is temporarily unavailable. Please report this in EverLeaf's bug-report channel.");
                    cm.dispose();
                    return;
                }

                pepe.setProperty("player", cm.getPlayer().getName());
                if (!pepe.startInstance(cm.getPlayer())) {
                    cm.sendOk("King Pepe is already being challenged in this channel. Try another channel or wait for the current battle to finish.");
                }
                cm.dispose();

            } else if (selection == 1) {
                var em = cm.getEventManager("MK_PrimeMinister2");
                if (em == null) {
                    cm.sendOk("The Prime Minister battle is temporarily unavailable. Please report this in EverLeaf's bug-report channel.");
                    cm.dispose();
                    return;
                }

                var party = cm.getPlayer().getParty();
                if (party != null) {
                    var eligible = em.getEligibleParty(party);
                    if (eligible.size() <= 0) {
                        cm.sendOk("Your party is not eligible to enter. Make sure all required members are present on this map and meet the battle requirements.");
                        cm.dispose();
                        return;
                    }

                    if (!em.startInstance(party, cm.getMap(), 1)) {
                        cm.sendOk("Another party is already challenging the Prime Minister in this channel. Try another channel or wait for the current battle to finish.");
                    }
                } else {
                    if (!em.startInstance(cm.getPlayer())) {
                        cm.sendOk("The Prime Minister is already being challenged in this channel. Try another channel or wait for the current battle to finish.");
                    }
                }

                cm.dispose();
            }
        }
    } else {
        var questProgress = cm.getQuestProgressInt(2330, 3300005) + cm.getQuestProgressInt(2330, 3300006) + cm.getQuestProgressInt(2330, 3300007); //3 Yetis
        if (!(cm.isQuestStarted(2330) && questProgress < 3)) {
            cm.sendOk("This entrance is only available during the required Mushroom Kingdom quest objective.");
            cm.dispose();
            return;
        }

        if (status == 0) {
            cm.sendSimple("#L1#Enter to fight #bKing Pepe#k and #bYeti Brothers#k.#l");
        } else if (status == 1 && selection == 1) {
            var pepe = cm.getEventManager("KingPepeAndYetis");
            if (pepe == null) {
                cm.sendOk("The King Pepe battle is temporarily unavailable. Please report this in EverLeaf's bug-report channel.");
                cm.dispose();
                return;
            }

            pepe.setProperty("player", cm.getPlayer().getName());
            if (!pepe.startInstance(cm.getPlayer())) {
                cm.sendOk("King Pepe is already being challenged in this channel. Try another channel or wait for the current battle to finish.");
            }
            cm.dispose();
        }
    }
}
