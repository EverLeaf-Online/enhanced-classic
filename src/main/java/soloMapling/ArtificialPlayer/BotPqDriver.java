package soloMapling.ArtificialPlayer;

import client.Character;
import net.server.world.Party;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import scripting.event.EventInstanceManager;
import server.TimerManager;
import server.life.Monster;
import server.life.NPC;
import server.maps.Portal;
import server.maps.Reactor;
import soloMapling.ArtificialPlayer.BotAttackSystem.BotAttackDriver;
import soloMapling.ArtificialPlayer.GCMoveSystem.GCMovement;

import java.awt.Point;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ScheduledFuture;

/**
 * Controlled party-quest runner for headless EverLeaf QA players.
 *
 * <p>The real NPC/event/portal/reactor scripts remain authoritative. This class deliberately
 * does not set PQ stage properties, award rewards, or force a scripted clear. It adapts the
 * useful SoloMapling v0.3 OPQ-orchestrator pattern: keep the artificial players attached to
 * the real party/event instance, move them to actual objectives, hit real reactors, fight
 * real monsters and drive ordinary NPC/portal interactions.</p>
 */
public final class BotPqDriver {
    private static final Logger log = LoggerFactory.getLogger(BotPqDriver.class);
    private static final long TICK_MS = 350L;
    private static final long DEFAULT_TIMEOUT_MS = 30L * 60L * 1000L;
    private static final int MAX_ENTRY_ACTIONS = 12;
    private static final double INTERACT_RANGE_SQ = 150.0 * 150.0;
    private static final Map<Integer, Run> runsByBotId = new ConcurrentHashMap<>();

    private BotPqDriver() {}

    public static PqResult start(Character leader, int entryNpcId) {
        return start(leader, entryNpcId, 0, DEFAULT_TIMEOUT_MS);
    }

    public static synchronized PqResult start(Character leader, int entryNpcId, int menuSelection, long timeoutMs) {
        if (!eligible(leader)) return PqResult.fail("not-eligible");
        Party party = leader.getParty();
        if (party == null) return PqResult.fail("party-required");
        if (party.getLeaderId() != leader.getId()) return PqResult.fail("party-leader-required");
        NPC entry = BotNpcDriver.findNpc(leader, entryNpcId);
        if (entry == null) return PqResult.fail("entry-npc-not-on-map");

        List<Character> participants = new ArrayList<>();
        for (Character member : leader.getPartyMembersOnline()) {
            if (eligible(member) && BotHelpers.isBot(member) && member.getParty() == party) participants.add(member);
        }
        if (participants.isEmpty()) return PqResult.fail("no-bot-party-members");
        for (Character bot : participants) {
            Run old = runsByBotId.get(bot.getId());
            if (old != null) old.stop("replaced");
            stopTransient(bot);
        }

        Run run = new Run(leader, participants, entryNpcId, menuSelection,
                Math.max(30_000L, timeoutMs));
        for (Character bot : participants) runsByBotId.put(bot.getId(), run);
        run.task = TimerManager.getInstance().register(run, TICK_MS, TICK_MS);
        return run.snapshot("started");
    }

    public static synchronized PqResult stop(Character bot) {
        Run run = bot == null ? null : runsByBotId.get(bot.getId());
        if (run == null) return PqResult.fail("not-running");
        run.stop("stopped");
        return run.snapshot("stopped");
    }

    public static PqResult status(Character bot) {
        Run run = bot == null ? null : runsByBotId.get(bot.getId());
        return run == null ? PqResult.fail("not-running") : run.snapshot("status");
    }

    public static boolean isRunning(Character bot) {
        return bot != null && runsByBotId.containsKey(bot.getId());
    }

    private enum Phase { ENTERING, RUNNING, COMPLETE, FAILED, STOPPED }

    private static final class Run implements Runnable {
        private final Character leader;
        private final List<Character> participants;
        private final int entryNpcId;
        private final int menuSelection;
        private final long startedAt = System.currentTimeMillis();
        private final long timeoutMs;
        private volatile Phase phase = Phase.ENTERING;
        private volatile ScheduledFuture<?> task;
        private volatile EventInstanceManager event;
        private int entryActions;
        private int reactorHits;
        private int attacks;
        private int combatHits;
        private int npcActions;
        private int portalUses;
        private int deaths;
        private int eventRegistrations;
        private int mapChanges;
        private int lastLeaderMapId;
        private long lastFailureLogAt;

        private Run(Character leader, List<Character> participants, int entryNpcId, int menuSelection, long timeoutMs) {
            this.leader = leader;
            this.participants = List.copyOf(participants);
            this.entryNpcId = entryNpcId;
            this.menuSelection = menuSelection;
            this.timeoutMs = timeoutMs;
            this.lastLeaderMapId = leader.getMapId();
        }

        @Override
        public void run() {
            try { tick(); }
            catch (Throwable t) {
                long now = System.currentTimeMillis();
                if (now - lastFailureLogAt >= 5_000L) {
                    lastFailureLogAt = now;
                    log.warn("SoloMapling PQ QA tick recovered leader={} phase={}", leader.getId(), phase, t);
                }
            }
        }

