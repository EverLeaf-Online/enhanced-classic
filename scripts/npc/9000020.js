/*
	This file is part of the OdinMS Maple Story Server
    Copyright (C) 2008 Patrick Huy <patrick.huy@frz.cc>
		       Matthias Butz <matze@odinms.de>
		       Jan Christian Meyer <vimes@odinms.de>

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as
    published by the Free Software Foundation version 3 as published by
    the Free Software Foundation. You may not use, modify or distribute
    this program under any other version of the GNU Affero General Public
    License.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
*/

var status = -1;
var selectedDestination = -1;

// EverLeaf instant-travel hub. Keep this focused on safe towns/hubs so travel
// removes repetitive transit without bypassing bosses, instances, or progression.
var TRAVEL_FEE = 5000;
var destinations = [
    [100000000, "Henesys"],
    [101000000, "Ellinia"],
    [102000000, "Perion"],
    [103000000, "Kerning City"],
    [104000000, "Lith Harbor"],
    [120000000, "Nautilus Harbor"],
    [130000000, "Ereve"],
    [140000000, "Rien"],
    [200000000, "Orbis"],
    [211000000, "El Nath"],
    [220000000, "Ludibrium"],
    [230000000, "Aquarium"],
    [240000000, "Leafre"],
    [250000000, "Mu Lung"],
    [251000000, "Herb Town"],
    [260000000, "Ariant"],
    [261000000, "Magatia"],
    [800000000, "Mushroom Shrine"],
    [550000000, "Malaysia"],
    [600000000, "New Leaf City"]
];

function start() {
    action(1, 0, 0);
}

function action(mode, type, selection) {
    if (mode != 1) {
        cm.dispose();
        return;
    }

    status++;

    if (status == 0) {
        var text = "#eEverLeaf Instant Travel#n\r\n\r\n" +
            "Choose a major town or travel hub. Each trip costs #b" +
            cm.numberWithCommas(TRAVEL_FEE) + " mesos#k.\r\n\r\n";

        for (var i = 0; i < destinations.length; i++) {
            if (cm.getPlayer().getMapId() != destinations[i][0]) {
                text += "#L" + i + "##b" + destinations[i][1] + "#k#l\r\n";
            }
        }

        cm.sendSimple(text);
        return;
    }

    if (status == 1) {
        selectedDestination = selection;

        if (selectedDestination < 0 || selectedDestination >= destinations.length) {
            cm.sendOk("That destination is unavailable. Please reopen the travel menu and try again.");
            cm.dispose();
            return;
        }

        var destination = destinations[selectedDestination];
        if (cm.getPlayer().getMapId() == destination[0]) {
            cm.sendOk("You're already in #b" + destination[1] + "#k.");
            cm.dispose();
            return;
        }

        cm.sendYesNo("Travel to #b" + destination[1] + "#k for #b" +
            cm.numberWithCommas(TRAVEL_FEE) + " mesos#k?");
        return;
    }

    if (status == 2) {
        var destination = destinations[selectedDestination];

        if (cm.getMeso() < TRAVEL_FEE) {
            cm.sendOk("You need #b" + cm.numberWithCommas(TRAVEL_FEE) +
                " mesos#k to use EverLeaf Instant Travel.");
            cm.dispose();
            return;
        }

        cm.gainMeso(-TRAVEL_FEE);
        cm.warp(destination[0], 0);
        cm.dispose();
    }
}
