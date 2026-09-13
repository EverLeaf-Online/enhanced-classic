package server;

import client.Character;
import client.Client;
import config.YamlConfig;
import constants.game.GameConstants;
import net.server.Server;
import tools.PacketCreator;

import java.awt.Point;
import java.awt.Rectangle;
import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Deque;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/** EverLeaf server-side anti-cheat and exploit guardrails. */
public final class AntiCheatService {
    private static final Logger log = LoggerFactory.getLogger(AntiCheatService.class);
    private static final long GM_ALERT_COOLDOWN_MS = 5_000L;
    private static final long HARD_STRIKE_WINDOW_MS = 30_000L;
    private static final int HARD_STRIKES_TO_KICK = 3;
    private static final int MAX_RECENT_EVIDENCE = 16;
    private static final int PLAYER_PICKUP_MAX_X = 260;
    private static final int PLAYER_PICKUP_MAX_Y = 220;
    private static final int PET_PICKUP_MAX_X = 320;
    private static final int PET_PICKUP_MAX_Y = 260;
    private static final int HARD_MOVE_X = 2_000;
    private static final int HARD_MOVE_Y = 1_400;
    private static final double HARD_MOVE_DISTANCE = 2_400.0;
    private static final double SUSPICIOUS_MOVE_SPEED = 4_500.0;
    private static final double HARD_MOB_MOVE_DISTANCE = 3_000.0;
    private static final double SUSPICIOUS_MOB_MOVE_DISTANCE = 1_300.0;
    private static final long RAPID_ATTACK_INTERVAL_MS = 45L;
    private static final int RAPID_ATTACK_BURST = 6;
    private static final long PACKET_WINDOW_MS = 1_000L;
    private static final long PACKET_LONG_WINDOW_MS = 10_000L;
    private static final int PACKET_SOFT_LIMIT = 180;
    private static final int PACKET_HARD_LIMIT = 320;
    private static final int PACKET_LONG_HARD_LIMIT = 2_000;
    private static final int MAX_PACKET_BYTES = 512 * 1024;
    private static final Map<Integer, State> states = new ConcurrentHashMap<>();

    private AntiCheatService() {}

    public static boolean inspectPacket(Client client, short opcode, String handlerName, int remainingBytes) {
        Character chr = client == null ? null : client.getPlayer();
        if (!enabled(chr)) return true;
        if (remainingBytes < 0 || remainingBytes > MAX_PACKET_BYTES) {
            flag(chr, "PACKET_SIZE", "opcode=" + opcode + " handler=" + handlerName + " bytes=" + remainingBytes, true);
            return false;
        }
        long now = now();
        State state = state(chr);
        if (state.packetWindowStart == 0L || now - state.packetWindowStart >= PACKET_WINDOW_MS) {
            state.packetWindowStart = now; state.packetCount = 0; state.packetSoftAlerted = false;
        }
        if (state.packetLongWindowStart == 0L || now - state.packetLongWindowStart >= PACKET_LONG_WINDOW_MS) {
            state.packetLongWindowStart = now; state.packetLongCount = 0;
        }
        state.packetCount++;
        state.packetLongCount++;
        if (state.packetCount > PACKET_SOFT_LIMIT && !state.packetSoftAlerted) {
            state.packetSoftAlerted = true;
            flag(chr, "PACKET_FLOOD", "opcode=" + opcode + " handler=" + handlerName + " rate=" + state.packetCount + "/s", false);
        }
        if (state.packetCount > PACKET_HARD_LIMIT || state.packetLongCount > PACKET_LONG_HARD_LIMIT) {
            flag(chr, "PACKET_FLOOD_HARD", "opcode=" + opcode + " handler=" + handlerName + " short=" + state.packetCount + " long=" + state.packetLongCount, true);
            return false;
        }
        int[] limits = sensitivePacketLimits(handlerName);
        if (limits != null && !guardSensitiveAction(chr, "PKT_" + handlerName, limits[0], limits[1])) return false;
        state.lastSeenAt = now;
        return true;
    }

