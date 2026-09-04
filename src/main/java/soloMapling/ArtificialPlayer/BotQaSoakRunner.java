package soloMapling.ArtificialPlayer;

import client.Character;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import server.TimerManager;

import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ScheduledFuture;

/**
 * Explicitly armed, bounded multi-bot soak runner for controlled EverLeaf QA.
 *
 * <p>This never starts from server bootstrap. A GM must first create a bounded {@link BotQaFleet}
 * and then arm a soak run. The runner keeps EverLeaf authoritative, starts the normal autonomous
 * hunter on each synthetic player, records recovery/health invariants, and stops all hunters when
 * the requested duration expires.</p>
 */
public final class BotQaSoakRunner {
    private static final Logger log = LoggerFactory.getLogger(BotQaSoakRunner.class);
    private static final long TICK_MS = 1_000L;
    private static final String ARM_TOKEN = "ARM";
    public static final int MAX_DURATION_MINUTES = 12 * 60;
    private static final Map<Integer, Run> runsByOwner = new ConcurrentHashMap<>();
    // Terminal snapshots deliberately contain no Character references, so completed/stopped soak runs
    // cannot pin synthetic players or their headless clients in memory.
    private static final Map<Integer, SoakResult> lastResultsByOwner = new ConcurrentHashMap<>();

    private BotQaSoakRunner() {}

    /** Fail closed for callers that omit the explicit production-soak arming token. */
    public static SoakResult start(int ownerId, int durationMinutes) {
        return SoakResult.fail("explicit-arm-token-required");
    }

    public static synchronized SoakResult start(int ownerId, int durationMinutes, String armToken) {
        if (armToken == null || !ARM_TOKEN.equalsIgnoreCase(armToken)) return SoakResult.fail("explicit-arm-token-required");
        if (ownerId <= 0) return SoakResult.fail("invalid-owner");
        if (durationMinutes < 1 || durationMinutes > MAX_DURATION_MINUTES) {
            return SoakResult.fail("duration-must-be-1-to-" + MAX_DURATION_MINUTES + "-minutes");
        }
        BotQaFleet.Fleet fleet = BotQaFleet.get(ownerId);
        if (fleet == null || fleet.bots().isEmpty()) return SoakResult.fail("fleet-required");

        Run old = runsByOwner.remove(ownerId);
        if (old != null) old.stop("replaced");
        lastResultsByOwner.remove(ownerId);

        Run run = new Run(ownerId, fleet.bots(), durationMinutes * 60_000L);
        int started = 0;
        for (Character bot : run.bots) {
            if (bot != null && bot.isLoggedinWorld() && bot.getMap() != null && BareBotHunter.start(bot)) started++;
        }
        if (started != run.bots.size()) {
            run.stopHunters();
            return SoakResult.fail("not-all-hunters-started:" + started + "/" + run.bots.size());
        }

        run.task = TimerManager.getInstance().register(run, TICK_MS, TICK_MS);
        runsByOwner.put(ownerId, run);
        return run.snapshot("started");
    }

    public static synchronized SoakResult stop(int ownerId) {
        Run run = runsByOwner.get(ownerId);
        if (run == null) return SoakResult.fail("no-soak-run");
        run.stop("stopped");
        SoakResult terminal = lastResultsByOwner.get(ownerId);
        return terminal == null ? run.snapshot("stopped") : terminal;
    }

    public static SoakResult status(int ownerId) {
        Run run = runsByOwner.get(ownerId);
        if (run != null) return run.snapshot("status");
        SoakResult terminal = lastResultsByOwner.get(ownerId);
        return terminal == null ? SoakResult.fail("no-soak-run") : terminal;
    }

    public static boolean isRunning(int ownerId) {
        Run run = runsByOwner.get(ownerId);
        return run != null && "running".equals(run.phase);
    }

    private static final class Run implements Runnable {
        private final int ownerId;
        private final List<Character> bots;
        private final long durationMs;
        private final long startedAt = System.currentTimeMillis();
        private final long baselineLevelSum;
        private final long baselineMesosSum;
        private final Set<Integer> deadLastTick = new HashSet<>();
        private volatile ScheduledFuture<?> task;
        private volatile String phase = "running";
        private volatile String terminalReason = "";
        private int deaths;
        private int recoveries;
        private int invariantFailures;
        private int exceptions;
        private int ticks;

        private Run(int ownerId, List<Character> bots, long durationMs) {
            this.ownerId = ownerId;
            this.bots = List.copyOf(bots);
            this.durationMs = durationMs;
            this.baselineLevelSum = levelSum(this.bots);
            this.baselineMesosSum = mesoSum(this.bots);
        }

