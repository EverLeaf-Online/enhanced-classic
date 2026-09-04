/*
 * EverLeaf - Gate to the Future / Empress expedition
 *
 * This event is intentionally gated while the matching v83 client assets and
 * imported server XML are still being staged. Do not enable it independently
 * of the full Gate/Future Henesys/Knight Stronghold package.
 */

var isPq = true;
var minPlayers = 3, maxPlayers = 12;
var minLevel = 180, maxLevel = 250;
var entryMap = 271040100;   // Cygnus's Chamber
var exitMap = 271040000;    // Cygnus Garden
var recruitMap = 271040000;
var clearMap = 271040000;
var minMapId = 271040100;
var maxMapId = 271040300;
var eventTime = 60;

const maxLobbies = 1;
const CYGNUS_FINAL = 8850011;
const PHASE_ONE = [8850000, 8850001, 8850002, 8850003, 8850004];
const PHASE_TWO = [8850005, 8850006, 8850007, 8850008, 8850009];
const PHASE_THREE = [8850010];
const PHASE_FOUR = [CYGNUS_FINAL];
const SPAWN_X = [-560, -280, 0, 280, 560];

function init() {
    setEventRequirements();
}

function getMaxLobbies() {
    return maxLobbies;
}

function setEventRequirements() {
    var reqStr = "";
    reqStr += "\r\n    Number of players: " + minPlayers + " ~ " + maxPlayers;
    reqStr += "\r\n    Level range: " + minLevel + " ~ " + maxLevel;
    reqStr += "\r\n    Time limit: " + eventTime + " minutes";
    em.setProperty("party", reqStr);
}

function setEventExclusives(eim) {
    eim.setExclusiveItems([]);
}

function setEventRewards(eim) {
    // Rare scrolls are real monster drops on final Cygnus (8850011), not
    // generic event rewards. Keeping this empty prevents duplicate faucets.
    eim.setEventRewards(1, [], []);
    eim.setEventClearStageExp([]);
    eim.setEventClearStageMeso([]);
}

function setup(channel) {
    const EmpressContentPolicy = Java.type('everleaf.content.EmpressContentPolicy');
    if (!EmpressContentPolicy.isEnabled()) {
        return null;
    }

    var eim = em.newInstance("Empress" + channel);
    eim.setProperty("canJoin", 1);
    eim.setProperty("defeatedBoss", 0);
    eim.setProperty("channel", channel);
    eim.setProperty("phase", 1);

    var map = eim.getInstanceMap(entryMap);
    map.resetPQ(1);

    eim.startEventTimer(eventTime * 60000);
    setEventRewards(eim);
    setEventExclusives(eim);
    return eim;
}

function afterSetup(eim) {
    eim.dropMessage(5, "[Expedition] The Empress battle has begun. The Chief Knights are approaching.");
    spawnPhase(eim, 1);
}

function spawnMob(eim, mobId, x, allowDrops) {
    const LifeFactory = Java.type('server.life.LifeFactory');
    const Point = Java.type('java.awt.Point');
    var mob = LifeFactory.getMonster(mobId);
    if (!allowDrops) {
        mob.disableDrops();
    }
    eim.getInstanceMap(entryMap).spawnMonsterOnGroundBelow(mob, new Point(x, 0));
}

function spawnPhase(eim, phase) {
    var ids;
    var allowDrops = false;

    if (phase == 1) {
        ids = PHASE_ONE;
        eim.dropMessage(6, "[Empress] Phase 1: Mihile, Oz, Irena, Eckhart, and Hawkeye enter the chamber.");
    } else if (phase == 2) {
        ids = PHASE_TWO;
        eim.dropMessage(6, "[Empress] Phase 2: the empowered Chief Knights return for a final stand.");
    } else if (phase == 3) {
        ids = PHASE_THREE;
        eim.dropMessage(6, "[Empress] Phase 3: Shinsoo guards the path to Cygnus.");
    } else if (phase == 4) {
        ids = PHASE_FOUR;
        allowDrops = true;
        eim.setIntProperty("canJoin", 0);
        eim.dropMessage(6, "[Empress] Final Phase: Empress Cygnus enters the battle.");
    } else {
        return;
    }

    eim.setIntProperty("phase", phase);
    for (var i = 0; i < ids.length; i++) {
        var x = ids.length == 1 ? 0 : SPAWN_X[i];
        spawnMob(eim, ids[i], x, allowDrops);
    }
}

