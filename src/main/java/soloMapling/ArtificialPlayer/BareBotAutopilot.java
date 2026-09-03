package soloMapling.ArtificialPlayer;

import client.Character;
import server.TimerManager;
import server.maps.Foothold;
import tools.exceptions.EmptyMovementException;

import java.awt.Point;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ScheduledFuture;

/**
 * Bounded unattended movement smoke test.
 *
 * <p>This is not a replacement for SoloMapling GCMove. It gives the staged
 * integration a safe autonomous workload while the full graph/physics package
 * is reconciled: walk back and forth on the current foothold only, never use a
 * portal, never change maps, and stop automatically if the bot disappears.</p>
 */
public final class BareBotAutopilot {
    private static final long TICK_MS = 750;
    private static final int STEP_PX = 28;
    private static final int EDGE_MARGIN_PX = 12;
    private static final Map<Integer, Patrol> patrols = new ConcurrentHashMap<>();

    private BareBotAutopilot() {
    }

    public static boolean startPatrol(Character bot) {
        if (bot == null || bot.getMap() == null) {
            return false;
        }
        stop(bot);

        Patrol patrol = new Patrol(bot);
        ScheduledFuture<?> task = TimerManager.getInstance().register(patrol, TICK_MS, TICK_MS);
        patrol.task = task;
        patrols.put(bot.getId(), patrol);
        return true;
    }

    public static boolean stop(Character bot) {
        if (bot == null) {
            return false;
        }
        Patrol patrol = patrols.remove(bot.getId());
        if (patrol == null) {
            return false;
        }
        patrol.cancel();
        return true;
    }

    public static boolean isPatrolling(Character bot) {
        return bot != null && patrols.containsKey(bot.getId());
    }

    private static final class Patrol implements Runnable {
        private final Character bot;
        private int direction = 1;
        private volatile ScheduledFuture<?> task;

        private Patrol(Character bot) {
            this.bot = bot;
        }

        @Override
        public void run() {
            if (bot.getMap() == null || !BotHelpers.isBot(bot)) {
                stop(bot);
                return;
            }

            Point current = bot.getPosition();
            Foothold foothold = bot.getMap().getFootholds().findBelow(new Point(current.x, current.y - 1));
            if (foothold == null || foothold.isWall()) {
                stop(bot);
                return;
            }

            int left = Math.min(foothold.getX1(), foothold.getX2()) + EDGE_MARGIN_PX;
            int right = Math.max(foothold.getX1(), foothold.getX2()) - EDGE_MARGIN_PX;
            if (right <= left) {
                stop(bot);
                return;
            }

            int nextX = current.x + direction * STEP_PX;
            if (nextX >= right) {
                nextX = right;
                direction = -1;
            } else if (nextX <= left) {
                nextX = left;
                direction = 1;
            }

            int nextY = interpolateY(foothold, nextX);
            try {
                BareBotMovement.moveTo(bot, new Point(nextX, nextY));
            } catch (EmptyMovementException | RuntimeException e) {
                stop(bot);
            }
        }

        private void cancel() {
            ScheduledFuture<?> currentTask = task;
            if (currentTask != null) {
                currentTask.cancel(false);
            }
        }
    }

    private static int interpolateY(Foothold foothold, int x) {
        int dx = foothold.getX2() - foothold.getX1();
        if (dx == 0) {
            return Math.max(foothold.getY1(), foothold.getY2());
        }
        double t = (x - foothold.getX1()) / (double) dx;
        return (int) Math.round(foothold.getY1() + t * (foothold.getY2() - foothold.getY1()));
    }
}
