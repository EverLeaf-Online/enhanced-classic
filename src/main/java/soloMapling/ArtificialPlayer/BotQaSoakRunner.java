package soloMapling.ArtificialPlayer;

import client.Character;
import server.TimerManager;

import java.awt.Point;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ScheduledFuture;

/**
 * Explicitly-started, bounded SoloMapling soak runner for live QA.
 *
 * <p>No session starts from server bootstrap or a scheduler. A GM must start a run through the
 * QA command surface. Each run owns one {@link BotQaFleet}, samples it every 30 seconds, records
 * progress/stall/death/recovery/runtime-memory signals, and removes every synthetic player when
 * the requested duration expires or the GM stops it.</p>
 */
public final class BotQaSoakRunner {
    private static final long OBSERVE_MS = 30_000L;
    private static final long STALL_MS = 180_000L;
    private static final Map<Integer, Session> activeByOwner = new ConcurrentHashMap<>();
    private static final Map<Integer, SoakStatus> finishedByOwner = new ConcurrentHashMap<>();

    private BotQaSoakRunner() {}

    public enum Preset {
        ONE_HOUR("1h", 60L * 60L * 1000L),
        SIX_HOURS("6h", 6L * 60L * 60L * 1000L),
        OVERNIGHT("overnight", 8L * 60L * 60L * 1000L);

        private final String token;
        private final long durationMs;

        Preset(String token, long durationMs) {
            this.token = token;
            this.durationMs = durationMs;
        }

        public String token() { return token; }
        public long durationMs() { return durationMs; }

        public static Preset parse(String value) {
            if (value == null) return null;
            return switch (value.toLowerCase()) {
                case "1h", "60m", "hour" -> ONE_HOUR;
                case "6h" -> SIX_HOURS;
                case "overnight", "8h" -> OVERNIGHT;
                default -> null;
            };
        }
    }

    public static synchronized SoakStatus start(int ownerId, int templateCharacterId, int count,
                                                int worldId, int channelId, int mapId, Preset preset) {
        if (preset == null) return SoakStatus.notFound("invalid-preset");
        if (count < 1 || count > BotQaFleet.MAX_BOTS_PER_FLEET) {
            return SoakStatus.notFound("count-must-be-1-to-" + BotQaFleet.MAX_BOTS_PER_FLEET);
        }

        Session prior = activeByOwner.remove(ownerId);
        if (prior != null) prior.finish("replaced", true);
        finishedByOwner.remove(ownerId);

        BotQaFleet.FleetResult fleetResult = BotQaFleet.spawn(
                ownerId, templateCharacterId, count, worldId, channelId, mapId);
        if (!fleetResult.success()) return SoakStatus.notFound("fleet-" + fleetResult.reason());

        List<Character> bots = new ArrayList<>(BotQaFleet.bots(ownerId));
        if (bots.size() != count) {
            BotQaFleet.remove(ownerId);
            return SoakStatus.notFound("fleet-count-mismatch");
        }

        int started = 0;
        for (Character bot : bots) {
            if (BareBotHunter.start(bot)) started++;
        }
        if (started != bots.size()) {
            for (Character bot : bots) BareBotHunter.stop(bot);
            BotQaFleet.remove(ownerId);
            return SoakStatus.notFound("hunter-start-failed-" + started + "-of-" + bots.size());
        }

        long now = System.currentTimeMillis();
        Session session = new Session(ownerId, preset, now, now + preset.durationMs(), bots);
        session.observe(now);
        session.task = TimerManager.getInstance().register(session, OBSERVE_MS, OBSERVE_MS);
        activeByOwner.put(ownerId, session);
        return session.snapshot(now, "started");
    }

    public static SoakStatus status(int ownerId) {
        Session session = activeByOwner.get(ownerId);
        if (session != null) return session.snapshot(System.currentTimeMillis(), "running");
        SoakStatus finished = finishedByOwner.get(ownerId);
        return finished != null ? finished : SoakStatus.notFound("no-soak");
    }

    public static synchronized SoakStatus stop(int ownerId) {
        Session session = activeByOwner.remove(ownerId);
        if (session == null) {
            SoakStatus finished = finishedByOwner.get(ownerId);
            return finished != null ? finished : SoakStatus.notFound("no-soak");
        }
        return session.finish("stopped", true);
    }

    public static boolean isRunning(int ownerId) {
        return activeByOwner.containsKey(ownerId);
    }

    private static final class Session implements Runnable {
        private final int ownerId;
        private final Preset preset;
        private final long startedAt;
        private final long endsAt;
        private final List<Character> bots;
        private final List<Integer> botIds;
        private final Map<Integer, BotSnapshot> previous = new HashMap<>();
        private final Map<Integer, Long> lastProgressAt = new HashMap<>();
        private final Set<Integer> stalled = new HashSet<>();
        private final Set<Integer> invariantFailures = new HashSet<>();
        private volatile ScheduledFuture<?> task;
        private volatile boolean running = true;
        private long observations;
        private long progressEvents;
        private long stallEvents;
        private long observedDeaths;
        private long observedRecoveries;
        private long errors;
        private long peakUsedMemoryBytes;
        private int cleanupClientLeaks;
        private int cleanupRegistrationLeaks;
        private String terminalReason = "running";

