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

/**
 * Controlled autonomous QA wrapper around SoloMapling's real GCMove + BotAttackSystem.
 * It selects/chases targets, loots EverLeaf-owned drops, and keeps running through
 * transient failures; class/weapon attack selection, visible attack packets,
 * cooldowns and damage are delegated to BotAttackDriver.
 */
public final class BareBotHunter {
    private static final Logger log = LoggerFactory.getLogger(BareBotHunter.class);
    private static final long TICK_MS = 250;
    private static final int APPROACH_MARGIN = 20;
    private static final Map<Integer, Hunt> hunts = new ConcurrentHashMap<>();

    private BareBotHunter() {}

    public static boolean start(Character bot) {
        if (bot == null || bot.getMap() == null) return false;
        stop(bot);
        BareBotAutopilot.stop(bot);
        GCMovement.enable(bot);

        Hunt hunt = new Hunt(bot, bot.getMapId());
        ScheduledFuture<?> task = TimerManager.getInstance().register(hunt, TICK_MS, TICK_MS);
        hunt.task = task;
        hunts.put(bot.getId(), hunt);
        return true;
    }

    /** Compatibility overload for the earlier fixed-damage QA command. */
    public static boolean start(Character bot, int ignoredDamage) {
        return start(bot);
    }

    public static boolean stop(Character bot) {
        if (bot == null) return false;
        Hunt hunt = hunts.remove(bot.getId());
        if (hunt == null) return false;
        hunt.cancel();
        GCMovement.stop(bot);
        BotAttackDriver.clearBot(bot.getId());
        BotLootDriver.clearBot(bot.getId());
        return true;
    }

    public static boolean isHunting(Character bot) {
        return bot != null && hunts.containsKey(bot.getId());
    }

    private static final class Hunt implements Runnable {
        private final Character bot;
        private final int mapId;
        private volatile ScheduledFuture<?> task;
        private long lastFailureLogAt;

        private Hunt(Character bot, int mapId) {
            this.bot = bot;
            this.mapId = mapId;
        }

        @Override
        public void run() {
            try {
                tick();
            } catch (Throwable t) {
                // ScheduledExecutorService suppresses every future execution after an
                // uncaught exception. A transient navigation/combat/loot failure must
                // never permanently kill an active QA hunt session.
                long now = System.currentTimeMillis();
                if (now - lastFailureLogAt >= 5_000L) {
                    lastFailureLogAt = now;
                    log.warn("SoloMapling QA hunter recovered from tick failure bot={} map={}",
                            bot == null ? -1 : bot.getId(), mapId, t);
                }
            }
        }

        private void tick() {
            if (bot.getMap() == null || bot.getMapId() != mapId || !BotHelpers.isBot(bot)) {
                stop(bot);
                return;
            }

            // Loot bot-owned drops before acquiring another target. The loot driver
            // delegates the transaction to Character.pickupItem(), so EverLeaf's
            // normal ownership/inventory/quest/meso checks remain authoritative.
            BotLootDriver.LootResult loot = BotLootDriver.tick(bot);
            if (loot.found()) {
                return;
            }

            Monster target = nearestMonster(bot);
            if (target == null || target.getPosition() == null || bot.getPosition() == null) {
                // Keep the scheduled hunt alive while a map is temporarily empty so
                // respawns can be acquired without issuing !qabot hunt start again.
                return;
            }

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
                    // GCMove diagnostics retain navigation failures; later ticks may recover.
                }
                return;
            }

            GCMovement.stop(bot);
            BotAttackDriver.botAttack(bot);
        }

        private void cancel() {
            ScheduledFuture<?> current = task;
            if (current != null) current.cancel(false);
        }
    }

    private static Monster nearestMonster(Character bot) {
        Point botPos = bot.getPosition();
        if (botPos == null) return null;

        // Do not impose a short seek radius here. On sparse or partially cleared maps,
        // the nearest living target may be across the map; GCMove is responsible for
        // deciding how to traverse toward it. Keeping acquisition map-wide prevents a
        // healthy hunt session from appearing to stop after clearing a local cluster.
        return bot.getMap().getAllMonsters().stream()
                .filter(monster -> monster != null && monster.isAlive() && monster.getPosition() != null)
                .min(Comparator.comparingDouble(monster -> botPos.distanceSq(monster.getPosition())))
                .orElse(null);
    }
}
