package soloMapling.ArtificialPlayer;

import client.Character;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import server.TimerManager;
import server.life.Monster;
import soloMapling.ArtificialPlayer.BotAttackSystem.BotAttackDriver;
import soloMapling.ArtificialPlayer.GCMoveSystem.BotTrainingMapSelector;
import soloMapling.ArtificialPlayer.GCMoveSystem.GCMovement;

import java.awt.Point;
import java.util.Comparator;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ScheduledFuture;

/** Controlled autonomous QA hunter with bounded death recovery, cross-map restocking and progression. */
public final class BareBotHunter {
    private static final Logger log = LoggerFactory.getLogger(BareBotHunter.class);
    private static final long TICK_MS = 250;
    private static final int APPROACH_MARGIN = 20;
    private static final int PROGRESSION_LEVEL_STEP = 5;
    private static final long TRAVEL_RETRY_MS = 3_000L;
    private static final int MAX_TRAVEL_ATTEMPTS = 5;
    private static final int MAX_RECOVERY_ATTEMPTS = 5;
    private static final int MAX_RESTOCK_FAILURES = 3;
    private static final int MAX_CONSECUTIVE_TICK_FAILURES = 5;
    private static final long MAX_NON_HUNTING_PHASE_MS = 120_000L;
    private static final Map<Integer, Hunt> hunts = new ConcurrentHashMap<>();
    private static final Map<Integer, String> lastFailureByBot = new ConcurrentHashMap<>();

    private BareBotHunter() {}

    public static boolean start(Character bot) {
        if (bot == null || bot.getMap() == null || bot.getPosition() == null) return false;
        stop(bot);
        lastFailureByBot.remove(bot.getId());
        BareBotAutopilot.stop(bot);
        GCMovement.enable(bot);
        Hunt hunt = new Hunt(bot, bot.getMapId(), new Point(bot.getPosition()));
        hunt.task = TimerManager.getInstance().register(hunt, TICK_MS, TICK_MS);
        hunts.put(bot.getId(), hunt);
        return true;
    }

    public static boolean start(Character bot, int ignoredDamage) { return start(bot); }

    public static boolean stop(Character bot) {
        if (bot == null) return false;
        Hunt hunt = hunts.remove(bot.getId());
        if (hunt == null) return false;
        hunt.cancel();
        GCMovement.disable(bot);
        BotAttackDriver.clearBot(bot.getId());
        BotLootDriver.clearBot(bot.getId());
        BotBuffDriver.clearBot(bot.getId());
        BotConsumableDriver.clearBot(bot.getId());
        BotNpcDriver.cancel(bot);
        return true;
    }

    public static boolean isHunting(Character bot) { return bot != null && hunts.containsKey(bot.getId()); }

    public static String phase(Character bot) {
        Hunt hunt = bot == null ? null : hunts.get(bot.getId());
        return hunt == null ? "stopped" : hunt.phase.name().toLowerCase();
    }

    public static String failureReason(Character bot) {
        return bot == null ? null : lastFailureByBot.get(bot.getId());
    }

    public static void clearFailure(int botId) {
        lastFailureByBot.remove(botId);
    }

    private enum Phase { HUNTING, RECOVERING, TO_SHOP, SHOPPING, RETURNING, PROGRESSING }

    private static final class Hunt implements Runnable {
        private final Character bot;
        private volatile int trainingMapId;
        private volatile Point trainingPosition;
        private volatile Phase phase = Phase.HUNTING;
        private volatile ScheduledFuture<?> task;
        private volatile int pendingTrainingMapId = -1;
        private volatile int shopMapId = -1;
        private int lastProgressionLevel;
        private int travelAttempts;
        private int recoveryAttempts;
        private int restockFailures;
        private int consecutiveTickFailures;
        private long phaseStartedAt = System.currentTimeMillis();
        private long nextTravelRetryAt;
        private long lastFailureLogAt;

