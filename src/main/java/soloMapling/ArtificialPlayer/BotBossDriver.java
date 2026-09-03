package soloMapling.ArtificialPlayer;

import client.Character;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import server.TimerManager;
import server.life.Monster;
import soloMapling.ArtificialPlayer.BotAttackSystem.BotAttackDriver;
import soloMapling.ArtificialPlayer.GCMoveSystem.GCMovement;

import java.awt.Point;
import java.util.Comparator;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ScheduledFuture;

/** Runs a bounded, server-authoritative boss encounter against a boss already present on the map. */
public final class BotBossDriver {
    private static final Logger log = LoggerFactory.getLogger(BotBossDriver.class);
    private static final long TICK_MS = 250L;
    private static final int APPROACH_MARGIN = 25;
    private static final long REENTRY_RETRY_MS = 3_000L;
    private static final Map<Integer, Encounter> encounters = new ConcurrentHashMap<>();

    private BotBossDriver() {}

    public static BossResult start(Character bot) {
        if (!eligible(bot)) return BossResult.fail("not-eligible");
        Monster boss = nearestBoss(bot);
        if (boss == null) return BossResult.fail("no-boss-on-map");
        stop(bot);
        BareBotHunter.stop(bot);
        BareBotAutopilot.stop(bot);
        GCMovement.enable(bot);
        Encounter encounter = new Encounter(bot, boss);
        encounter.task = TimerManager.getInstance().register(encounter, TICK_MS, TICK_MS);
        encounters.put(bot.getId(), encounter);
        return encounter.snapshot("started");
    }

    public static BossResult stop(Character bot) {
        if (bot == null) return BossResult.fail("not-eligible");
        Encounter encounter = encounters.remove(bot.getId());
        if (encounter == null) return BossResult.fail("not-running");
        encounter.cancel();
        encounter.stopTransient();
        return encounter.snapshot("stopped");
    }

    public static BossResult status(Character bot) {
        Encounter encounter = bot == null ? null : encounters.get(bot.getId());
        return encounter == null ? BossResult.fail("not-running") : encounter.snapshot("status");
    }

    public static boolean isRunning(Character bot) {
        return bot != null && encounters.containsKey(bot.getId());
    }

    private enum Phase { FIGHTING, REENTERING, LOOTING, COMPLETE, FAILED }

    private static final class Encounter implements Runnable {
        private final Character bot;
        private final int bossMapId;
        private final int bossObjectId;
        private final int bossMobId;
        private final Point bossAnchor;
        private volatile ScheduledFuture<?> task;
        private volatile Phase phase = Phase.FIGHTING;
        private long startedAt = System.currentTimeMillis();
        private long nextRetryAt;
        private long lootUntil;
        private int attacks;
        private int hits;
        private int deaths;
        private int reentries;
        private int consumables;
        private int buffs;
        private long lastFailureLogAt;

        private Encounter(Character bot, Monster boss) {
            this.bot = bot;
            bossMapId = bot.getMapId();
            bossObjectId = boss.getObjectId();
            bossMobId = boss.getId();
            bossAnchor = boss.getPosition() == null ? new Point(bot.getPosition()) : new Point(boss.getPosition());
        }

        @Override
        public void run() {
            try { tick(); }
            catch (Throwable t) {
                long now = System.currentTimeMillis();
                if (now - lastFailureLogAt >= 5_000L) {
                    lastFailureLogAt = now;
                    log.warn("SoloMapling boss QA tick recovered bot={} boss={} phase={}", bot.getId(), bossMobId, phase, t);
                }
            }
        }

