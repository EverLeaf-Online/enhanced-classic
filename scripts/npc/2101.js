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
var route = "";

var MAP_MUSHROOM_TOWN = 10000;
var MAP_EVAN_START = 100030100; // Utah's House - Small Attic
var MAP_NORMAL_TRAINING_EXIT = 40000;
var BEGINNERS_GUIDE = 4161001;
var EVAN_BEGINNER_JOB = 2001;

function isFreshBeginner() {
    return cm.getPlayer().getMapId() == MAP_MUSHROOM_TOWN
        && cm.getJobId() == 0
        && cm.getPlayer().getLevel() == 1
        && cm.getPlayer().getExp() == 0;
}

function finishEvanConversion() {
    cm.changeJobById(EVAN_BEGINNER_JOB);
    cm.warp(MAP_EVAN_START, 0);

    try {
        var guideCount = cm.itemQuantity(BEGINNERS_GUIDE);
        if (guideCount > 0) {
            cm.gainItem(BEGINNERS_GUIDE, -guideCount);
        }
    } catch (cleanupError) {
        // Non-critical cleanup must not strand a converted Evan on Maple Island.
    }

    try {
        cm.getPlayer().saveCharToDB(false);
    } catch (saveError) {
        // Normal autosave/logout persistence remains as a fallback.
    }

    cm.dispose();
}

function start() {
    if (isFreshBeginner()) {
        route = "menu";
        cm.sendSimple(
            "Before you leave the training camp, there is another path open to you.\r\n\r\n"
            + "#L0##bBegin your journey as an Evan (Dragon Master).#k#l\r\n"
            + "#L1#Leave the training camp as a normal Beginner.#l\r\n"
            + "#L2#Stay here for now.#l"
        );
    } else {
        route = "leave";
        cm.sendYesNo("Are you done with your training? If you wish, I will send you out from this training camp.");
    }
}

function action(mode, type, selection) {
    if (mode == -1) {
        cm.dispose();
        return;
    }

    status++;

    if (route == "menu") {
        if (mode != 1) {
            cm.dispose();
            return;
        }

        if (selection == 0) {
            route = "evan";
            cm.sendYesNo(
                "You will become an #bEvan#k and begin the Dragon Master story at Utah's House. "
                + "This choice is permanent for this character.\r\n\r\n"
                + "Do you want to begin your Evan journey?"
            );
            return;
        }

        if (selection == 1) {
            route = "leave";
            cm.sendYesNo("Leave the training camp as a normal Beginner?");
            return;
        }

        cm.sendOk("Take your time. Speak with me again when you have decided which path to follow.");
        cm.dispose();
        return;
    }

    if (route == "evan") {
        if (mode != 1) {
            cm.sendOk("No problem. Your character has not been changed.");
            cm.dispose();
            return;
        }

        if (!isFreshBeginner()) {
            cm.sendOk("Only a brand-new Level 1 Beginner with no EXP can choose the Evan path here.");
            cm.dispose();
            return;
        }

        finishEvanConversion();
        return;
    }

    if (route == "leave") {
        if (mode != 1) {
            cm.sendOk("Haven't you finished the training program yet? If you want to leave this place, please do not hesitate to tell me.");
            cm.dispose();
            return;
        }

        route = "leaveWarp";
        cm.sendNext("Then, I will send you out from here. Good job.");
        return;
    }

    if (route == "leaveWarp") {
        if (mode == 1) {
            cm.warp(MAP_NORMAL_TRAINING_EXIT, 0);
        }
        cm.dispose();
    }
}