    public static void inspectUnknownPacket(Client client, short opcode, int remainingBytes) {
        Character chr = client == null ? null : client.getPlayer();
        if (!enabled(chr)) return;
        State state = state(chr);
        long now = now();
        if (state.unknownWindowStart == 0L || now - state.unknownWindowStart > 10_000L) {
            state.unknownWindowStart = now; state.unknownCount = 0;
        }
        state.unknownCount++;
        if (state.unknownCount == 4) flag(chr, "UNKNOWN_PACKET", "opcode=" + opcode + " bytes=" + remainingBytes + " count=" + state.unknownCount, false);
        else if (state.unknownCount >= 10) flag(chr, "UNKNOWN_PACKET_FLOOD", "opcode=" + opcode + " bytes=" + remainingBytes + " count=" + state.unknownCount, true);
    }

    public static boolean guardSensitiveAction(Character chr, String action, int softPerSecond, int hardPerSecond) {
        if (!enabled(chr)) return true;
        State state = state(chr);
        long now = now();
        synchronized (state.actionWindows) {
            WindowCounter counter = state.actionWindows.computeIfAbsent(action, ignored -> new WindowCounter());
            if (counter.startedAt == 0L || now - counter.startedAt >= 1_000L) {
                counter.startedAt = now; counter.count = 0; counter.softAlerted = false;
            }
            counter.count++;
            if (counter.count > softPerSecond && !counter.softAlerted) {
                counter.softAlerted = true;
                flag(chr, "ACTION_RATE", "action=" + action + " count=" + counter.count + "/s", false);
            }
            if (counter.count > hardPerSecond) {
                flag(chr, "ACTION_RATE_HARD", "action=" + action + " count=" + counter.count + "/s", true);
                return false;
            }
            return counter.count <= softPerSecond;
        }
    }

    public static void inspectMovement(Character chr, Point before, Point after) {
        if (!enabled(chr) || before == null || after == null) return;
        long now = now();
        State state = state(chr);
        long elapsed = state.lastMovementAt == 0L ? 0L : now - state.lastMovementAt;
        int dx = Math.abs(after.x - before.x), dy = Math.abs(after.y - before.y);
        double distance = before.distance(after);
        Rectangle area = chr.getMap().getMapArea();
        if (area != null && area.width > 0 && area.height > 0) {
            Rectangle toleratedArea = new Rectangle(area); toleratedArea.grow(600, 600);
            if (!toleratedArea.contains(after)) flag(chr, "MOVEMENT_BOUNDS", "map=" + chr.getMapId() + " before=" + before + " after=" + after + " area=" + area, false);
        }
        if (dx > HARD_MOVE_X || dy > HARD_MOVE_Y || distance > HARD_MOVE_DISTANCE) {
            flag(chr, "MOVEMENT_TELEPORT", "map=" + chr.getMapId() + " dx=" + dx + " dy=" + dy + " distance=" + Math.round(distance), true);
        } else {
            if (dy > 650) flag(chr, "MOVEMENT_VERTICAL", "map=" + chr.getMapId() + " dx=" + dx + " dy=" + dy, false);
            if (elapsed >= 20L && elapsed <= 2_000L && distance >= 220.0) {
                double speed = distance * 1_000.0 / elapsed;
                if (speed > SUSPICIOUS_MOVE_SPEED) {
                    state.fastMovementBurst++;
                    if (state.fastMovementBurst >= 4) {
                        flag(chr, "MOVEMENT_SPEED", "map=" + chr.getMapId() + " speed=" + Math.round(speed) + "px/s elapsed=" + elapsed + "ms distance=" + Math.round(distance), false);
                        state.fastMovementBurst = 0;
                    }
                } else state.fastMovementBurst = 0;
            }
        }
        state.lastMovementAt = now; state.lastSeenAt = now;
    }

    public static void inspectMobMovement(Character controller, int mobId, Point before, Point after) {
        if (!enabled(controller) || before == null || after == null) return;
        double distance = before.distance(after);
        if (distance > HARD_MOB_MOVE_DISTANCE) {
            flag(controller, "MOB_VAC", "mob=" + mobId + " distance=" + Math.round(distance) + " before=" + before + " after=" + after, true);
        } else if (distance > SUSPICIOUS_MOB_MOVE_DISTANCE) {
            State state = state(controller); state.suspiciousMobMoves++;
            if (state.suspiciousMobMoves >= 3) {
                flag(controller, "MOB_MOVE_ANOMALY", "mob=" + mobId + " distance=" + Math.round(distance), false);
                state.suspiciousMobMoves = 0;
            }
        }
    }

