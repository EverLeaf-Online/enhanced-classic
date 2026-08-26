/*
 * Everleaf — Rooted Zakum
 *
 * Enhanced level-200 reference encounter. Reuses the v83 Zakum map/monster
 * assets but runs as a small-party dedicated instance with its own lobby.
 */

var isPq = true;
var minPlayers = 3, maxPlayers = 6;
var minLevel = 200, maxLevel = 250;
var entryMap = 280030000;
var exitMap = 211042400;
var recruitMap = 211042300;
var clearMap = 211042400;

var minMapId = 280030000;
var maxMapId = 280030000;
var eventTime = 30;

// The event system allocates the first free lobby id to each party, giving
// Rooted Zakum true party isolation instead of one shared world boss room.
const maxLobbies = 20;

function init() {
    setEventRequirements();
}

function getMaxLobbies() {
    return maxLobbies;
}

function setEventRequirements() {
    var reqStr = "";
    reqStr += "\r\n    Party size: " + minPlayers + " ~ " + maxPlayers;
    reqStr += "\r\n    Level range: " + minLevel + " ~ " + maxLevel;
    reqStr += "\r\n    Time limit: " + eventTime + " minutes";
    reqStr += "\r\n    Dedicated Everleaf party instance";
    em.setProperty("party", reqStr);
}

function setEventExclusives(eim) {
    eim.setExclusiveItems([]);
}

function setEventRewards(eim) {
    // Everleaf progression rewards are fulfilled by the server-side encounter
    // service. Keeping the legacy event reward pool empty prevents accidental
    // duplicate power rewards while the weekly/account rules are enforced.
    eim.setEventRewards(1, [], []);
    eim.setEventClearStageExp([]);
    eim.setEventClearStageMeso([]);
}

function getEligibleParty(party) {
    var eligible = [];
    var hasLeader = false;

    if (party.size() > 0) {
        var partyList = party.toArray();
        for (var i = 0; i < party.size(); i++) {
            var ch = partyList[i];
            if (ch.getMapId() == recruitMap && ch.getLevel() >= minLevel && ch.getLevel() <= maxLevel) {
                if (ch.isLeader()) {
                    hasLeader = true;
                }
                eligible.push(ch);
            }
        }
    }

    if (!(hasLeader && eligible.length >= minPlayers && eligible.length <= maxPlayers)) {
        eligible = [];
    }

    return Java.to(eligible, Java.type('net.server.world.PartyCharacter[]'));
}

function setup(level, lobbyid) {
    var eim = em.newInstance("RootedZakum-" + lobbyid);
    eim.setProperty("level", level);
    eim.setProperty("everleafEncounterId", "rooted_zakum");
    eim.setProperty("defeatedBoss", 0);
    eim.setProperty("everleafCleared", 0);

    eim.getInstanceMap(entryMap).resetPQ(level);
    eim.startEventTimer(eventTime * 60000);
    setEventRewards(eim);
    setEventExclusives(eim);
    return eim;
}

function afterSetup(eim) {}

function playerEntry(eim, player) {
    var Runtime = Java.type('everleaf.progression.EverleafProgressionRuntime');
    var Instant = Java.type('java.time.Instant');
    var started = Runtime.rootedZakumLifecycleService().begin(
        player.getAccountID(), player.getId(), player.getLevel(), Instant.now()
    );
    eim.setProperty("everleafAttemptId:" + player.getId(), String(started.attemptId()));
    eim.setProperty("everleafRewardMode:" + player.getId(), started.mode().name());
    eim.dropMessage(5, "[Everleaf] " + player.getName() + " entered Rooted Zakum.");
    var map = eim.getMapInstance(entryMap);
    player.changeMap(map, map.getPortal(0));
}

function scheduledTimeout(eim) {
    eim.dropMessage(5, "[Everleaf] Rooted Zakum has enraged. The encounter has ended.");
    end(eim);
}

function changedMap(eim, player, mapid) {
    if (mapid < minMapId || mapid > maxMapId) {
        eim.unregisterPlayer(player);
        if (eim.getPlayerCount() == 0 && !eim.isEventCleared()) {
            end(eim);
        }
    }
}

