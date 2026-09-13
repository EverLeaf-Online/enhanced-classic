package server;

import client.Character;
import config.YamlConfig;
import net.server.Server;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import tools.PacketCreator;

import java.awt.Point;
import java.awt.Rectangle;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

/**
 * EverLeaf server-side anti-cheat guardrails.
 *
 * <p>This intentionally does not autoban. High-confidence violations can
 * disconnect a player after repeated strikes while all detections are logged
 * and optionally surfaced to online GMs.</p>
 */
public final class AntiCheatService {
    private static final Logger log = LoggerFactory.getLogger(AntiCheatService.class);

    private static final long GM_ALERT_COOLDOWN_MS = 5_000L;
    private static final long HARD_STRIKE_WINDOW_MS = 30_000L;
    private static final int HARD_STRIKES_TO_KICK = 3;

    private static final int PLAYER_PICKUP_MAX_X = 260;
    private static final int PLAYER_PICKUP_MAX_Y = 220;
    private static final int PET_PICKUP_MAX_X = 320;
    private static final int PET_PICKUP_MAX_Y = 260;

    private static final int HARD_MOVE_X = 2_000;
    private static final int HARD_MOVE_Y = 1_400;
    private static final double HARD_MOVE_DISTANCE = 2_400.0;
    private static final double SUSPICIOUS_MOVE_SPEED = 4_500.0;

    private static final long RAPID_ATTACK_INTERVAL_MS = 45L;
    private static final int RAPID_ATTACK_BURST = 6;

    private static final Map<Integer, State> states = new ConcurrentHashMap<>();

    private AntiCheatService() {
    }

    public static void inspectMovement(Character chr, Point before, Point after) {
        if (!enabled(chr) || before == null || after == null) {
            return;
        }

        long now = Server.getInstance().getCurrentTime();
        State state = state(chr);
        long elapsed = state.lastMovementAt == 0L ? 0L : now - state.lastMovementAt;

        int dx = Math.abs(after.x - before.x);
        int dy = Math.abs(after.y - before.y);
        double distance = before.distance(after);

        Rectangle area = chr.getMap().getMapArea();
        if (area != null && area.width > 0 && area.height > 0) {
            Rectangle toleratedArea = new Rectangle(area);
            toleratedArea.grow(600, 600);
            if (!toleratedArea.contains(after)) {
                flag(chr, "MOVEMENT_BOUNDS",
                        "map=" + chr.getMapId() + " before=" + before + " after=" + after + " area=" + area,
                        false);
            }
        }

        if (dx > HARD_MOVE_X || dy > HARD_MOVE_Y || distance > HARD_MOVE_DISTANCE) {
            flag(chr, "MOVEMENT_TELEPORT",
                    "map=" + chr.getMapId() + " dx=" + dx + " dy=" + dy + " distance=" + Math.round(distance),
                    true);
        } else if (elapsed >= 20L && elapsed <= 2_000L && distance >= 220.0) {
            double speed = distance * 1_000.0 / elapsed;
            if (speed > SUSPICIOUS_MOVE_SPEED) {
                state.fastMovementBurst++;
                if (state.fastMovementBurst >= 4) {
                    flag(chr, "MOVEMENT_SPEED",
                            "map=" + chr.getMapId() + " speed=" + Math.round(speed) + "px/s elapsed=" + elapsed
                                    + "ms distance=" + Math.round(distance),
                            false);
                    state.fastMovementBurst = 0;
                }
            } else {
                state.fastMovementBurst = 0;
            }
        }

        state.lastMovementAt = now;
        state.lastSeenAt = now;
    }

    public static void inspectAttack(Character chr, int skillId, String attackType) {
        if (!enabled(chr)) {
            return;
        }

        long now = Server.getInstance().getCurrentTime();
        State state = state(chr);
        long elapsed = state.lastAttackAt == 0L ? Long.MAX_VALUE : now - state.lastAttackAt;

        if (elapsed >= 0L && elapsed < RAPID_ATTACK_INTERVAL_MS) {
            state.rapidAttackBurst++;
            if (state.rapidAttackBurst >= RAPID_ATTACK_BURST) {
                flag(chr, "FAST_ATTACK",
                        "type=" + attackType + " skill=" + skillId + " interval=" + elapsed + "ms",
                        true);
                state.rapidAttackBurst = 0;
            }
        } else {
            state.rapidAttackBurst = 0;
        }

        state.lastAttackAt = now;
        state.lastSeenAt = now;
    }

