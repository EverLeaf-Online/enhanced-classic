package server.travel;

import client.Character;
import tools.PacketCreator;

import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

/**
 * Small per-character timer for legacy personal travel maps that repeatedly
 * invoke a portal script while the ride is in progress.
 *
 * The timer is intentionally fail-open when no ticket exists: a player who
 * reconnects after a process restart must be able to leave a transit map rather
 * than becoming permanently trapped there.
 */
public final class PersonalTravelService {
    private static final int MAX_DURATION_SECONDS = 10 * 60;
    private static final Map<Integer, Long> ARRIVAL_TIMES = new ConcurrentHashMap<>();

    private PersonalTravelService() {
    }

    public static void begin(Character player, int durationSeconds) {
        if (player == null) {
            throw new IllegalArgumentException("player is required");
        }
        if (durationSeconds <= 0 || durationSeconds > MAX_DURATION_SECONDS) {
            throw new IllegalArgumentException("invalid travel duration: " + durationSeconds);
        }

        long durationMillis = Math.multiplyExact((long) durationSeconds, 1000L);
        ARRIVAL_TIMES.put(player.getId(), Math.addExact(System.currentTimeMillis(), durationMillis));
        player.sendPacket(PacketCreator.getClock(durationSeconds));
    }

    public static boolean completeIfReady(Character player) {
        if (player == null) {
            return false;
        }

        Long arrivalTime = ARRIVAL_TIMES.get(player.getId());
        if (arrivalTime != null && System.currentTimeMillis() < arrivalTime) {
            return false;
        }

        ARRIVAL_TIMES.remove(player.getId());
        return true;
    }

    public static void cancel(Character player) {
        if (player != null) {
            ARRIVAL_TIMES.remove(player.getId());
        }
    }
}
