package soloMapling.ArtificialPlayer;

import client.Character;
import server.TimerManager;
import server.life.Monster;
import soloMapling.ArtificialPlayer.BotCommandsPack.BotAttack;
import soloMapling.ArtificialPlayer.GCMoveSystem.GCMovement;

import java.awt.Point;
import java.util.Comparator;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ScheduledFuture;

/**
 * Controlled autonomous combat loop for the live QA bot.
 *
 * <p>This stitches together the already-vendored SoloMapling GCMove runtime and
 * SoloMapling attack-animation helper while keeping EverLeaf's existing monster
 * damage/kill/drop path authoritative. It deliberately stays on the current map;
 * portal/travel testing remains an explicit QA action.</p>
 */
public final class BareBotHunter {
    private static final long TICK_MS = 350;
    private static final long ATTACK_COOLDOWN_MS = 850;
    private static final double SEEK_DISTANCE_SQ = 1_400.0 * 1_400.0;
    private static final int ATTACK_X = 95;
    private static final int ATTACK_Y = 85;
    private static final int APPROACH_OFFSET = 55;
    private static final int DEFAULT_DAMAGE = 250;
    private static final Map<Integer, Hunt> hunts = new ConcurrentHashMap<>();

    private BareBotHunter() {
    }

    public static boolean start(Character bot) {
        return start(bot, DEFAULT_DAMAGE);
    }

    public static boolean start(Character bot, int damage) {
        if (bot == null || bot.getMap() == null || damage < 1 || damage > 1_000_000) {
            return false;
        }
        stop(bot);
        BareBotAutopilot.stop(bot);

        Hunt hunt = new Hunt(bot, damage, bot.getMapId());
        ScheduledFuture<?> task = TimerManager.getInstance().register(hunt, TICK_MS, TICK_MS);
        hunt.task = task;
        hunts.put(bot.getId(), hunt);
        return true;
    }

    public static boolean stop(Character bot) {
        if (bot == null) {
            return false;
        }
        Hunt hunt = hunts.remove(bot.getId());
        if (hunt == null) {
            return false;
        }
        hunt.cancel();
        GCMovement.disable(bot);
        return true;
    }

    public static boolean isHunting(Character bot) {
        return bot != null && hunts.containsKey(bot.getId());
    }

    private static final class Hunt implements Runnable {
        private final Character bot;
        private final int damage;
        private final int mapId;
        private volatile ScheduledFuture<?> task;
        private long nextAttackAt;

        private Hunt(Character bot, int damage, int mapId) {
            this.bot = bot;
            this.damage = damage;
            this.mapId = mapId;
        }

        @Override
        public void run() {
            if (bot.getMap() == null || bot.getMapId() != mapId || !BotHelpers.isBot(bot)) {
                stop(bot);
                return;
            }

            Monster target = nearestMonster(bot);
            if (target == null) {
                return;
            }

            Point botPos = bot.getPosition();
            Point mobPos = target.getPosition();
            if (botPos == null || mobPos == null) {
                return;
            }

            int dx = mobPos.x - botPos.x;
            int dy = mobPos.y - botPos.y;
            if (Math.abs(dx) > ATTACK_X || Math.abs(dy) > ATTACK_Y) {
                int approachX = mobPos.x + (dx >= 0 ? -APPROACH_OFFSET : APPROACH_OFFSET);
                try {
                    GCMovement.move(bot, approachX, mobPos.y);
                } catch (RuntimeException ignored) {
                    // GCMove diagnostics retain the actionable navigation failure; keep the hunt alive
                    // so a moving monster or a later graph warmup can recover naturally.
                }
                return;
            }

            boolean left = mobPos.x < botPos.x;
            if (GCMovement.isEnabled(bot)) {
                GCMovement.face(bot, left);
            }

            long now = System.currentTimeMillis();
            if (now < nextAttackAt) {
                return;
            }
            nextAttackAt = now + ATTACK_COOLDOWN_MS;

            BotAttack.basicSwing(bot);
            BareBotCombat.strikeNearest(bot, damage);
        }

        private void cancel() {
            ScheduledFuture<?> currentTask = task;
            if (currentTask != null) {
                currentTask.cancel(false);
            }
        }
    }

    private static Monster nearestMonster(Character bot) {
        Point botPos = bot.getPosition();
        if (botPos == null) {
            return null;
        }
        return bot.getMap().getAllMonsters().stream()
                .filter(monster -> monster != null && monster.getHp() > 0 && monster.getPosition() != null)
                .filter(monster -> botPos.distanceSq(monster.getPosition()) <= SEEK_DISTANCE_SQ)
                .min(Comparator.comparingDouble(monster -> botPos.distanceSq(monster.getPosition())))
                .orElse(null);
    }
}