    public static boolean validatePickup(Character chr, Point collector, Point item, boolean petPickup) {
        if (!enabled(chr) || collector == null || item == null) {
            return true;
        }

        int maxX = petPickup ? PET_PICKUP_MAX_X : PLAYER_PICKUP_MAX_X;
        int maxY = petPickup ? PET_PICKUP_MAX_Y : PLAYER_PICKUP_MAX_Y;
        int dx = Math.abs(collector.x - item.x);
        int dy = Math.abs(collector.y - item.y);

        if (dx > maxX || dy > maxY) {
            flag(chr, petPickup ? "PET_ITEM_VAC" : "ITEM_VAC",
                    "map=" + chr.getMapId() + " collector=" + collector + " item=" + item
                            + " dx=" + dx + " dy=" + dy,
                    true);
            return false;
        }
        return true;
    }

    public static void flag(Character chr, String type, String detail, boolean hardViolation) {
        if (!enabled(chr)) {
            return;
        }

        long now = Server.getInstance().getCurrentTime();
        State state = state(chr);
        state.lastSeenAt = now;

        log.warn("AntiCheat type={} chr={} cid={} account={} map={} hard={} detail={}",
                type, chr.getName(), chr.getId(), chr.getAccountID(), chr.getMapId(), hardViolation, detail);

        if (YamlConfig.config.server.USE_ANTICHEAT_GM_ALERTS) {
            Long lastAlert = state.lastAlertAt.get(type);
            if (lastAlert == null || now - lastAlert >= GM_ALERT_COOLDOWN_MS) {
                state.lastAlertAt.put(type, now);
                Server.getInstance().broadcastGMMessage(chr.getWorld(),
                        PacketCreator.sendYellowTip("[AntiCheat] " + chr.getName() + " " + type + ": " + detail));
            }
        }

        if (hardViolation && YamlConfig.config.server.USE_ANTICHEAT_ENFORCE) {
            if (state.hardStrikeWindowStart == 0L || now - state.hardStrikeWindowStart > HARD_STRIKE_WINDOW_MS) {
                state.hardStrikeWindowStart = now;
                state.hardStrikes = 0;
            }

            state.hardStrikes++;
            if (state.hardStrikes >= HARD_STRIKES_TO_KICK) {
                log.warn("AntiCheat disconnect chr={} cid={} account={} after {} hard strikes in {}ms",
                        chr.getName(), chr.getId(), chr.getAccountID(), state.hardStrikes, HARD_STRIKE_WINDOW_MS);
                Server.getInstance().broadcastGMMessage(chr.getWorld(),
                        PacketCreator.sendYellowTip("[AntiCheat] Disconnecting " + chr.getName()
                                + " after repeated high-confidence violations."));
                state.hardStrikes = 0;
                state.hardStrikeWindowStart = now;
                if (chr.getClient() != null) {
                    chr.getClient().disconnect(false, false);
                }
            }
        }
    }

    private static boolean enabled(Character chr) {
        return chr != null
                && chr.getMap() != null
                && !chr.isGM()
                && YamlConfig.config.server.USE_ANTICHEAT;
    }

    private static State state(Character chr) {
        long now = Server.getInstance().getCurrentTime();
        State state = states.computeIfAbsent(chr.getId(), ignored -> new State());
        if (state.lastSeenAt != 0L && now - state.lastSeenAt > 10 * 60_000L) {
            state.resetTransient();
        }
        return state;
    }

    private static final class State {
        private long lastSeenAt;
        private long lastMovementAt;
        private long lastAttackAt;
        private int fastMovementBurst;
        private int rapidAttackBurst;
        private long hardStrikeWindowStart;
        private int hardStrikes;
        private final Map<String, Long> lastAlertAt = new ConcurrentHashMap<>();

        private void resetTransient() {
            lastMovementAt = 0L;
            lastAttackAt = 0L;
            fastMovementBurst = 0;
            rapidAttackBurst = 0;
            hardStrikeWindowStart = 0L;
            hardStrikes = 0;
            lastAlertAt.clear();
        }
    }
}