        private Hunt(Character bot, int mapId, Point position) {
            this.bot = bot;
            trainingMapId = mapId;
            trainingPosition = position;
            lastProgressionLevel = Math.max(1, bot.getLevel());
        }

        @Override
        public void run() {
            try {
                tick();
                consecutiveTickFailures = 0;
            } catch (Throwable t) {
                consecutiveTickFailures++;
                long now = System.currentTimeMillis();
                if (now - lastFailureLogAt >= 5_000L) {
                    lastFailureLogAt = now;
                    log.warn("SoloMapling QA hunter tick failure bot={} map={} phase={} consecutive={} location={}",
                            bot == null ? -1 : bot.getId(), bot == null ? -1 : bot.getMapId(), phase,
                            consecutiveTickFailures, failureLocation(t), t);
                }
                if (consecutiveTickFailures >= MAX_CONSECUTIVE_TICK_FAILURES) {
                    failClosed("tick-exception-threshold:" + t.getClass().getSimpleName() + "@" + failureLocation(t));
                }
            }
        }

        private void tick() {
            if (bot.getMap() == null || !BotHelpers.isBot(bot)) { failClosed("bot-left-valid-runtime"); return; }
            if (phase != Phase.HUNTING && System.currentTimeMillis() - phaseStartedAt > MAX_NON_HUNTING_PHASE_MS) {
                failClosed("phase-timeout:" + phase.name().toLowerCase());
                return;
            }
            if (!bot.isAlive()) { recoverFromDeath(); return; }
            switch (phase) {
                case RECOVERING, RETURNING, TO_SHOP, PROGRESSING -> tickTravel();
                case SHOPPING -> tickShopping();
                case HUNTING -> tickHunting();
            }
        }

        private void recoverFromDeath() {
            long now = System.currentTimeMillis();
            if (phase != Phase.RECOVERING) {
                enterPhase(Phase.RECOVERING);
                recoveryAttempts = 0;
            }
            if (now < nextTravelRetryAt) return;
            if (++recoveryAttempts > MAX_RECOVERY_ATTEMPTS) {
                failClosed("death-recovery-attempts-exhausted");
                return;
            }

            stopTransientState();
            int returnMapId = bot.getMap().getReturnMapId();
            try {
                bot.respawn(returnMapId); // same normal Character path used by ChangeMapHandler
            } catch (RuntimeException e) {
                log.warn("SoloMapling QA death respawn failed bot={} returnMap={} attempt={}",
                        bot.getId(), returnMapId, recoveryAttempts, e);
                nextTravelRetryAt = now + TRAVEL_RETRY_MS;
                return;
            }
            if (bot.isAlive()) beginReturnToTraining();
            else nextTravelRetryAt = now + TRAVEL_RETRY_MS;
        }

        private void tickTravel() {
            if (!bot.isAlive()) return;
            if (GCMovement.isTraveling(bot)) return;
            long now = System.currentTimeMillis();
            if (phase == Phase.RECOVERING) {
                if (now >= nextTravelRetryAt) recoverFromDeath();
                return;
            }
            if (phase == Phase.TO_SHOP) {
                if (shopMapId > 0 && bot.getMapId() == shopMapId) enterPhase(Phase.SHOPPING);
                else if (shopMapId > 0) retryTravel(shopMapId, Phase.TO_SHOP);
                else beginReturnToTraining();
                return;
            }
            if (phase == Phase.RETURNING) {
                if (bot.getMapId() == trainingMapId) resumeHunting();
                else retryTravel(trainingMapId, Phase.RETURNING);
                return;
            }
            if (phase == Phase.PROGRESSING) {
                if (pendingTrainingMapId > 0 && bot.getMapId() == pendingTrainingMapId) {
                    trainingMapId = pendingTrainingMapId;
                    trainingPosition = new Point(bot.getPosition());
                    pendingTrainingMapId = -1;
                    lastProgressionLevel = Math.max(lastProgressionLevel, bot.getLevel());
                    resumeHunting();
                } else if (pendingTrainingMapId > 0) retryTravel(pendingTrainingMapId, Phase.PROGRESSING);
                else resumeHunting();
            }
        }

