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

    var map = eim.getInstanceMap(entryMap);
    map.resetPQ(1);

    // The imported encounter package carries Cygnus and her summon family.
    // Until the MobSkill review is complete, only the final body is spawned
    // explicitly here; unsupported summon/skill behavior remains gated.
    const LifeFactory = Java.type('server.life.LifeFactory');
    const Point = Java.type('java.awt.Point');
    var cygnus = LifeFactory.getMonster(CYGNUS_FINAL);
    map.spawnMonsterOnGroundBelow(cygnus, new Point(0, 0));

    eim.startEventTimer(eventTime * 60000);
    setEventRewards(eim);
    setEventExclusives(eim);
    return eim;
}

function afterSetup(eim) {
    eim.dropMessage(5, "[Expedition] The Empress battle has begun. Defeat Cygnus before time expires.");
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
    // Death removes the player from the run. Re-entry behavior will be added
    // only after the reconnect/recall policy is validated for Empress.
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

function monsterKilled(mob, eim) {
    if (mob.getId() != CYGNUS_FINAL) {
        return;
    }

    eim.setIntProperty("defeatedBoss", 1);
    eim.setIntProperty("canJoin", 0);
    eim.showClearEffect(mob.getMap().getId());
    eim.clearPQ();
    eim.dropMessage(6, "[Expedition] Cygnus has been defeated.");
}

function allMonstersDead(eim) {}
function cancelSchedule() {}
function dispose(eim) {}
