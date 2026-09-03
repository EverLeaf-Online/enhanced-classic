package soloMapling.ArtificialPlayer;

import client.Character;

import java.awt.Point;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.ScheduledFuture;
import java.util.concurrent.TimeUnit;

/**
 * Explicit, bounded multi-bot soak controller for SoloMapling QA.
 *
 * <p>This class never starts at server bootstrap. A GM must first create an owner-scoped
 * {@link BotQaFleet} and then explicitly arm a soak. The controller exercises the normal
 * autonomous hunt/recovery loop, continuously checks registration/client/runtime invariants,
 * attempts bounded self-recovery for stalled hunters, and deterministically removes the fleet
 * when the run completes, fails, or is manually stopped.</p>
 */
public final class BotQaSoak {
    public static final int MIN_DURATION_MINUTES = 1;
    public static final int MAX_DURATION_MINUTES = 12 * 60;
    private static final long CHECK_INTERVAL_SECONDS = 10;
    private static final long DEAD_GRACE_MS = TimeUnit.MINUTES.toMillis(1);
    private static final long STALL_RECOVERY_MS = TimeUnit.MINUTES.toMillis(3);
    private static final long STALL_FAILURE_MS = TimeUnit.MINUTES.toMillis(10);

    private static final ScheduledExecutorService executor = Executors.newSingleThreadScheduledExecutor(r -> {
        Thread thread = new Thread(r, "solomapling-qa-soak");
        thread.setDaemon(true);
        return thread;
    });
    private static final Map<Integer, Session> sessions = new ConcurrentHashMap<>();
    private static final Map<Integer, Report> lastReports = new ConcurrentHashMap<>();

    private BotQaSoak() {}

    public static synchronized Report start(int ownerId, int durationMinutes) {
        if (durationMinutes < MIN_DURATION_MINUTES || durationMinutes > MAX_DURATION_MINUTES) {
            return Report.rejected("duration-must-be-1-to-" + MAX_DURATION_MINUTES + "-minutes");
        }
        if (sessions.containsKey(ownerId)) return Report.rejected("soak-already-running");

        List<Character> bots = BotQaFleet.bots(ownerId);
        if (bots.isEmpty()) return Report.rejected("spawn-fleet-first");
        if (bots.size() > BotQaFleet.MAX_BOTS_PER_FLEET) return Report.rejected("fleet-over-safety-cap");

        long now = System.currentTimeMillis();
        Session session = new Session(ownerId, bots, now, now + TimeUnit.MINUTES.toMillis(durationMinutes));
        sessions.put(ownerId, session);
        for (Character bot : bots) {
            session.capture(bot, now);
            if (!BareBotHunter.isHunting(bot)) BareBotHunter.start(bot);
        }
        session.future = executor.scheduleAtFixedRate(() -> tick(ownerId),
                CHECK_INTERVAL_SECONDS, CHECK_INTERVAL_SECONDS, TimeUnit.SECONDS);
        Report report = session.report(true, false, "running");
        lastReports.put(ownerId, report);
        return report;
    }

    public static synchronized Report stop(int ownerId) {
        Session session = sessions.remove(ownerId);
        if (session == null) {
            Report previous = lastReports.get(ownerId);
            return previous != null ? previous : Report.rejected("no-soak");
        }
        cancel(session);
        BotQaFleet.remove(ownerId);
        Report report = session.report(false, true, "stopped-by-gm");
        lastReports.put(ownerId, report);
        return report;
    }

    public static Report status(int ownerId) {
        Session session = sessions.get(ownerId);
        if (session != null) return session.report(true, false, "running");
        Report previous = lastReports.get(ownerId);
        return previous != null ? previous : Report.rejected("no-soak");
    }

    public static boolean isRunning(int ownerId) {
        return sessions.containsKey(ownerId);
    }

    private static void tick(int ownerId) {
        Session session = sessions.get(ownerId);
        if (session == null) return;
        long now = System.currentTimeMillis();
        try {
            if (now >= session.endsAt) {
                finish(ownerId, session, true, "completed");
                return;
            }

            List<Character> current = BotQaFleet.bots(ownerId);
            if (current.size() != session.expectedBotIds.size()) {
                session.violation("fleet-size-changed");
                finish(ownerId, session, false, "fleet-size-changed");
                return;
            }

            Set<Integer> seen = new HashSet<>();
            for (Character bot : current) {
                if (bot == null) {
                    session.violation("null-bot");
                    finish(ownerId, session, false, "null-bot");
                    return;
                }
                seen.add(bot.getId());
                if (!session.expectedBotIds.contains(bot.getId())) {
                    session.violation("unexpected-bot:" + bot.getId());
                    finish(ownerId, session, false, "bot-identity-changed");
                    return;
                }
                if (bot.getClient() == null || BotClientHandler.getBotClient(bot.getId()) != bot.getClient()) {
                    session.violation("client-registration-lost:" + bot.getId());
                    finish(ownerId, session, false, "client-registration-lost");
                    return;
                }
                if (!bot.isLoggedinWorld() || bot.getMap() == null || bot.getPosition() == null) {
                    session.violation("world-registration-lost:" + bot.getId());
                    finish(ownerId, session, false, "world-registration-lost");
                    return;
                }

                BotState previous = session.states.get(bot.getId());
                if (!bot.isAlive()) {
                    if (previous != null && previous.deadSince > 0 && now - previous.deadSince > DEAD_GRACE_MS) {
                        session.violation("death-recovery-timeout:" + bot.getId());
                        finish(ownerId, session, false, "death-recovery-timeout");
                        return;
                    }
                    session.captureDead(bot, previous, now);
                    continue;
                }

                boolean progressed = previous == null || changed(bot, previous);
                long lastProgress = progressed ? now : previous.lastProgressAt;
                if (!BareBotHunter.isHunting(bot)) {
                    if (BareBotHunter.start(bot)) session.restarts++;
                }
                long stalledFor = now - lastProgress;
                if (stalledFor >= STALL_FAILURE_MS) {
                    session.violation("progress-stall:" + bot.getId());
                    finish(ownerId, session, false, "progress-stall");
                    return;
                }
                if (stalledFor >= STALL_RECOVERY_MS && now - previous.lastRestartAt >= STALL_RECOVERY_MS) {
                    BareBotHunter.stop(bot);
                    if (BareBotHunter.start(bot)) session.restarts++;
                    session.capture(bot, now, lastProgress, now);
                } else {
                    session.capture(bot, now, lastProgress, previous == null ? 0 : previous.lastRestartAt);
                }
            }
            if (!seen.equals(session.expectedBotIds)) {
                session.violation("fleet-membership-changed");
                finish(ownerId, session, false, "fleet-membership-changed");
                return;
            }
            session.checks++;
            lastReports.put(ownerId, session.report(true, false, "running"));
        } catch (RuntimeException failure) {
            session.violation("exception:" + failure.getClass().getSimpleName());
            finish(ownerId, session, false, "runtime-exception");
        }
    }

