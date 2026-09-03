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

/**
 * Controlled autonomous QA wrapper around SoloMapling's real GCMove + BotAttackSystem.
 *
 * <p>Besides the map-local hunt loop, this controller owns the Batch-4 lifecycle:
 * normal EverLeaf death/respawn, stale movement cleanup, return-to-training travel,
 * cross-map shop trips, return from restocking, route-failure recovery and conservative
 * level-aware map progression. GCTravel itself provides per-hop route recalculation,
 * portal retries, soft-lock detection and hard stuck recovery.</p>
 */
public final class BareBotHunter {
    private static final Logger log = LoggerFactory.getLogger(BareBotHunter.class);
    private static final long TICK_MS = 250;
    private static final int APPROACH_MARGIN = 20;
    private static final int PROGRESSION_LEVEL_STEP = 5;
    private static final long TRAVEL_RETRY_MS = 3_000L;
    private static final Map<Integer, Hunt> hunts = new ConcurrentHashMap<>();

    private BareBotHunter() {}

    public static boolean start(Character bot) {
        if (bot == null || bot.getMap() == null) return false;
        stop(bot);
        BareBotAutopilot.stop(bot);
        GCMovement.enable(bot);

        Hunt hunt = new Hunt(bot, bot.getMapId(), new Point(bot.getPosition()));
        ScheduledFuture<?> task = TimerManager.getInstance().register(hunt, TICK_MS, TICK_MS);
        hunt.task = task;
        hunts.put(bot.getId(), hunt);
        return true;
    }

    public static boolean start(Character bot, int ignoredDamage) {
        return start(bot);
    }

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

    public static boolean isHunting(Character bot) {
        return bot != null && hunts.containsKey(bot.getId());
    }

    public static String phase(Character bot) {
        Hunt hunt = bot == null ? null : hunts.get(bot.getId());
        return hunt == null ? "stopped" : hunt.phase.name().toLowerCase();
    }

    private enum Phase {
        HUNTING,
        RECOVERING,
        TO_SHOP,
        SHOPPING,
        RETURNING,
        PROGRESSING
    }

    private static final class Hunt implements Runnable {
        private final Character bot;
        private volatile int trainingMapId;
        private volatile Point trainingPosition;
        private volatile Phase phase = Phase.HUNTING;
        private volatile ScheduledFuture<?> task;
        private volatile int pendingTrainingMapId = -1;
        private int lastProgressionLevel;
        private long nextTravelRetryAt;
        private long lastFailureLogAt;

        private Hunt(Character bot, int mapId, Point position) {
            this.bot = bot;
            this.trainingMapId = mapId;
            this.trainingPosition = position;
            this.lastProgressionLevel = Math.max(1, bot.getLevel());
        }

        @Override
        public void run() {
            try {
                tick();
            } catch (Throwable t) {
                long now = System.currentTimeMillis();
                if (now - lastFailureLogAt >= 5_000L) {
                    lastFailureLogAt = now;
                    log.warn("SoloMapling QA hunter recovered from tick failure bot={} map={} phase={}",
                            bot == null ? -1 : bot.getId(), bot == null ? -1 : bot.getMapId(), phase, t);
                }
            }
        }

        private void tick() {
            if (bot.getMap() == null || !BotHelpers.isBot(bot)) {
                stop(bot);
                return;
            }

            if (!bot.isAlive()) {
                recoverFromDeath();
                return;
            }

            switch (phase) {
                case RECOVERING, RETURNING, TO_SHOP, PROGRESSING -> tickTravel();
                case SHOPPING -> tickShopping();
                case HUNTING -> tickHunting();
            }
        }

        private void recoverFromDeath() {
            if (phase == Phase.RECOVERING) return;
            phase = Phase.RECOVERING;
            stopTransientState();

            int returnMapId = bot.getMap().getReturnMapId();
            try {
                // Use the same Character.respawn path invoked by ChangeMapHandler for a dead real player.
                bot.respawn(returnMapId);
            } catch (RuntimeException e) {
                log.warn("SoloMapling QA death respawn failed bot={} returnMap={}", bot.getId(), returnMapId, e);
                nextTravelRetryAt = System.currentTimeMillis() + TRAVEL_RETRY_MS;
                return;
            }

            if (bot.isAlive()) {
                beginReturnToTraining(Phase.RETURNING);
            }
        }

        private void tickTravel() {
            if (!bot.isAlive()) return;
            if (phase == Phase.RECOVERING) {
                if (System.currentTimeMillis() >= nextTravelRetryAt) recoverFromDeath();
                return;
            }
            // GCTravel owns active route execution and recomputes from the live map every poll.
            if (GCMovement.isTraveling(bot)) return;

            if (phase == Phase.TO_SHOP) {
                phase = Phase.SHOPPING;
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
                } else if (pendingTrainingMapId > 0) {
                    retryTravel(pendingTrainingMapId, Phase.PROGRESSING);
                } else {
                    resumeHunting();
                }
            }
        }