        private void tickShopping() {
            BotShopDriver.RestockResult restock = BotShopDriver.tickRestock(bot);
            if (restock.active()) return;
            if ("stocked".equals(restock.reason())) {
                restockFailures = 0;
                beginReturnToTraining();
                return;
            }
            if ("no-shop-on-map".equals(restock.reason()) || "shop-unavailable".equals(restock.reason())
                    || "shop-could-not-restock".equals(restock.reason())) {
                if (++restockFailures >= MAX_RESTOCK_FAILURES) {
                    failClosed("restock-failures-exhausted:" + restock.reason());
                    return;
                }
                log.warn("SoloMapling QA restock trip failed bot={} map={} reason={} attempt={}",
                        bot.getId(), bot.getMapId(), restock.reason(), restockFailures);
                beginReturnToTraining();
                return;
            }
            if (restock.attempted()) {
                restockFailures = 0;
                beginReturnToTraining();
            }
        }

        private void tickHunting() {
            if (bot.getMapId() != trainingMapId) { beginReturnToTraining(); return; }

            BotConsumableDriver.UseResult consumable = BotConsumableDriver.tick(bot);
            if (consumable.used()) return;
            BotBuffDriver.BuffResult buff = BotBuffDriver.tick(bot);
            if (buff.applied()) return;

            BotShopDriver.RestockResult restock = BotShopDriver.tickRestock(bot);
            if (restock.active()) return;
            if ("no-shop-on-map".equals(restock.reason())) { beginShopTrip(); return; }

            if (bot.getLevel() >= lastProgressionLevel + PROGRESSION_LEVEL_STEP) {
                int target = BotTrainingMapSelector.select(bot, trainingMapId);
                lastProgressionLevel = bot.getLevel();
                if (target != trainingMapId) { beginProgression(target); return; }
            }

            BotLootDriver.LootResult loot = BotLootDriver.tick(bot);
            if (loot.found()) return;
            Monster target = nearestMonster(bot);
            if (target == null || target.getPosition() == null || bot.getPosition() == null) return;

            Point botPos = bot.getPosition();
            Point mobPos = target.getPosition();
            int reachX = Math.max(70, BotAttackDriver.attackReachX(bot));
            int reachY = Math.max(60, BotAttackDriver.attackReachY(bot));
            int dx = mobPos.x - botPos.x;
            int dy = mobPos.y - botPos.y;
            if (Math.abs(dx) > Math.max(1, reachX - APPROACH_MARGIN) || Math.abs(dy) > reachY) {
                int offset = Math.max(25, reachX - APPROACH_MARGIN);
                int approachX = mobPos.x + (dx >= 0 ? -offset : offset);
                try { GCMovement.move(bot, approachX, mobPos.y); }
                catch (RuntimeException ignored) { }
                return;
            }
            GCMovement.stop(bot);
            BotAttackDriver.botAttack(bot);
        }

        private void beginShopTrip() {
            int destinationMapId = BotShopMapSelector.select(bot);
            if (destinationMapId <= 0) {
                if (++restockFailures >= MAX_RESTOCK_FAILURES) {
                    failClosed("shop-destination-unavailable");
                    return;
                }
                log.warn("SoloMapling QA could not resolve restock destination bot={} map={} attempt={}",
                        bot.getId(), bot.getMapId(), restockFailures);
                return;
            }
            if (destinationMapId == bot.getMapId()) {
                enterPhase(Phase.SHOPPING);
                return;
            }
            stopTransientState();
            shopMapId = destinationMapId;
            startTravel(shopMapId, Phase.TO_SHOP);
        }

        private void beginProgression(int targetMapId) {
            stopTransientState();
            pendingTrainingMapId = targetMapId;
            startTravel(targetMapId, Phase.PROGRESSING);
        }

