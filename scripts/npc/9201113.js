/*
	This file is part of the OdinMS Maple Story Server
*/
/* Jack - Crimsonwood Keep Party Quest */

var status = 0;
var expedition;
var expedMembers;
var player;
var em;
const ExpeditionType = Java.type('server.expeditions.ExpeditionType');
var cwkpq = ExpeditionType.CWKPQ;
var list = "What would you like to do?#b\r\n\r\n#L1#View current Expedition members#l\r\n#L2#Start the party quest!#l\r\n#L3#Stop the expedition.#l";

function start() {
    action(1, 0, 0);
}

function action(mode, type, selection) {
    player = cm.getPlayer();
    expedition = cm.getExpedition(cwkpq);
    em = cm.getEventManager("CWKPQ");

    if (mode == -1 || mode == 0) {
        cm.dispose();
        return;
    }

    if (status == 0) {
        if (player.getLevel() < cwkpq.getMinLevel() || player.getLevel() > cwkpq.getMaxLevel()) {
            cm.sendOk("You cannot enter Crimsonwood Keep Party Quest at your current level.\r\n\r\nRequired: #bLv. " + cwkpq.getMinLevel() + " - " + cwkpq.getMaxLevel() + "#k\r\nYour level: #rLv. " + player.getLevel() + "#k");
            cm.dispose();
        } else if (em == null) {
            cm.sendOk("Crimsonwood Keep Party Quest is temporarily unavailable. Please report this in EverLeaf's bug-report channel.");
            cm.dispose();
        } else if (expedition == null) {
            cm.sendSimple("#e#b<Party Quest: Crimsonwood Keep>\r\n#k#n" + em.getProperty("party") + "\r\n\r\nWould you like to assemble a team?\r\n#b#L1#Create the expedition.#l\r\n#L2#Not yet.#l");
            status = 1;
        } else if (expedition.isLeader(player)) {
            if (expedition.isInProgress()) {
                cm.sendOk("Your Crimsonwood Keep expedition is already in progress in this channel.");
                cm.dispose();
            } else {
                cm.sendSimple(list);
                status = 2;
            }
        } else if (expedition.isRegistering()) {
            if (expedition.contains(player)) {
                cm.sendOk("You are already registered. Expedition leader: #b" + expedition.getLeader().getName() + "#k. Wait for the leader to begin the party quest.");
                cm.dispose();
            } else {
                cm.sendOk(expedition.addMember(player));
                cm.dispose();
            }
        } else if (expedition.isInProgress()) {
            if (expedition.contains(player)) {
                var eim = em.getInstance("CWKPQ" + player.getClient().getChannel());
                if (eim == null) {
                    cm.sendOk("The active Crimsonwood Keep instance could not be loaded. Please report this in EverLeaf's bug-report channel.");
                } else {
                    eim.registerPlayer(player);
                }
                cm.dispose();
            } else {
                cm.sendOk("Another expedition is already running Crimsonwood Keep Party Quest in this channel. Try another channel or wait for the current run to finish.");
                cm.dispose();
            }
        }
    } else if (status == 1) {
        if (selection == 1) {
            expedition = cm.getExpedition(cwkpq);
            if (expedition != null) {
                cm.sendOk("An expedition is already being organized in this channel. You can join that group instead.");
                cm.dispose();
                return;
            }

            var res = cm.createExpedition(cwkpq);
            if (res == 0) {
                cm.sendOk("The #rCrimsonwood Keep Party Quest Expedition#k has been created. Talk to me again when your team is ready.");
            } else if (res > 0) {
                cm.sendOk("You have reached the entry-attempt limit for Crimsonwood Keep Party Quest. Try again after the attempt limit resets.");
            } else {
                cm.sendOk("The expedition could not be created because of an unexpected server error. Please try again, and report it if the problem continues.");
            }
            cm.dispose();
        } else if (selection == 2) {
            cm.dispose();
        }
    } else if (status == 2) {
        if (selection == 1) {
            if (expedition == null) {
                cm.sendOk("The expedition could not be loaded. Please talk to me again.");
                cm.dispose();
                return;
            }

            expedMembers = expedition.getMemberList();
            var size = expedMembers.size();
            if (size == 1) {
                cm.sendOk("You are currently the only registered member.");
                cm.dispose();
                return;
            }

            var text = "Registered expedition members (select a member to remove them):\r\n";
            text += "\r\n\t\t1. " + expedition.getLeader().getName();
            for (var i = 1; i < size; i++) {
                text += "\r\n#b#L" + (i + 1) + "#" + (i + 1) + ". " + expedMembers.get(i).getValue() + "#l\n";
            }
            cm.sendSimple(text);
            status = 6;
        } else if (selection == 2) {
            var min = cwkpq.getMinSize();
            var size = expedition.getMemberList().size();
            if (size < min) {
                cm.sendOk("Your expedition does not have enough registered players.\r\n\r\nRequired: #b" + min + "#k\r\nCurrently registered: #r" + size + "#k");
                cm.dispose();
                return;
            }

            cm.sendOk("Your expedition is ready. You will now be escorted to the #bCrimsonwood Keep altar entrance#k.");
            status = 4;
        } else if (selection == 3) {
            const PacketCreator = Java.type('tools.PacketCreator');
            player.getMap().broadcastMessage(PacketCreator.serverNotice(6, expedition.getLeader().getName() + " has ended the expedition."));
            cm.endExpedition(expedition);
            cm.sendOk("The expedition has been ended.");
            cm.dispose();
        }
    } else if (status == 4) {
        if (em == null) {
            cm.sendOk("Crimsonwood Keep Party Quest could not be initialized. Please report this in EverLeaf's bug-report channel.");
            cm.dispose();
            return;
        }

        em.setProperty("leader", player.getName());
        em.setProperty("channel", player.getClient().getChannel());
        if (!em.startInstance(expedition)) {
            cm.sendOk("A Crimsonwood Keep Party Quest run is already active in this channel. Try another channel or wait for the current run to finish.");
            cm.dispose();
            return;
        }

        cm.dispose();
    } else if (status == 6) {
        if (selection > 0) {
            var banned = expedMembers.get(selection - 1);
            expedition.ban(banned);
            cm.sendOk(banned.getValue() + " has been removed from the expedition.");
            cm.dispose();
        } else {
            cm.sendSimple(list);
            status = 2;
        }
    }
}