        @Override
        public void run() {
            try {
                tick();
            } catch (Throwable t) {
                exceptions++;
                log.warn("SoloMapling QA soak tick recovered owner={} phase={}", ownerId, phase, t);
            }
        }

        private void tick() {
            if (!"running".equals(phase)) return;
            ticks++;

            BotQaFleet.Fleet currentFleet = BotQaFleet.get(ownerId);
            if (currentFleet == null || currentFleet.bots().size() != bots.size()) {
                fail("fleet-changed-or-removed");
                return;
            }

            int unhealthy = 0;
            Set<Integer> deadNow = new HashSet<>();
            for (Character bot : bots) {
                if (bot == null || !bot.isLoggedinWorld() || bot.getMap() == null) {
                    unhealthy++;
                    continue;
                }
                if (!bot.isAlive()) {
                    deadNow.add(bot.getId());
                    if (!deadLastTick.contains(bot.getId())) deaths++;
                } else {
                    if (deadLastTick.contains(bot.getId())) recoveries++;
                    if (!BareBotHunter.isHunting(bot)) unhealthy++;
                }
            }
            deadLastTick.clear();
            deadLastTick.addAll(deadNow);

            if (BareBotFactory.activeBotCount() < bots.size()
                    || BotClientHandler.activeClientCount() < bots.size()
                    || unhealthy > 0) {
                invariantFailures++;
            }

            if (System.currentTimeMillis() - startedAt >= durationMs) complete();
        }

        private void complete() {
            if (!"running".equals(phase)) return;
            phase = "complete";
            terminalReason = "duration-complete";
            finish();
        }

        private void fail(String reason) {
            if (!"running".equals(phase)) return;
            phase = "failed";
            terminalReason = reason;
            finish();
            log.warn("SoloMapling QA soak failed owner={} reason={}", ownerId, reason);
        }

        private void stop(String reason) {
            if (!"running".equals(phase)) return;
            phase = "stopped";
            terminalReason = reason;
            finish();
        }

        private void finish() {
            cancelTask();
            stopHunters();
            SoakResult terminal = snapshot(terminalReason);
            runsByOwner.remove(ownerId, this);
            lastResultsByOwner.put(ownerId, terminal);
        }

        private void stopHunters() {
            for (Character bot : bots) {
                if (bot == null) continue;
                try { BareBotHunter.stop(bot); } catch (RuntimeException ignored) { }
            }
        }

        private void cancelTask() {
            ScheduledFuture<?> current = task;
            if (current != null) current.cancel(false);
        }

        private SoakResult snapshot(String reason) {
            int alive = 0;
            int logged = 0;
            int hunting = 0;
            for (Character bot : bots) {
                if (bot == null) continue;
                if (bot.isAlive()) alive++;
                if (bot.isLoggedinWorld()) logged++;
                if (BareBotHunter.isHunting(bot)) hunting++;
            }
            long elapsed = Math.min(System.currentTimeMillis() - startedAt, durationMs);
            String detail = terminalReason.isEmpty() ? reason : terminalReason;
            return new SoakResult(true, phase, bots.size(), alive, logged, hunting, deaths, recoveries,
                    invariantFailures, exceptions, ticks, elapsed, durationMs,
                    levelSum(bots) - baselineLevelSum, mesoSum(bots) - baselineMesosSum,
                    BareBotFactory.activeBotCount(), BotClientHandler.activeClientCount(), detail);
        }
    }

    private static long levelSum(List<Character> bots) {
        long total = 0L;
        for (Character bot : bots) if (bot != null) total += bot.getLevel();
        return total;
    }

    private static long mesoSum(List<Character> bots) {
        long total = 0L;
        for (Character bot : bots) if (bot != null) total += bot.getMeso();
        return total;
    }

    public record SoakResult(boolean success, String phase, int bots, int alive, int loggedInWorld, int hunting,
                             int deaths, int recoveries, int invariantFailures, int exceptions, int ticks,
                             long elapsedMs, long durationMs, long levelGain, long mesoDelta,
                             int globalFactoryBots, int headlessClients, String reason) {
        static SoakResult fail(String reason) {
            return new SoakResult(false, "stopped", 0, 0, 0, 0, 0, 0, 0, 0, 0,
                    0L, 0L, 0L, 0L, BareBotFactory.activeBotCount(), BotClientHandler.activeClientCount(), reason);
        }
    }
}