        private void beginReturnToTraining() {
            stopTransientState();
            shopMapId = -1;
            enterPhase(Phase.RETURNING);
            travelAttempts = 0;
            if (bot.getMapId() == trainingMapId) {
                if (trainingPosition != null) GCMovement.move(bot, trainingPosition.x, trainingPosition.y, this::resumeHunting);
                else resumeHunting();
                return;
            }
            startTravelToTraining();
        }

        private void startTravelToTraining() {
            if (!nextTravelAttempt()) return;
            if (trainingPosition == null) {
                GCMovement.travel(bot, trainingMapId,
                        ok -> { if (ok) resumeHunting(); else scheduleTravelRetry(); });
            } else {
                GCMovement.travelTo(bot, trainingMapId, trainingPosition.x, trainingPosition.y,
                        ok -> { if (ok) resumeHunting(); else scheduleTravelRetry(); });
            }
        }

        private void startTravel(int mapId, Phase travelPhase) {
            if (phase != travelPhase) {
                enterPhase(travelPhase);
                travelAttempts = 0;
            }
            if (!nextTravelAttempt()) return;
            GCMovement.travel(bot, mapId, ok -> { if (!ok) scheduleTravelRetry(); });
        }

        private boolean nextTravelAttempt() {
            if (++travelAttempts > MAX_TRAVEL_ATTEMPTS) {
                failClosed("travel-attempts-exhausted:" + phase.name().toLowerCase());
                return false;
            }
            return true;
        }

        private void retryTravel(int mapId, Phase travelPhase) {
            long now = System.currentTimeMillis();
            if (now < nextTravelRetryAt) return;
            nextTravelRetryAt = now + TRAVEL_RETRY_MS;
            if (travelPhase == Phase.RETURNING) startTravelToTraining();
            else startTravel(mapId, travelPhase);
        }

        private void scheduleTravelRetry() {
            nextTravelRetryAt = System.currentTimeMillis() + TRAVEL_RETRY_MS;
            GCMovement.cancelTravel(bot);
        }

        private void resumeHunting() {
            if (!bot.isAlive() || bot.getMap() == null) return;
            enterPhase(Phase.HUNTING);
            travelAttempts = 0;
            recoveryAttempts = 0;
            GCMovement.enable(bot);
        }

        private void enterPhase(Phase next) {
            if (phase != next) {
                phase = next;
                phaseStartedAt = System.currentTimeMillis();
            }
        }

        private void failClosed(String reason) {
            if (bot == null) return;
            lastFailureByBot.put(bot.getId(), reason);
            log.error("SoloMapling QA hunter failed closed bot={} map={} phase={} reason={}",
                    bot.getId(), bot.getMapId(), phase, reason);
            Hunt removed = hunts.remove(bot.getId());
            if (removed != null) removed.cancel();
            stopTransientState();
            try { GCMovement.disable(bot); } catch (RuntimeException ignored) { }
        }

        private void stopTransientState() {
            BareBotAutopilot.stop(bot);
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
    }

    private static String failureLocation(Throwable t) {
        if (t == null) return "unknown";
        for (StackTraceElement frame : t.getStackTrace()) {
            String className = frame.getClassName();
            if (className.startsWith("soloMapling.") || className.startsWith("server.") || className.startsWith("client.")) {
                return className + "." + frame.getMethodName() + ":" + frame.getLineNumber();
            }
        }
        StackTraceElement[] frames = t.getStackTrace();
        if (frames.length == 0) return "unknown";
        StackTraceElement frame = frames[0];
        return frame.getClassName() + "." + frame.getMethodName() + ":" + frame.getLineNumber();
    }

    private static Monster nearestMonster(Character bot) {
        Point botPos = bot.getPosition();
        if (botPos == null || bot.getMap() == null) return null;
        return bot.getMap().getAllMonsters().stream()
                .filter(monster -> monster != null && monster.isAlive() && monster.getPosition() != null)
                .min(Comparator.comparingDouble(monster -> botPos.distanceSq(monster.getPosition())))
                .orElse(null);
    }
}