    public static boolean validateAttackSkill(Character chr, int skillId) {
        if (!enabled(chr) || skillId == 0) return true;
        if (chr.getSkillLevel(skillId) > 0) return true;
        if (GameConstants.isPqSkillMap(chr.getMapId()) && GameConstants.isPqSkill(skillId)) return true;
        flag(chr, "INVALID_SKILL", "skill=" + skillId + " job=" + chr.getJob().getId() + " map=" + chr.getMapId(), true);
        return false;
    }

    public static void inspectAttack(Character chr, int skillId, String attackType) {
        if (!enabled(chr)) return;
        long now = now(); State state = state(chr);
        long elapsed = state.lastAttackAt == 0L ? Long.MAX_VALUE : now - state.lastAttackAt;
        if (elapsed >= 0L && elapsed < RAPID_ATTACK_INTERVAL_MS) {
            state.rapidAttackBurst++;
            if (state.rapidAttackBurst >= RAPID_ATTACK_BURST) {
                flag(chr, "FAST_ATTACK", "type=" + attackType + " skill=" + skillId + " interval=" + elapsed + "ms", true);
                state.rapidAttackBurst = 0;
            }
        } else state.rapidAttackBurst = 0;
        if (elapsed >= 80L && elapsed <= 2_000L) {
            if (state.lastAttackInterval > 0 && Math.abs(elapsed - state.lastAttackInterval) <= 2L) {
                state.regularAttackStreak++;
                if (state.regularAttackStreak == 30) flag(chr, "BOT_PATTERN", "type=" + attackType + " skill=" + skillId + " interval~=" + elapsed + "ms streak=30", false);
            } else state.regularAttackStreak = 0;
            state.lastAttackInterval = elapsed;
        }
        state.lastAttackAt = now; state.lastSeenAt = now;
    }

    public static boolean validatePickup(Character chr, Point collector, Point item, boolean petPickup) {
        if (!enabled(chr) || collector == null || item == null) return true;
        int maxX = petPickup ? PET_PICKUP_MAX_X : PLAYER_PICKUP_MAX_X;
        int maxY = petPickup ? PET_PICKUP_MAX_Y : PLAYER_PICKUP_MAX_Y;
        int dx = Math.abs(collector.x - item.x), dy = Math.abs(collector.y - item.y);
        if (dx > maxX || dy > maxY) {
            flag(chr, petPickup ? "PET_ITEM_VAC" : "ITEM_VAC", "map=" + chr.getMapId() + " collector=" + collector + " item=" + item + " dx=" + dx + " dy=" + dy, true);
            return false;
        }
        return true;
    }

    public static boolean validateQuantity(Character chr, String action, long quantity, long maxAllowed) {
        if (quantity <= 0 || quantity > maxAllowed) {
            if (enabled(chr)) flag(chr, "INVALID_QUANTITY", "action=" + action + " quantity=" + quantity + " max=" + maxAllowed, true);
            return false;
        }
        return true;
    }

    public static boolean validateMeso(Character chr, String action, long amount, long maxAllowed) {
        if (amount < 0 || amount > maxAllowed) {
            if (enabled(chr)) flag(chr, "INVALID_MESO", "action=" + action + " amount=" + amount + " max=" + maxAllowed, true);
            return false;
        }
        return true;
    }

    public static void flag(Character chr, String type, String detail, boolean hardViolation) {
        if (!enabled(chr)) return;
        long now = now(); State state = state(chr); state.lastSeenAt = now;
        synchronized (state) {
            state.violationCounts.put(type, state.violationCounts.getOrDefault(type, 0) + 1);
            state.recentEvidence.addLast(now + " " + type + " " + detail);
            while (state.recentEvidence.size() > MAX_RECENT_EVIDENCE) state.recentEvidence.removeFirst();
        }
        log.warn("AntiCheat type={} chr={} cid={} account={} map={} hard={} detail={}", type, chr.getName(), chr.getId(), chr.getAccountID(), chr.getMapId(), hardViolation, detail);
        if (YamlConfig.config.server.USE_ANTICHEAT_GM_ALERTS) {
            Long lastAlert = state.lastAlertAt.get(type);
            if (lastAlert == null || now - lastAlert >= GM_ALERT_COOLDOWN_MS) {
                state.lastAlertAt.put(type, now);
                Server.getInstance().broadcastGMMessage(chr.getWorld(), PacketCreator.sendYellowTip("[AntiCheat] " + chr.getName() + " " + type + ": " + detail));
            }
        }
        if (hardViolation && YamlConfig.config.server.USE_ANTICHEAT_ENFORCE) {
            if (state.hardStrikeWindowStart == 0L || now - state.hardStrikeWindowStart > HARD_STRIKE_WINDOW_MS) {
                state.hardStrikeWindowStart = now; state.hardStrikes = 0;
            }
            state.hardStrikes++;
            if (state.hardStrikes >= HARD_STRIKES_TO_KICK) {
                log.warn("AntiCheat disconnect chr={} cid={} account={} after {} hard strikes in {}ms", chr.getName(), chr.getId(), chr.getAccountID(), state.hardStrikes, HARD_STRIKE_WINDOW_MS);
                Server.getInstance().broadcastGMMessage(chr.getWorld(), PacketCreator.sendYellowTip("[AntiCheat] Disconnecting " + chr.getName() + " after repeated high-confidence violations."));
                state.hardStrikes = 0; state.hardStrikeWindowStart = now;
                if (chr.getClient() != null) chr.getClient().disconnect(false, false);
            }
        }
    }

