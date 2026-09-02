package soloMapling.ArtificialPlayer;

import client.Character;
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
 * It selects/chases targets; class/weapon attack selection, visible attack packets,
 * cooldowns and damage are delegated to BotAttackDriver.
 */
public final class BareBotHunter {
    private static final long TICK_MS = 250;
    private static final double SEEK_DISTANCE_SQ = 1_400.0 * 1_400.0;
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
        return true;
    }

    public static boolean isHunting(Character bot) {
        return bot != null && hunts.containsKey(bot.getId());
    }

    private static final class Hunt implements Runnable {
        private final Character bot;
        private final int mapId;
        private volatile ScheduledFuture<?> task;

        private Hunt(Character bot, int mapId) {
            this.bot = bot;
            this.mapId = mapId;
        }

        @Override
        public void run() {
            if (bot.getMap() == null || bot.getMapId() != mapId || !BotHelpers.isBot(bot)) {
                stop(bot);
                return;
            }

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
        return bot.getMap().getAllMonsters().stream()
                .filter(monster -> monster != null && monster.isAlive() && monster.getPosition() != null)
                .filter(monster -> botPos.distanceSq(monster.getPosition()) <= SEEK_DISTANCE_SQ)
                .min(Comparator.comparingDouble(monster -> botPos.distanceSq(monster.getPosition())))
                .orElse(null);
    }
}
