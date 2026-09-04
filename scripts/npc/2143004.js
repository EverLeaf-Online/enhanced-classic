/* Another Informant - Cygnus Garden expedition recruiter */

var status = 0;
var expedition;
var expedMembers;
var player;
var em;
const ExpeditionType = Java.type('server.expeditions.ExpeditionType');
const EmpressContentPolicy = Java.type('everleaf.content.EmpressContentPolicy');
const EmpressWeeklyLockoutService = Java.type('everleaf.content.EmpressWeeklyLockoutService');
var exped = ExpeditionType.EMPRESS;
var expedMap = "Cygnus's Chamber";

var list = "What would you like to do?#b\r\n\r\n#L1#View current Expedition members#l\r\n#L2#Start the fight!#l\r\n#L3#Stop the expedition.#l";

function start() {
    action(1, 0, 0);
}

function action(mode, type, selection) {
    player = cm.getPlayer();

    if (!EmpressContentPolicy.isEnabled()) {
        cm.sendOk(EmpressContentPolicy.disabledMessage());
        cm.dispose();
        return;
    }

    // Every character must talk to the recruiter to create/join the expedition,
    // so the account-scoped weekly check is enforced before registration.
    if (!EmpressWeeklyLockoutService.canEnter(player.getAccountID())) {
        cm.sendOk("Your account has already cleared the Empress expedition this week. EverLeaf weekly lockouts reset Monday at 00:00 UTC.");
        cm.dispose();
        return;
    }

    expedition = cm.getExpedition(exped);
    em = cm.getEventManager("EmpressBattle");

    if (mode == -1 || mode == 0) {
        cm.dispose();
        return;
    }

    if (status == 0) {
        if (player.getLevel() < exped.getMinLevel() || player.getLevel() > exped.getMaxLevel()) {
            cm.sendOk("You cannot enter the Empress expedition at your current level.\r\n\r\n#bRequired Level: " + exped.getMinLevel() + " - " + exped.getMaxLevel() + "#k\r\nYour Level: " + player.getLevel());
            cm.dispose();
        } else if (em == null) {
            cm.sendOk("The Empress battle event is unavailable. Please report this in EverLeaf's bug-report channel.");
            cm.dispose();
        } else if (expedition == null) {
            cm.sendSimple("#e#b<Expedition: Empress Cygnus>\r\n#k#n" + em.getProperty("party") + "\r\n\r\nThis is EverLeaf's level-180 Gate to the Future encounter.\r\n#b#L1#Create an expedition.#l\r\n#L2#Not yet.#l");
            status = 1;
        } else if (expedition.isLeader(player)) {
            if (expedition.isInProgress()) {
                cm.sendOk("Your Empress expedition is already in progress.");
                cm.dispose();
            } else {
                cm.sendSimple(list);
                status = 2;
            }
        } else if (expedition.isRegistering()) {
            if (expedition.contains(player)) {
                cm.sendOk("You are already registered. Please wait for the expedition leader to start the battle.");
                cm.dispose();
            } else {
                cm.sendOk(expedition.addMember(player));
                cm.dispose();
            }
        } else {
            cm.sendOk("An Empress expedition is already in progress on this channel.");
            cm.dispose();
        }
    } else if (status == 1) {
        if (selection == 1) {
            var res = cm.createExpedition(exped);
            if (res == 0) {
                cm.sendOk("The #rEmpress Expedition#k has been created. Talk to me again to manage the team and begin the fight.");
            } else if (res > 0) {
                cm.sendOk("You have reached the current expedition entry limit.");
            } else {
                cm.sendOk("The Empress expedition could not be created. Please try again.");
            }
        } else {
            cm.sendOk("Come back when you're ready to challenge Cygnus.");
        }
        cm.dispose();
    } else if (status == 2) {
        if (selection == 1) {
            expedMembers = expedition.getMemberList();
            var size = expedMembers.size();
            var text = "Current expedition members:\r\n\r\n1. " + expedition.getLeader().getName();
            for (var i = 1; i < size; i++) {
                text += "\r\n#b#L" + (i + 1) + "#" + (i + 1) + ". " + expedMembers.get(i).getValue() + "#l";
            }
            cm.sendSimple(text);
            status = 6;
        } else if (selection == 2) {
            var min = exped.getMinSize();
            var size = expedition.getMemberList().size();
            if (size < min) {
                cm.sendOk("The expedition needs at least " + min + " registered players. Current members: " + size + ".");
                cm.dispose();
                return;
            }

            cm.sendOk("The expedition is ready. You will now enter #b" + expedMap + "#k.");
            status = 4;
        } else if (selection == 3) {
            cm.endExpedition(expedition);
            cm.sendOk("The expedition has been ended.");
            cm.dispose();
        }
    } else if (status == 4) {
        em.setProperty("leader", player.getName());
        em.setProperty("channel", player.getClient().getChannel());
        if (!em.startInstance(expedition)) {
            cm.sendOk("The Empress battle could not start because this channel already has an active instance.");
        }
        cm.dispose();
    } else if (status == 6) {
        if (selection > 0) {
            var banned = expedMembers.get(selection - 1);
            expedition.ban(banned);
            cm.sendOk("You have removed " + banned.getValue() + " from the expedition.");
        } else {
            cm.sendSimple(list);
            status = 2;
            return;
        }
        cm.dispose();
    }
}
