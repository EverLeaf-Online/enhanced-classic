/* EverLeaf Fallen Cygnus / Empress encounter. */
var isPq = true;
var minPlayers = 3, maxPlayers = 12;
var minLevel = 180, maxLevel = 255;
var entryMap = 271040100, exitMap = 271040000, recruitMap = 271040000, clearMap = 271040000;
var minMapId = entryMap, maxMapId = entryMap;
var eventTime = 60;
const maxLobbies = 1;

function init() { setEventRequirements(); }
function getMaxLobbies() { return maxLobbies; }
function setEventRequirements() {
    em.setProperty("party", "\r\n    Players: " + minPlayers + " ~ " + maxPlayers
        + "\r\n    Level range: " + minLevel + " ~ " + maxLevel
        + "\r\n    Time limit: " + eventTime + " minutes");
}
function setEventExclusives(eim) { eim.setExclusiveItems([]); }
function setEventRewards(eim) { eim.setEventRewards(1, [], []); eim.setEventClearStageExp([]); eim.setEventClearStageMeso([]); }

function setup(channel) {
    var eim = em.newInstance("Cygnus" + channel);
    eim.setProperty("canJoin", 1);
    eim.setProperty("everleafEncounterId", "fallen_cygnus");
    eim.setIntProperty("everleafPhase", 0);
    eim.setIntProperty("everleafPhaseKills", 0);
    eim.setIntProperty("everleafCleared", 0);
    eim.getInstanceMap(entryMap).resetPQ(1);
    eim.startEventTimer(eventTime * 60000);
    setEventRewards(eim); setEventExclusives(eim);
    return eim;
}
function afterSetup(eim) { eim.schedule("startEncounter", 3000); }

function spawnTuned(eim, id, x, hp, mp, exp, watk, matk, level) {
    var OverrideMonsterStats = Java.type('server.life.OverrideMonsterStats');
    var Point = Java.type('java.awt.Point');
    var mob = eim.getMonster(id);
    if (mob == null) throw "Missing Fallen Cygnus mob " + id;
    mob.setOverrideStats(new OverrideMonsterStats(hp, mp, exp, watk, matk, 900, 900, level));
    mob.disableDrops();
    eim.getMapInstance(entryMap).spawnMonsterOnGroundBelow(mob, new Point(x, 112));
}

function phase(eim, number, message) {
    eim.setIntProperty("everleafPhase", number);
    eim.setIntProperty("everleafPhaseKills", 0);
    eim.dropMessage(5, message);
}
function startEncounter(eim) {
    if (eim.isEventCleared()) return;
    phase(eim, 1, "[EverLeaf] The Chief Knights have taken the field.");
    var xs = [-520,-260,0,260,520];
    for (var i=0;i<5;i++) spawnTuned(eim, 8850000+i, xs[i], 60000000, 50000, 1000000, 1900, 1850, 185);
}
function startEliteKnights(eim) {
    if (eim.isEventCleared()) return;
    phase(eim, 2, "[EverLeaf] The Chief Knights return with their full strength!");
    var xs = [-520,-260,0,260,520];
    for (var i=0;i<5;i++) spawnTuned(eim, 8850005+i, xs[i], 90000000, 65000, 1500000, 2350, 2250, 188);
}
function startShinsoo(eim) {
    if (eim.isEventCleared()) return;
    phase(eim, 3, "[EverLeaf] Shinsoo descends to defend the Empress. Defeat it before it withdraws!");
    spawnTuned(eim, 8850010, 0, 120000000, 50000, 0, 2500, 2400, 190);
    eim.schedule("shinsooTimeout", 120000);
}
function shinsooTimeout(eim) {
    if (eim.isEventCleared() || eim.getIntProperty("everleafPhase") != 3) return;
    eim.getMapInstance(entryMap).killAllMonsters();
    eim.dropMessage(5, "[EverLeaf] Shinsoo withdraws. Cygnus enters the battle.");
    startCygnus(eim);
}
function startCygnus(eim) {
    if (eim.isEventCleared() || eim.getIntProperty("everleafPhase") >= 4) return;
    phase(eim, 4, "[EverLeaf] Fallen Cygnus has appeared. This is the final phase!");
    spawnTuned(eim, 8850011, 0, 500000000, 90000, 25000000, 2850, 2750, 195);
}