        private Session(int ownerId, Preset preset, long startedAt, long endsAt, List<Character> bots) {
            this.ownerId = ownerId;
            this.preset = preset;
            this.startedAt = startedAt;
            this.endsAt = endsAt;
            this.bots = List.copyOf(bots);
            this.botIds = bots.stream().map(Character::getId).toList();
        }

        @Override
        public void run() {
            long now = System.currentTimeMillis();
            try {
                observe(now);
                if (now >= endsAt) finish("completed", true);
            } catch (Throwable failure) {
                synchronized (this) { errors++; }
            }
        }

        private synchronized void observe(long now) {
            if (!running) return;
            observations++;
            long usedMemory = usedMemoryBytes();
            peakUsedMemoryBytes = Math.max(peakUsedMemoryBytes, usedMemory);

            for (Character bot : bots) {
                if (bot == null) {
                    errors++;
                    continue;
                }

                int id = bot.getId();
                BotSnapshot current = BotSnapshot.capture(bot);
                BotSnapshot old = previous.put(id, current);
                if (old == null) {
                    lastProgressAt.put(id, now);
                } else {
                    if (!old.progressKey().equals(current.progressKey())) {
                        progressEvents++;
                        lastProgressAt.put(id, now);
                        stalled.remove(id);
                    }
                    if (old.alive() && !current.alive()) observedDeaths++;
                    if (!old.alive() && current.alive()) observedRecoveries++;
                }

                long lastProgress = lastProgressAt.getOrDefault(id, startedAt);
                if (now - lastProgress >= STALL_MS && stalled.add(id)) stallEvents++;

                if ((BotClientHandler.getBotClient(id) == null || !BareBotFactory.isRegistered(id))
                        && invariantFailures.add(id)) {
                    errors++;
                }
            }
        }

        private synchronized SoakStatus finish(String reason, boolean cleanup) {
            if (!running) return snapshot(System.currentTimeMillis(), terminalReason);
            running = false;
            terminalReason = reason;
            ScheduledFuture<?> scheduled = task;
            if (scheduled != null) scheduled.cancel(false);

            if (cleanup) {
                try {
                    BotQaFleet.remove(ownerId);
                } catch (RuntimeException failure) {
                    errors++;
                }
                for (int botId : botIds) {
                    if (BotClientHandler.getBotClient(botId) != null) cleanupClientLeaks++;
                    if (BareBotFactory.isRegistered(botId)) cleanupRegistrationLeaks++;
                }
                if (cleanupClientLeaks > 0 || cleanupRegistrationLeaks > 0) errors++;
            }

            SoakStatus result = snapshot(System.currentTimeMillis(), reason);
            activeByOwner.remove(ownerId, this);
            finishedByOwner.put(ownerId, result);
            return result;
        }

        private synchronized SoakStatus snapshot(long now, String reason) {
            int alive = 0;
            int loggedIn = 0;
            int hunting = 0;
            for (Character bot : bots) {
                if (bot == null) continue;
                if (bot.isAlive()) alive++;
                if (bot.isLoggedinWorld()) loggedIn++;
                if (BareBotHunter.isHunting(bot)) hunting++;
            }
            long elapsed = Math.max(0L, now - startedAt);
            long remaining = running ? Math.max(0L, endsAt - now) : 0L;
            return new SoakStatus(true, running, preset.token(), bots.size(), elapsed, remaining,
                    observations, progressEvents, stallEvents, observedDeaths, observedRecoveries, errors,
                    usedMemoryBytes(), peakUsedMemoryBytes, alive, loggedIn, hunting,
                    cleanupClientLeaks, cleanupRegistrationLeaks, reason);
        }
    }

    private record BotSnapshot(int mapId, int x, int y, int level, int exp, int mesos, int hp, int mp,
                               boolean alive, boolean loggedIn, String phase) {
        static BotSnapshot capture(Character bot) {
            Point position = bot.getPosition();
            int x = position == null ? 0 : position.x;
            int y = position == null ? 0 : position.y;
            return new BotSnapshot(bot.getMapId(), x, y, bot.getLevel(), bot.getExp(), bot.getMeso(),
                    bot.getHp(), bot.getMp(), bot.isAlive(), bot.isLoggedinWorld(), BareBotHunter.phase(bot));
        }

        String progressKey() {
            return mapId + ":" + x + ":" + y + ":" + level + ":" + exp + ":" + mesos + ":"
                    + hp + ":" + mp + ":" + alive + ":" + loggedIn + ":" + phase;
        }
    }

    private static long usedMemoryBytes() {
        Runtime runtime = Runtime.getRuntime();
        return Math.max(0L, runtime.totalMemory() - runtime.freeMemory());
    }

    public record SoakStatus(boolean found, boolean running, String preset, int bots,
                             long elapsedMs, long remainingMs, long observations, long progressEvents,
                             long stallEvents, long observedDeaths, long observedRecoveries, long errors,
                             long usedMemoryBytes, long peakUsedMemoryBytes, int alive, int loggedInWorld,
                             int hunting, int cleanupClientLeaks, int cleanupRegistrationLeaks, String reason) {
        static SoakStatus notFound(String reason) {
            return new SoakStatus(false, false, "", 0, 0, 0, 0, 0, 0, 0, 0, 0,
                    usedMemoryBytes(), usedMemoryBytes(), 0, 0, 0, 0, 0, reason);
        }

        public boolean clean() {
            return errors == 0 && cleanupClientLeaks == 0 && cleanupRegistrationLeaks == 0;
        }
    }
}