        private void tick() {
            if (isTerminal()) return;
            if (System.currentTimeMillis() - startedAt >= timeoutMs) { fail("timeout"); return; }
            if (!eligibleWithoutAlive(leader) || leader.getParty() == null) { fail("leader-left-party-or-world"); return; }

            if (leader.getMapId() != lastLeaderMapId) {
                mapChanges++;
                lastLeaderMapId = leader.getMapId();
            }

            if (phase == Phase.ENTERING) tickEntry();
            else if (phase == Phase.RUNNING) tickEvent();
        }

        private void tickEntry() {
            EventInstanceManager leaderEvent = leader.getEventInstance();
            if (leaderEvent != null) {
                event = leaderEvent;
                attachHeadlessPartyMembers();
                phase = Phase.RUNNING;
                return;
            }
            if (entryActions >= MAX_ENTRY_ACTIONS) { fail("pq-entry-did-not-start-event"); return; }

            BotNpcDriver.InteractionResult result;
            if (entryActions == 0) result = BotNpcDriver.start(leader, entryNpcId);
            else result = BotNpcDriver.next(leader, menuSelection);
            entryActions++;
            if (result.success()) npcActions++;
            else if (entryActions > 1 && !"no-active-dialogue".equals(result.reason())) fail("pq-entry-" + result.reason());
        }

        private void attachHeadlessPartyMembers() {
            if (event == null) return;
            for (Character bot : participants) {
                if (!eligibleWithoutAlive(bot)) continue;
                if (bot.getEventInstance() == event) continue;
                // Headless clients are not always moved by the same packet-facing entry path as a real
                // client. Registering invokes the event's real playerEntry script, matching the donor
                // OPQ orchestrator's role without inventing stage state or rewards.
                event.registerPlayer(bot);
                if (bot.getEventInstance() == event) eventRegistrations++;
            }
        }

        private void tickEvent() {
            if (event == null) { fail("event-instance-lost"); return; }
            attachHeadlessPartyMembers();

            boolean anyoneStillInEvent = false;
            for (Character bot : participants) {
                if (!eligibleWithoutAlive(bot)) continue;
                if (bot.getEventInstance() == event) anyoneStillInEvent = true;
                tickParticipant(bot);
            }

            if (!anyoneStillInEvent || event.getPlayerCount() == 0) complete();
        }

        private void tickParticipant(Character bot) {
            if (!bot.isAlive()) {
                deaths++;
                stopTransient(bot);
                try {
                    boolean eventAllowsRevive = event.revivePlayer(bot);
                    if (eventAllowsRevive && bot.getMap() != null) bot.respawn(bot.getMap().getReturnMapId());
                } catch (RuntimeException ex) {
                    log.warn("SoloMapling PQ QA revive failed bot={}", bot.getId(), ex);
                }
                return;
            }

            BotConsumableDriver.UseResult use = BotConsumableDriver.tick(bot);
            if (use.used()) return;
            BotBuffDriver.BuffResult buff = BotBuffDriver.tick(bot);
            if (buff.applied()) return;

            Monster monster = nearestMonster(bot);
            if (monster != null) { fight(bot, monster); return; }

            Reactor reactor = nearestLiveReactor(bot);
            if (reactor != null) { handleReactor(bot, reactor); return; }

            BotLootDriver.LootResult loot = BotLootDriver.tick(bot);
            if (loot.found()) return;

            NPC npc = BotNpcDriver.nearestNpc(bot, false);
            if (npc != null) {
                handleNpc(bot, npc);
                return;
            }

            tryPortal(bot);
        }

        private void fight(Character bot, Monster monster) {
            Point bp = bot.getPosition();
            Point mp = monster.getPosition();
            if (bp == null || mp == null) return;
            int reachX = Math.max(80, BotAttackDriver.attackReachX(bot));
            int reachY = Math.max(80, BotAttackDriver.attackReachY(bot));
            if (Math.abs(mp.x - bp.x) > Math.max(40, reachX - 20) || Math.abs(mp.y - bp.y) > reachY + 250) {
                GCMovement.enable(bot);
                GCMovement.move(bot, mp.x, mp.y);
                return;
            }
            GCMovement.stop(bot);
            attacks++;
            BotAttackDriver.AttackResult result = BotAttackDriver.botAttack(bot);
            if (result.hit()) combatHits++;
        }

        private void handleReactor(Character bot, Reactor reactor) {
            Point bp = bot.getPosition();
            Point rp = reactor.getPosition();
            if (bp == null || rp == null) return;
            if (bp.distanceSq(rp) > INTERACT_RANGE_SQ) {
                GCMovement.enable(bot);
                GCMovement.move(bot, rp.x, rp.y);
                return;
            }
            GCMovement.stop(bot);
            reactor.hitReactor(bot.getClient());
            reactorHits++;
        }