        private void tickShopping() {
            BotShopDriver.RestockResult restock = BotShopDriver.tickRestock(bot);
            if (restock.active()) return;

            if ("stocked".equals(restock.reason())) {
                beginReturnToTraining(Phase.RETURNING);
                return;
            }

            if ("no-shop-on-map".equals(restock.reason()) || "shop-unavailable".equals(restock.reason())) {
                // A return map without a usable shop is not fatal. Resume the original scenario rather
                // than deadlocking the bot in town; diagnostics retain the failed restock reason.
                log.warn("SoloMapling QA restock trip found no usable shop bot={} map={} reason={}",
                        bot.getId(), bot.getMapId(), restock.reason());
                beginReturnToTraining(Phase.RETURNING);
                return;
            }

            // A shop attempted a transaction but could not satisfy it (mesos/inventory/etc.).
            // Those are valid QA outcomes, not infinite retry conditions.
            if (restock.attempted()) beginReturnToTraining(Phase.RETURNING);
        }

        private void tickHunting() {
            if (bot.getMapId() != trainingMapId) {
                beginReturnToTraining(Phase.RETURNING);
                return;
            }

            BotConsumableDriver.UseResult consumable = BotConsumableDriver.tick(bot);
            if (consumable.used()) return;

            BotBuffDriver.BuffResult buff = BotBuffDriver.tick(bot);
            if (buff.applied()) return;

            BotShopDriver.RestockResult restock = BotShopDriver.tickRestock(bot);
            if (restock.active()) return;
            if ("no-shop-on-map".equals(restock.reason())) {
                beginShopTrip();
                return;
            }

            if (bot.getLevel() >= lastProgressionLevel + PROGRESSION_LEVEL_STEP) {
                int target = BotTrainingMapSelector.select(bot, trainingMapId);
                lastProgressionLevel = bot.getLevel();
                if (target != trainingMapId) {
                    beginProgression(target);
                    return;
                }
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
                try {
                    GCMovement.move(bot, approachX, mobPos.y);
                } catch (RuntimeException ignored) {
                    // GCMove/GCTravel diagnostics retain navigation failures; later ticks recover.
                }
                return;
            }

            GCMovement.stop(bot);
            BotAttackDriver.botAttack(bot);
        }

        private void beginShopTrip() {
            int townMapId = bot.getMap().getReturnMapId();
            if (townMapId <= 0 || townMapId == bot.getMapId()) return;
            stopTransientState();
            phase = Phase.TO_SHOP;
            GCMovement.travel(bot, townMapId, ok -> {
                if (ok) phase = Phase.SHOPPING;
                else scheduleTravelRetry();
            });
        }

        private void beginProgression(int targetMapId) {
            stopTransientState();
            pendingTrainingMapId = targetMapId;
            phase = Phase.PROGRESSING;
            GCMovement.travel(bot, targetMapId, ok -> {
                if (!ok) scheduleTravelRetry();
            });
        }

        private void beginReturnToTraining(Phase returnPhase) {
            stopTransientState();
            phase = returnPhase;
            if (bot.getMapId() == trainingMapId) {
                if (trainingPosition != null) {
                    GCMovement.move(bot, trainingPosition.x, trainingPosition.y, this::resumeHunting);
                } else {
                    resumeHunting();
                }
                return;
            }
            GCMovement.travelTo(bot, trainingMapId,
                    trainingPosition == null ? 0 : trainingPosition.x,
                    trainingPosition == null ? 0 : trainingPosition.y,
                    ok -> {
                        if (ok) resumeHunting();
                        else scheduleTravelRetry();
                    });
        }

        private void retryTravel(int mapId, Phase travelPhase) {
            long now = System.currentTimeMillis();
            if (now < nextTravelRetryAt) return;
            nextTravelRetryAt = now + TRAVEL_RETRY_MS;
            phase = travelPhase;
            GCMovement.travel(bot, mapId, ok -> {
                if (!ok) scheduleTravelRetry();
            });
        }

        private void scheduleTravelRetry() {
            nextTravelRetryAt = System.currentTimeMillis() + TRAVEL_RETRY_MS;
            GCMovement.cancelTravel(bot);
        }

        private void resumeHunting() {
            if (!bot.isAlive() || bot.getMap() == null) return;
            phase = Phase.HUNTING;
            GCMovement.enable(bot);
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

    private static Monster nearestMonster(Character bot) {
        Point botPos = bot.getPosition();
        if (botPos == null) return null;
        return bot.getMap().getAllMonsters().stream()
                .filter(monster -> monster != null && monster.isAlive() && monster.getPosition() != null)
                .min(Comparator.comparingDouble(monster -> botPos.distanceSq(monster.getPosition())))
                .orElse(null);
    }
}