        private void tick() {
            if (!eligibleWithoutAlive(bot)) { fail("bot-left-world"); return; }
            if (!bot.isAlive()) { recoverDeath(); return; }

            if (phase == Phase.REENTERING) {
                if (bot.getMapId() == bossMapId) {
                    reentries++;
                    phase = Phase.FIGHTING;
                    GCMovement.enable(bot);
                } else if (!GCMovement.isTraveling(bot) && System.currentTimeMillis() >= nextRetryAt) {
                    nextRetryAt = System.currentTimeMillis() + REENTRY_RETRY_MS;
                    GCMovement.travelTo(bot, bossMapId, bossAnchor.x, bossAnchor.y,
                            ok -> { if (!ok) nextRetryAt = System.currentTimeMillis() + REENTRY_RETRY_MS; });
                }
                return;
            }

            if (phase == Phase.LOOTING) {
                BotLootDriver.LootResult loot = BotLootDriver.tick(bot);
                if (!loot.found() && System.currentTimeMillis() >= lootUntil) complete();
                return;
            }
            if (phase == Phase.COMPLETE || phase == Phase.FAILED) return;

            if (bot.getMapId() != bossMapId) {
                phase = Phase.REENTERING;
                nextRetryAt = 0L;
                return;
            }

            Monster boss = findBoss(bot, bossObjectId, bossMobId);
            if (boss == null || !boss.isAlive()) {
                phase = Phase.LOOTING;
                lootUntil = System.currentTimeMillis() + 5_000L;
                BotAttackDriver.clearBot(bot.getId());
                GCMovement.stop(bot);
                return;
            }

            BotConsumableDriver.UseResult use = BotConsumableDriver.tick(bot);
            if (use.used()) { consumables++; return; }
            BotBuffDriver.BuffResult buff = BotBuffDriver.tick(bot);
            if (buff.applied()) { buffs++; return; }

            Point bp = bot.getPosition();
            Point mp = boss.getPosition();
            if (bp == null || mp == null) return;
            int reachX = Math.max(80, BotAttackDriver.attackReachX(bot));
            int reachY = Math.max(80, BotAttackDriver.attackReachY(bot));
            int dx = mp.x - bp.x;
            int dy = mp.y - bp.y;
            if (Math.abs(dx) > Math.max(1, reachX - APPROACH_MARGIN) || Math.abs(dy) > reachY + 300) {
                int offset = Math.max(30, reachX - APPROACH_MARGIN);
                GCMovement.move(bot, mp.x + (dx >= 0 ? -offset : offset), mp.y);
                return;
            }

            GCMovement.stop(bot);
            attacks++;
            BotAttackDriver.AttackResult result = BotAttackDriver.botAttack(bot);
            if (result.hit()) hits++;
        }

        private void recoverDeath() {
            deaths++;
            stopTransient();
            int returnMap = bot.getMap() == null ? -1 : bot.getMap().getReturnMapId();
            if (returnMap <= 0) { fail("no-return-map"); return; }
            try {
                bot.respawn(returnMap);
                phase = Phase.REENTERING;
                nextRetryAt = 0L;
            } catch (RuntimeException ex) {
                phase = Phase.REENTERING;
                nextRetryAt = System.currentTimeMillis() + REENTRY_RETRY_MS;
                log.warn("SoloMapling boss QA respawn failed bot={} returnMap={}", bot.getId(), returnMap, ex);
            }
        }

        private void complete() {
            phase = Phase.COMPLETE;
            cancel();
            stopTransient();
        }

        private void fail(String reason) {
            phase = Phase.FAILED;
            cancel();
            stopTransient();
            log.warn("SoloMapling boss QA encounter failed bot={} boss={} reason={}", bot.getId(), bossMobId, reason);
        }

        private void stopTransient() {
            GCMovement.disable(bot);
            BotAttackDriver.clearBot(bot.getId());
            BotLootDriver.clearBot(bot.getId());
            BotBuffDriver.clearBot(bot.getId());
            BotConsumableDriver.clearBot(bot.getId());
            BotNpcDriver.cancel(bot);
        }

        private void cancel() {
            ScheduledFuture<?> current = task;
            if (current != null) current.cancel(false);
        }

        private BossResult snapshot(String reason) {
            Monster boss = bot.getMapId() == bossMapId ? findBoss(bot, bossObjectId, bossMobId) : null;
            long hp = boss == null ? 0L : boss.getHp();
            return new BossResult(true, bossMobId, bossMapId, phase.name().toLowerCase(), hp, attacks, hits,
                    deaths, reentries, consumables, buffs, System.currentTimeMillis() - startedAt, reason);
        }
    }

    private static Monster nearestBoss(Character bot) {
        Point p = bot.getPosition();
        if (p == null) return null;
        return bot.getMap().getAllMonsters().stream()
                .filter(m -> m != null && m.isAlive() && m.isBoss() && m.getPosition() != null)
                .min(Comparator.comparingDouble(m -> p.distanceSq(m.getPosition())))
                .orElse(null);
    }

    private static Monster findBoss(Character bot, int objectId, int mobId) {
        if (bot == null || bot.getMap() == null) return null;
        return bot.getMap().getAllMonsters().stream()
                .filter(m -> m != null && m.isAlive() && m.isBoss())
                .filter(m -> m.getObjectId() == objectId || m.getId() == mobId)
                .findFirst().orElse(null);
    }

    private static boolean eligible(Character bot) {
        return eligibleWithoutAlive(bot) && bot.isAlive();
    }

    private static boolean eligibleWithoutAlive(Character bot) {
        return bot != null && BotHelpers.isBot(bot) && bot.getClient() != null && bot.isLoggedinWorld() && bot.getMap() != null;
    }

    public record BossResult(boolean success, int bossMobId, int bossMapId, String phase, long bossHp,
                             int attacks, int hits, int deaths, int reentries, int consumables, int buffs,
                             long elapsedMs, String reason) {
        static BossResult fail(String reason) {
            return new BossResult(false, 0, 0, "stopped", 0L, 0, 0, 0, 0, 0, 0, 0L, reason);
        }
    }
}
