/*
	This file is part of the OdinMS Maple Story Server
    Copyright (C) 2008 Patrick Huy <patrick.huy@frz.cc>
		       Matthias Butz <matze@odinms.de>
		       Jan Christian Meyer <vimes@odinms.de>

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License version 3
    as published by the Free Software Foundation. You may not use, modify
    or distribute this program under any other version of the
    GNU Affero General Public License.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */

/* @author RonanLana */

function enter(pi) {
    if (!((pi.isQuestStarted(6361) && pi.haveItem(4031870, 1)) || (pi.isQuestCompleted(6361) && !pi.isQuestCompleted(6363)))) {
        var em = pi.getEventManager("PapulatusBattle");

        if (em == null) {
            pi.playerMessage(5, "Papulatus is temporarily unavailable because the event could not be loaded. Please report this in EverLeaf's bug-report channel.");
            return false;
        }

        if (pi.getParty() == null) {
            pi.playerMessage(5, "Papulatus requires a party. Create or join a party, then have the party leader enter this portal.");
            return false;
        } else if (!pi.isLeader()) {
            pi.playerMessage(5, "Only your party leader can start the Papulatus battle. Ask the leader to enter this portal first.");
            return false;
        } else {
            var eli = em.getEligibleParty(pi.getParty());
            if (eli.size() > 0) {
                if (!em.startInstance(pi.getParty(), pi.getPlayer().getMap(), 1)) {
                    pi.playerMessage(5, "A Papulatus battle is already active on this channel. Try another channel or wait for the current battle to finish.");
                    return false;
                }
            } else {
                pi.playerMessage(5, "Your party is not eligible to enter Papulatus right now. Make sure all required party members are present on this map and meet the battle requirements.");
                return false;
            }

            pi.playPortalSound();
            return true;
        }
    } else {
        pi.playPortalSound();
        pi.warp(922020300, 0);
        return true;
    }
}