function playerEntry(eim, player) {
    var map = eim.getMapInstance(entryMap);
    player.changeMap(map, map.getPortal(0));
    eim.dropMessage(5, "[Expedition] " + player.getName() + " has entered Cygnus's Chamber.");
}

function scheduledTimeout(eim) {
    eim.dropMessage(5, "[Expedition] Time has expired. The Empress expedition has failed.");
    end(eim);
}

function changedMap(eim, player, mapid) {
    if (mapid < minMapId || mapid > maxMapId) {
        if (eim.isExpeditionTeamLackingNow(true, minPlayers, player)) {
            eim.unregisterPlayer(player);
            end(eim);
        } else {
            eim.unregisterPlayer(player);
        }
    }
}

function changedLeader(eim, leader) {}
function playerDead(eim, player) {}

function playerRevive(eim, player) {
    eim.unregisterPlayer(player);
    player.changeMap(exitMap, 0);
    return false;
}

function playerDisconnected(eim, player) {
    if (eim.isExpeditionTeamLackingNow(true, minPlayers, player)) {
        eim.unregisterPlayer(player);
        end(eim);
    } else {
        eim.unregisterPlayer(player);
    }
}

function leftParty(eim, player) {}
function disbandParty(eim) { end(eim); }
function monsterValue(eim, mobId) { return 1; }
function playerUnregistered(eim, player) {}

function playerExit(eim, player) {
    eim.unregisterPlayer(player);
    player.changeMap(exitMap, 0);
}

function end(eim) {
    var players = eim.getPlayers();
    for (var i = 0; i < players.size(); i++) {
        playerExit(eim, players.get(i));
    }
    eim.dispose();
}

function giveRandomEventReward(eim, player) {
    eim.giveEventReward(player);
}

function clearPQ(eim) {
    eim.stopEventTimer();
    eim.setEventCleared();
}

function recordWeeklyClears(eim) {
    const EmpressWeeklyLockoutService = Java.type('everleaf.content.EmpressWeeklyLockoutService');
    var players = eim.getPlayers();
    for (var i = 0; i < players.size(); i++) {
        var player = players.get(i);
        EmpressWeeklyLockoutService.markClear(player.getAccountID());
    }
}

function monsterKilled(mob, eim) {
    if (mob.getId() != CYGNUS_FINAL) {
        return;
    }

    eim.setIntProperty("defeatedBoss", 1);
    eim.setIntProperty("canJoin", 0);
    recordWeeklyClears(eim);
    eim.showClearEffect(mob.getMap().getId());
    eim.clearPQ();
    eim.dropMessage(6, "[Expedition] Cygnus has been defeated. Weekly clear credit has been recorded for the expedition.");
}

function allMonstersDead(eim) {
    if (eim.isEventCleared()) {
        return;
    }

    var phase = eim.getIntProperty("phase");
    if (phase >= 1 && phase < 4) {
        var next = phase + 1;
        eim.dropMessage(5, "[Empress] The next phase begins in 8 seconds. Prepare yourselves.");
        eim.setIntProperty("phase", next);
        eim.schedule("startNextPhase", 8 * 1000);
    }
}

function startNextPhase(eim) {
    if (eim == null || eim.isEventCleared()) {
        return;
    }
    spawnPhase(eim, eim.getIntProperty("phase"));
}

function cancelSchedule() {}
function dispose(eim) {}