function playerEntry(eim, player) {
    var Runtime = Java.type('everleaf.progression.EverleafProgressionRuntime');
    var Instant = Java.type('java.time.Instant');
    var started = Runtime.cygnusEncounterLifecycleService().begin(player.getAccountID(), player.getId(), player.getLevel(), Instant.now());
    eim.setProperty("everleafAttemptId:" + player.getId(), String(started.attemptId()));
    eim.setProperty("everleafRewardMode:" + player.getId(), started.mode().name());
    var map = eim.getMapInstance(entryMap);
    player.changeMap(map, map.getPortal(0));
    eim.dropMessage(5, "[Expedition] " + player.getName() + " entered the Fallen Cygnus encounter.");
}
function scheduledTimeout(eim) { eim.dropMessage(5, "[EverLeaf] The Empress encounter has timed out."); end(eim); }
function changedMap(eim, player, mapid) {
    if (mapid < minMapId || mapid > maxMapId) {
        eim.unregisterPlayer(player);
        if (eim.getPlayerCount() == 0 && !eim.isEventCleared()) end(eim);
    }
}
function changedLeader(eim, leader) {}
function playerDead(eim, player) {}
function playerRevive(eim, player) { eim.unregisterPlayer(player); player.changeMap(exitMap, 0); return false; }
function playerDisconnected(eim, player) { return 0; }
function leftParty(eim, player) { playerExit(eim, player); }
function disbandParty(eim) { end(eim); }
function monsterValue(eim, mobId) { return 1; }
function playerUnregistered(eim, player) {
    if (eim.isEventCleared()) return;
    var attemptId = eim.getProperty("everleafAttemptId:" + player.getId());
    if (attemptId == null) return;
    try {
        var Runtime = Java.type('everleaf.progression.EverleafProgressionRuntime');
        var Instant = Java.type('java.time.Instant');
        var Long = Java.type('java.lang.Long');
        Runtime.cygnusEncounterLifecycleService().fail(Long.parseLong(attemptId), Instant.now());
    } catch (error) { player.dropMessage(5, "[EverLeaf] Encounter exit record could not be finalized; contact a GM."); }
}
function playerExit(eim, player) { eim.unregisterPlayer(player); player.changeMap(exitMap, 0); }
function end(eim) {
    var party = eim.getPlayers();
    for (var i = party.size() - 1; i >= 0; i--) playerExit(eim, party.get(i));
    eim.dispose();
}
function giveRandomEventReward(eim, player) {}
function clearPQ(eim) { eim.stopEventTimer(); eim.setIntProperty("everleafCleared", 1); eim.setEventCleared(); }

function finishPlayer(eim, player) {
    var attemptId = eim.getProperty("everleafAttemptId:" + player.getId());
    var mode = eim.getProperty("everleafRewardMode:" + player.getId());
    if (attemptId == null || mode == null) { player.dropMessage(5, "[EverLeaf] Your clear needs GM review because its attempt record is missing."); return; }
    try {
        var Runtime = Java.type('everleaf.progression.EverleafProgressionRuntime');
        var RewardMode = Java.type('everleaf.progression.EnhancedBossRewardMode');
        var RewardPolicy = Java.type('everleaf.progression.CygnusRewardPolicy');
        var RewardDelivery = Java.type('everleaf.progression.CygnusRewardDelivery');
        var Randomizer = Java.type('tools.Randomizer');
        var Instant = Java.type('java.time.Instant');
        var Long = Java.type('java.lang.Long');
        var completion = Runtime.cygnusEncounterLifecycleService().complete(Long.parseLong(attemptId), RewardMode.valueOf(mode), Instant.now());
        if (!completion.completed()) { player.dropMessage(5, "[EverLeaf] Cygnus clear could not be finalized (" + completion.reason() + ")."); return; }
        if (!completion.weeklyRewardClaimed()) { player.dropMessage(5, "[EverLeaf] Practice clear complete; this account already claimed its weekly Cygnus reward."); return; }
        var rare = RewardPolicy.roll(Randomizer.nextInt(RewardPolicy.ROLL_SCALE));
        if (rare.itemId() == 0) { player.dropMessage(5, "[EverLeaf] Weekly Fallen Cygnus clear recorded. No rare scroll rolled this week."); return; }
        if (RewardDelivery.deliver(player, rare.itemId())) player.dropMessage(5, "[EverLeaf] Fallen Cygnus weekly rare reward received!");
        else player.dropMessage(5, "[EverLeaf] Your rare Cygnus reward could not fit in inventory. Contact a GM with this clear time.");
    } catch (error) { player.dropMessage(5, "[EverLeaf] Reward finalization failed safely. Contact a GM; do not repeat the clear yet."); }
}

function monsterKilled(mob, eim) {
    var id = mob.getId(), p = eim.getIntProperty("everleafPhase");
    if (p == 1 && id >= 8850000 && id <= 8850004) {
        var a = eim.getIntProperty("everleafPhaseKills") + 1; eim.setIntProperty("everleafPhaseKills", a); if (a >= 5) eim.schedule("startEliteKnights", 2500);
    } else if (p == 2 && id >= 8850005 && id <= 8850009) {
        var b = eim.getIntProperty("everleafPhaseKills") + 1; eim.setIntProperty("everleafPhaseKills", b); if (b >= 5) eim.schedule("startShinsoo", 2500);
    } else if (p == 3 && id == 8850010) {
        eim.schedule("startCygnus", 2500);
    } else if (p == 4 && id == 8850011) {
        eim.showClearEffect(entryMap); clearPQ(eim); eim.dropMessage(5, "[EverLeaf] Fallen Cygnus has been defeated!");
        var players = eim.getPlayers(); for (var i=0;i<players.size();i++) finishPlayer(eim, players.get(i));
    }
}
function allMonstersDead(eim) {}
function cancelSchedule() {}
function dispose(eim) {}