function changedLeader(eim, leader) {}
function playerDead(eim, player) {}

function playerRevive(eim, player) {
    // Death removes the character from this attempt; remaining members may
    // continue. Party-size enforcement is entry-time only so a death does not
    // instantly erase an otherwise recoverable run.
    eim.unregisterPlayer(player);
    player.changeMap(exitMap, 0);
    return false;
}

function playerDisconnected(eim, player) {
    // The Java-side dedicated-instance layer owns reconnect grace. Do not end
    // the whole party encounter merely because one client disconnects.
    return 0;
}

function leftParty(eim, player) {
    playerExit(eim, player);
}

function disbandParty(eim) {
    end(eim);
}

function monsterValue(eim, mobId) {
    return 1;
}

function playerUnregistered(eim, player) {
    if (eim.isEventCleared()) return;
    var attemptId = eim.getProperty("everleafAttemptId:" + player.getId());
    if (attemptId == null) return;
    try {
        var Runtime = Java.type('everleaf.progression.EverleafProgressionRuntime');
        var Instant = Java.type('java.time.Instant');
        var Long = Java.type('java.lang.Long');
        Runtime.rootedZakumLifecycleService().fail(Long.parseLong(attemptId), Instant.now());
    } catch (error) {
        player.dropMessage(5, "[Everleaf] The encounter exit record could not be finalized. Please contact a GM.");
    }
}

function playerExit(eim, player) {
    eim.unregisterPlayer(player);
    player.changeMap(exitMap, 0);
}

function end(eim) {
    var party = eim.getPlayers();
    for (var i = party.size() - 1; i >= 0; i--) {
        playerExit(eim, party.get(i));
    }
    eim.dispose();
}

function giveRandomEventReward(eim, player) {}

function clearPQ(eim) {
    eim.stopEventTimer();
    eim.setIntProperty("everleafCleared", 1);
    eim.setEventCleared();
}

function isZakumBody(mob) {
    return mob.getId() == 8800002;
}

function monsterKilled(mob, eim) {
    if (isZakumBody(mob)) {
        eim.setIntProperty("defeatedBoss", 1);
        eim.showClearEffect(mob.getMap().getId());
        eim.clearPQ();
        mob.getMap().broadcastZakumVictory();
        eim.dropMessage(5, "[Everleaf] Rooted Zakum has been defeated.");

        var Runtime = Java.type('everleaf.progression.EverleafProgressionRuntime');
        var RewardMode = Java.type('everleaf.progression.EnhancedBossRewardMode');
        var Instant = Java.type('java.time.Instant');
        var Long = Java.type('java.lang.Long');
        var players = eim.getPlayers();
        for (var i = 0; i < players.size(); i++) {
            var player = players.get(i);
            var attemptId = eim.getProperty("everleafAttemptId:" + player.getId());
            var mode = eim.getProperty("everleafRewardMode:" + player.getId());
            if (attemptId == null || mode == null) {
                player.dropMessage(5, "[Everleaf] Reward delivery is pending because the attempt record is missing. Please contact a GM.");
                continue;
            }
            try {
                var completion = Runtime.rootedZakumLifecycleService().complete(
                    Long.parseLong(attemptId), RewardMode.valueOf(mode), Instant.now()
                );
                if (!completion.completed()) {
                    player.dropMessage(5, "[Everleaf] Reward delivery is pending (" + completion.reason() + "). Your clear remains recorded.");
                } else if (completion.rewarded()) {
                    player.dropMessage(5, "[Everleaf] Weekly clear reward: " + completion.verdantMarks()
                        + " Verdant Marks, 2 Ember Cores, and 1 Ancient Bark.");
                } else {
                    player.dropMessage(5, "[Everleaf] Practice clear complete. Your weekly reward was already claimed on this account.");
                }
            } catch (error) {
                player.dropMessage(5, "[Everleaf] Reward delivery is pending. Your attempt can be safely retried by a GM.");
            }
        }
    }
}

function allMonstersDead(eim) {}
function cancelSchedule() {}
function dispose(eim) {}
