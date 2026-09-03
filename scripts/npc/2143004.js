/* Another Informant — Fallen Cygnus expedition controller. */
var status = 0;
var expedition, expedMembers, player, em;
const ExpeditionType = Java.type('server.expeditions.ExpeditionType');
const exped = ExpeditionType.CYGNUS;
var expedName = "Cygnus";
var expedBoss = "Fallen Cygnus";
var list = "What would you like to do?#b\r\n\r\n#L1#View current Expedition members#l\r\n#L2#Start the fight!#l\r\n#L3#Stop the expedition.#l";

function start() { action(1, 0, 0); }

function action(mode, type, selection) {
    player = cm.getPlayer();
    em = cm.getEventManager("CygnusBattle");

    if (player.getMapId() == 271040100) {
        if (mode <= 0) { cm.dispose(); return; }
        if (status == 0) { cm.sendYesNo("Leave the Fallen Cygnus chamber and return to the garden?"); status = 20; return; }
        if (status == 20) { cm.warp(271040000, 0); cm.dispose(); return; }
    }

    expedition = cm.getExpedition(exped);
    if (mode == -1 || mode == 0) { cm.dispose(); return; }

    if (status == 0) {
        if (em == null) { cm.sendOk("The Fallen Cygnus encounter is temporarily unavailable. Please contact a GM."); cm.dispose(); return; }
        if (player.getLevel() < exped.getMinLevel() || player.getLevel() > exped.getMaxLevel()) {
            cm.sendOk("You cannot enter the Fallen Cygnus expedition at your current level.\r\n\r\n#bRequired Level: " + exped.getMinLevel() + " - " + exped.getMaxLevel() + "#k");
            cm.dispose();
        } else if (expedition == null) {
            cm.sendSimple("#e#b<Expedition: Fallen Cygnus>\r\n#k#n" + em.getProperty("party") + "\r\n\r\nAssemble an expedition to confront the fallen Empress?\r\n#b#L1#Create the expedition.#l\r\n#L2#Not yet.#l");
            status = 1;
        } else if (expedition.isLeader(player)) {
            if (expedition.isInProgress()) { cm.sendOk("Your Fallen Cygnus expedition is already in progress."); cm.dispose(); }
            else { cm.sendSimple(list); status = 2; }
        } else if (expedition.isRegistering()) {
            if (expedition.contains(player)) cm.sendOk("You are already registered. Leader: #r" + expedition.getLeader().getName() + "#k");
            else cm.sendOk(expedition.addMember(player));
            cm.dispose();
        } else if (expedition.isInProgress()) {
            if (expedition.contains(player)) {
                var eim = em.getInstance(expedName + player.getClient().getChannel());
                if (eim != null && eim.getIntProperty("canJoin") == 1) eim.registerPlayer(player);
                else cm.sendOk("Late entry is closed for this Fallen Cygnus attempt.");
            } else cm.sendOk("A Fallen Cygnus expedition is already active on this channel.");
            cm.dispose();
        }
    } else if (status == 1) {
        if (selection == 1) {
            if (cm.getExpedition(exped) != null) { cm.sendOk("An expedition is already being organized on this channel."); cm.dispose(); return; }
            var res = cm.createExpedition(exped);
            if (res == 0) cm.sendOk("The Fallen Cygnus Expedition has been created. Recruit your team, then talk to me again to begin.");
            else if (res > 0) cm.sendOk("You have reached the expedition-attempt limit. Try again after the reset.");
            else cm.sendOk("The expedition could not be created. Please try again.");
            cm.dispose();
        } else { cm.dispose(); }
    } else if (status == 2) {
        if (selection == 1) {
            expedMembers = expedition.getMemberList();
            var size = expedMembers.size();
            var text = "Current expedition members (select a member to remove):\r\n\r\n1. " + expedition.getLeader().getName();
            for (var i = 1; i < size; i++) text += "\r\n#b#L" + (i + 1) + "#" + (i + 1) + ". " + expedMembers.get(i).getValue() + "#l";
            cm.sendSimple(text); status = 6;
        } else if (selection == 2) {
            var min = exped.getMinSize(), size = expedition.getMemberList().size();
            if (size < min) { cm.sendOk("The expedition needs at least " + min + " registered member(s). Currently registered: " + size); cm.dispose(); return; }
            cm.sendOk("The expedition is ready. Fallen Cygnus awaits."); status = 4;
        } else if (selection == 3) {
            cm.endExpedition(expedition); cm.sendOk("The Fallen Cygnus expedition has been ended."); cm.dispose();
        }
    } else if (status == 4) {
        em.setProperty("leader", player.getName());
        em.setProperty("channel", player.getClient().getChannel());
        if (!em.startInstance(expedition)) cm.sendOk("This channel already has an active Fallen Cygnus instance. Wait for it to finish or use another channel.");
        cm.dispose();
    } else if (status == 6) {
        if (selection > 1) {
            var banned = expedMembers.get(selection - 1); expedition.ban(banned); cm.sendOk("Removed " + banned.getValue() + " from the expedition."); cm.dispose();
        } else { cm.sendSimple(list); status = 2; }
    }
}