    private static boolean changed(Character bot, BotState previous) {
        Point p = bot.getPosition();
        BotLootDriver.RewardStats rewards = BotLootDriver.rewardStats(bot);
        return bot.getMapId() != previous.mapId
                || p.x != previous.x || p.y != previous.y
                || bot.getLevel() != previous.level || bot.getExp() != previous.exp
                || bot.getMeso() != previous.mesos || rewards.pickedDrops() != previous.pickedDrops;
    }

    private static synchronized void finish(int ownerId, Session session, boolean success, String reason) {
        if (!sessions.remove(ownerId, session)) return;
        cancel(session);
        BotQaFleet.remove(ownerId);
        Report report = session.report(false, true, success ? reason : "failed:" + reason);
        lastReports.put(ownerId, report);
    }

    private static void cancel(Session session) {
        ScheduledFuture<?> future = session.future;
        if (future != null) future.cancel(false);
    }

    private static final class Session {
        private final int ownerId;
        private final long startedAt;
        private final long endsAt;
        private final Set<Integer> expectedBotIds;
        private final Map<Integer, BotState> states = new HashMap<>();
        private final StringBuilder violations = new StringBuilder();
        private volatile ScheduledFuture<?> future;
        private long checks;
        private int restarts;
        private int violationCount;

        private Session(int ownerId, List<Character> bots, long startedAt, long endsAt) {
            this.ownerId = ownerId;
            this.startedAt = startedAt;
            this.endsAt = endsAt;
            Set<Integer> ids = new HashSet<>();
            for (Character bot : bots) ids.add(bot.getId());
            this.expectedBotIds = Set.copyOf(ids);
        }

        private void capture(Character bot, long now) {
            capture(bot, now, now, 0);
        }

        private void capture(Character bot, long now, long lastProgress, long lastRestart) {
            Point p = bot.getPosition();
            BotLootDriver.RewardStats rewards = BotLootDriver.rewardStats(bot);
            states.put(bot.getId(), new BotState(bot.getMapId(), p.x, p.y, bot.getLevel(), bot.getExp(),
                    bot.getMeso(), rewards.pickedDrops(), lastProgress, lastRestart, 0));
        }

        private void captureDead(Character bot, BotState previous, long now) {
            Point p = bot.getPosition();
            long deadSince = previous != null && previous.deadSince > 0 ? previous.deadSince : now;
            long lastProgress = previous == null ? now : previous.lastProgressAt;
            long lastRestart = previous == null ? 0 : previous.lastRestartAt;
            BotLootDriver.RewardStats rewards = BotLootDriver.rewardStats(bot);
            states.put(bot.getId(), new BotState(bot.getMapId(), p.x, p.y, bot.getLevel(), bot.getExp(),
                    bot.getMeso(), rewards.pickedDrops(), lastProgress, lastRestart, deadSince));
        }

        private void violation(String text) {
            violationCount++;
            if (violations.length() > 0) violations.append(',');
            if (violations.length() < 300) violations.append(text);
        }

        private Report report(boolean running, boolean cleanedUp, String reason) {
            long now = System.currentTimeMillis();
            return new Report(true, running, cleanedUp, expectedBotIds.size(), checks, restarts, violationCount,
                    startedAt, endsAt, Math.max(0, now - startedAt), reason,
                    violations.length() == 0 ? "none" : violations.toString());
        }
    }

    private record BotState(int mapId, int x, int y, int level, int exp, int mesos, int pickedDrops,
                            long lastProgressAt, long lastRestartAt, long deadSince) {}

    public record Report(boolean accepted, boolean running, boolean cleanedUp, int bots, long checks, int restarts,
                         int violations, long startedAt, long endsAt, long elapsedMs, String reason, String details) {
        static Report rejected(String reason) {
            return new Report(false, false, false, 0, 0, 0, 0, 0, 0, 0, reason, "none");
        }
    }
}