        private void handleNpc(Character bot, NPC npc) {
            Point bp = bot.getPosition();
            Point np = npc.getPosition();
            if (bp == null || np == null) return;
            if (bp.distanceSq(np) > INTERACT_RANGE_SQ) {
                GCMovement.enable(bot);
                GCMovement.move(bot, np.x, np.y);
                return;
            }
            GCMovement.stop(bot);
            BotNpcDriver.InteractionResult result = BotNpcDriver.next(bot, 0);
            if (!result.success() && "no-active-dialogue".equals(result.reason())) result = BotNpcDriver.start(bot, npc.getId());
            if (result.success()) npcActions++;
        }

        private void tryPortal(Character bot) {
            if (bot.getMap() == null || bot.getPosition() == null) return;
            Portal best = null;
            double bestDist = Double.MAX_VALUE;
            for (int id = 0; id < 32; id++) {
                Portal portal = bot.getMap().getPortal(id);
                if (portal == null || !portal.getPortalStatus() || portal.getPosition() == null) continue;
                // Ignore spawn portals that have no script and lead nowhere.
                if (portal.getScriptName() == null && portal.getTargetMapId() < 0) continue;
                double dist = bot.getPosition().distanceSq(portal.getPosition());
                if (dist < bestDist) { bestDist = dist; best = portal; }
            }
            if (best == null) return;
            if (bestDist > INTERACT_RANGE_SQ) {
                GCMovement.enable(bot);
                GCMovement.move(bot, best.getPosition().x, best.getPosition().y);
                return;
            }
            int before = bot.getMapId();
            GCMovement.stop(bot);
            best.enterPortal(bot.getClient());
            portalUses++;
            if (bot.getMapId() != before) mapChanges++;
        }

        private void complete() {
            phase = Phase.COMPLETE;
            cancel();
            cleanupMappings();
            for (Character bot : participants) stopTransient(bot);
        }

        private void fail(String reason) {
            phase = Phase.FAILED;
            cancel();
            cleanupMappings();
            for (Character bot : participants) stopTransient(bot);
            log.warn("SoloMapling PQ QA failed leader={} reason={} event={}", leader.getId(), reason, eventName());
        }

        private void stop(String reason) {
            if (isTerminal()) return;
            phase = Phase.STOPPED;
            cancel();
            cleanupMappings();
            for (Character bot : participants) stopTransient(bot);
        }

        private void cleanupMappings() {
            for (Character bot : participants) runsByBotId.remove(bot.getId(), this);
        }

        private void cancel() {
            ScheduledFuture<?> current = task;
            if (current != null) current.cancel(false);
        }

        private boolean isTerminal() {
            return phase == Phase.COMPLETE || phase == Phase.FAILED || phase == Phase.STOPPED;
        }

        private String eventName() {
            try { return event == null || event.getEm() == null ? "" : event.getEm().getName(); }
            catch (RuntimeException ignored) { return ""; }
        }

        private PqResult snapshot(String reason) {
            long timeLeft = event == null ? 0L : event.getTimeLeft();
            return new PqResult(true, phase.name().toLowerCase(), eventName(), participants.size(),
                    event == null ? 0 : event.getPlayerCount(), entryActions, eventRegistrations, mapChanges,
                    attacks, combatHits, reactorHits, npcActions, portalUses, deaths,
                    System.currentTimeMillis() - startedAt, timeLeft, reason);
        }
    }

    private static Monster nearestMonster(Character bot) {
        Point p = bot.getPosition();
        if (p == null || bot.getMap() == null) return null;
        return bot.getMap().getAllMonsters().stream()
                .filter(m -> m != null && m.isAlive() && m.getPosition() != null)
                .min(Comparator.comparingDouble(m -> p.distanceSq(m.getPosition())))
                .orElse(null);
    }

    private static Reactor nearestLiveReactor(Character bot) {
        Point p = bot.getPosition();
        if (p == null || bot.getMap() == null) return null;
        return bot.getMap().getAllReactors().stream()
                .filter(r -> r != null && r.isAlive() && r.getPosition() != null)
                .min(Comparator.comparingDouble(r -> p.distanceSq(r.getPosition())))
                .orElse(null);
    }

    private static void stopTransient(Character bot) {
        if (bot == null) return;
        BareBotHunter.stop(bot);
        BareBotAutopilot.stop(bot);
        BotBossDriver.stop(bot);
        GCMovement.disable(bot);
        BotAttackDriver.clearBot(bot.getId());
        BotLootDriver.clearBot(bot.getId());
        BotBuffDriver.clearBot(bot.getId());
        BotConsumableDriver.clearBot(bot.getId());
        BotNpcDriver.cancel(bot);
    }

    private static boolean eligible(Character bot) {
        return eligibleWithoutAlive(bot) && bot.isAlive();
    }

    private static boolean eligibleWithoutAlive(Character bot) {
        return bot != null && BotHelpers.isBot(bot) && bot.getClient() != null && bot.isLoggedinWorld() && bot.getMap() != null;
    }

    public record PqResult(boolean success, String phase, String eventName, int participants, int eventPlayers,
                           int entryActions, int eventRegistrations, int mapChanges, int attacks, int combatHits,
                           int reactorHits, int npcActions, int portalUses, int deaths, long elapsedMs,
                           long eventTimeLeftMs, String reason) {
        static PqResult fail(String reason) {
            return new PqResult(false, "stopped", "", 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0L, 0L, reason);
        }
    }
}
