package soloMapling.ArtificialPlayer;

import client.Character;
import server.maps.MapItem;
import server.maps.MapObject;
import server.maps.MapObjectType;
import soloMapling.ArtificialPlayer.GCMoveSystem.GCMovement;

import java.awt.Point;
import java.util.Arrays;
import java.util.Comparator;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

/**
 * Conservative EverLeaf-authoritative loot driver for QA bots.
 *
 * <p>Bots only target drops owned by themselves (or their current party), then
 * delegate the actual transaction to Character.pickupItem(). This deliberately
 * avoids SoloMapling's donor-side drop-removal shortcut so EverLeaf remains the
 * authority for ownership, inventory capacity, quest items, mesos and pickup
 * side effects.</p>
 */
public final class BotLootDriver {
    private static final int PICKUP_REACH_X = 85;
    private static final int PICKUP_REACH_Y = 80;
    private static final long FAILED_PICKUP_BACKOFF_MS = 5_000L;
    private static final Map<Long, Long> retryAfter = new ConcurrentHashMap<>();

    private BotLootDriver() {}

    public static LootResult tick(Character bot) {
        if (bot == null || bot.getMap() == null || bot.getPosition() == null || !BotHelpers.isBot(bot)) {
            return LootResult.none();
        }

        MapItem drop = nearestOwnedDrop(bot);
        if (drop == null || drop.getPosition() == null) return LootResult.none();

        Point botPos = bot.getPosition();
        Point dropPos = drop.getPosition();
        int dx = dropPos.x - botPos.x;
        int dy = dropPos.y - botPos.y;

        if (Math.abs(dx) > PICKUP_REACH_X || Math.abs(dy) > PICKUP_REACH_Y) {
            try {
                GCMovement.move(bot, dropPos.x, dropPos.y);
                return new LootResult(true, true, false, drop.getObjectId(), "moving-to-drop");
            } catch (RuntimeException ex) {
                defer(bot, drop);
                return new LootResult(true, false, false, drop.getObjectId(), "loot-navigation-failed");
            }
        }

        GCMovement.stop(bot);
        try {
            bot.pickupItem(drop);
            if (drop.isPickedUp()) {
                retryAfter.remove(key(bot, drop));
                return new LootResult(true, false, true, drop.getObjectId(), "picked-up");
            }
            defer(bot, drop);
            return new LootResult(true, false, false, drop.getObjectId(), "pickup-deferred");
        } catch (RuntimeException ex) {
            defer(bot, drop);
            return new LootResult(true, false, false, drop.getObjectId(), "pickup-failed");
        }
    }

    public static void clearBot(int botId) {
        retryAfter.keySet().removeIf(key -> (int) (key >>> 32) == botId);
    }

    private static MapItem nearestOwnedDrop(Character bot) {
        Point botPos = bot.getPosition();
        long now = System.currentTimeMillis();
        return bot.getMap().getMapObjectsInRange(
                        botPos,
                        Double.POSITIVE_INFINITY,
                        Arrays.asList(MapObjectType.ITEM))
                .stream()
                .filter(MapItem.class::isInstance)
                .map(MapItem.class::cast)
                .filter(drop -> !drop.isPickedUp() && drop.getPosition() != null)
                .filter(drop -> ownsDrop(bot, drop))
                .filter(drop -> retryAfter.getOrDefault(key(bot, drop), 0L) <= now)
                .min(Comparator.comparingDouble(drop -> botPos.distanceSq(drop.getPosition())))
                .orElse(null);
    }

    private static boolean ownsDrop(Character bot, MapItem drop) {
        if (drop.getOwnerId() == bot.getId()) return true;
        return bot.getPartyId() != -1 && drop.getPartyOwnerId() == bot.getPartyId();
    }

    private static void defer(Character bot, MapItem drop) {
        retryAfter.put(key(bot, drop), System.currentTimeMillis() + FAILED_PICKUP_BACKOFF_MS);
    }

    private static long key(Character bot, MapObject drop) {
        return ((long) bot.getId() << 32) ^ (drop.getObjectId() & 0xffffffffL);
    }

    public record LootResult(boolean found, boolean moving, boolean pickedUp, int objectId, String reason) {
        private static LootResult none() {
            return new LootResult(false, false, false, -1, "no-owned-drop");
        }
    }
}