    public static List<String> getStatus(Character chr) {
        List<String> lines = new ArrayList<>();
        if (chr == null) { lines.add("No character selected."); return lines; }
        State state = states.get(chr.getId());
        if (state == null) { lines.add(chr.getName() + ": no anti-cheat evidence in this server session."); return lines; }
        synchronized (state) {
            lines.add(chr.getName() + " anti-cheat: hardStrikes=" + state.hardStrikes + " violations=" + state.violationCounts);
            if (state.recentEvidence.isEmpty()) lines.add("No recent evidence."); else lines.addAll(state.recentEvidence);
        }
        return lines;
    }

    private static int[] sensitivePacketLimits(String handlerName) {
        if (handlerName == null) return null;
        return switch (handlerName) {
            case "StorageHandler" -> new int[]{25, 50};
            case "PlayerInteractionHandler" -> new int[]{50, 100};
            case "MesoDropHandler" -> new int[]{10, 25};
            case "ItemMoveHandler" -> new int[]{60, 120};
            case "NPCShopHandler" -> new int[]{35, 75};
            case "MakerSkillHandler" -> new int[]{15, 30};
            case "DueyHandler" -> new int[]{20, 40};
            case "CouponCodeHandler" -> new int[]{10, 20};
            case "ChangeMapSpecialHandler" -> new int[]{10, 20};
            case "ChangeMapHandler" -> new int[]{8, 16};
            case "HealOvertimeHandler" -> new int[]{8, 16};
            case "GiveFameHandler" -> new int[]{8, 16};
            default -> null;
        };
    }

    private static boolean enabled(Character chr) {
        return chr != null && chr.getMap() != null && !chr.isGM() && YamlConfig.config.server.USE_ANTICHEAT;
    }

    private static State state(Character chr) {
        long now = now(); State state = states.computeIfAbsent(chr.getId(), ignored -> new State());
        if (state.lastSeenAt != 0L && now - state.lastSeenAt > 10 * 60_000L) state.resetTransient();
        return state;
    }

    private static long now() { return Server.getInstance().getCurrentTime(); }

    private static final class WindowCounter { long startedAt; int count; boolean softAlerted; }
    private static final class State {
        long lastSeenAt, lastMovementAt, lastAttackAt, lastAttackInterval, hardStrikeWindowStart;
        int fastMovementBurst, rapidAttackBurst, regularAttackStreak, suspiciousMobMoves, hardStrikes;
        long packetWindowStart, packetLongWindowStart, unknownWindowStart;
        int packetCount, packetLongCount, unknownCount;
        boolean packetSoftAlerted;
        final Map<String, WindowCounter> actionWindows = new HashMap<>();
        final Map<String, Long> lastAlertAt = new ConcurrentHashMap<>();
        final Map<String, Integer> violationCounts = new HashMap<>();
        final Deque<String> recentEvidence = new ArrayDeque<>();
        void resetTransient() {
            lastMovementAt = lastAttackAt = lastAttackInterval = hardStrikeWindowStart = 0L;
            fastMovementBurst = rapidAttackBurst = regularAttackStreak = suspiciousMobMoves = hardStrikes = 0;
            packetWindowStart = packetLongWindowStart = unknownWindowStart = 0L;
            packetCount = packetLongCount = unknownCount = 0; packetSoftAlerted = false;
            actionWindows.clear(); lastAlertAt.clear();
        }
    }
}
