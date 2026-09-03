package soloMapling.ArtificialPlayer;

import client.Character;
import client.inventory.InventoryType;
import client.inventory.Item;
import client.inventory.manipulator.InventoryManipulator;
import net.server.Server;
import net.server.channel.Channel;
import server.maps.MapleMap;
import server.maps.Portal;
import soloMapling.ArtificialPlayer.BotAttackSystem.BotAttackDriver;

import java.awt.Point;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

/** Bounded multi-bot fixture for autonomous EverLeaf QA. Never runs automatically at server startup. */
public final class BotQaFleet {
    public static final int MAX_BOTS_PER_FLEET = 12;
    private static final int DEFAULT_LEVEL = 70;
    private static final int DEFAULT_MESOS = 250_000;
    private static final int[] DEFAULT_JOBS = {112, 212, 312, 412, 512, 522, 1112, 1212, 1312, 1412, 1512, 2112};
    private static final Map<Integer, Fleet> fleetsByOwner = new ConcurrentHashMap<>();

    private BotQaFleet() {}

    public static synchronized FleetResult spawn(int ownerId, int templateCharacterId, int count,
                                                 int worldId, int channelId, int mapId) {
        if (ownerId <= 0 || templateCharacterId <= 0) return FleetResult.fail("invalid-owner-or-template");
        if (count < 1 || count > MAX_BOTS_PER_FLEET) return FleetResult.fail("count-must-be-1-to-" + MAX_BOTS_PER_FLEET);
        remove(ownerId);

        Channel channel = Server.getInstance().getChannel(worldId, channelId);
        if (channel == null) return FleetResult.fail("channel-unavailable");
        MapleMap map = channel.getMapFactory().getMap(mapId);
        if (map == null) return FleetResult.fail("map-unavailable");
        Point origin = spawnPoint(map);

        List<Character> bots = new ArrayList<>();
        try {
            for (int i = 0; i < count; i++) {
                Point position = new Point(origin.x + (i % 4) * 25, origin.y);
                Character bot = BareBotFactory.createBareBot(templateCharacterId, position, map, worldId, channelId);
                normalize(bot, DEFAULT_JOBS[i % DEFAULT_JOBS.length], DEFAULT_LEVEL, DEFAULT_MESOS);
                bots.add(bot);
            }
            Fleet fleet = new Fleet(ownerId, templateCharacterId, worldId, channelId, mapId,
                    System.currentTimeMillis(), List.copyOf(bots));
            fleetsByOwner.put(ownerId, fleet);
            return snapshot(fleet, true, "spawned");
        } catch (SQLException | RuntimeException failure) {
            for (Character bot : bots) safeRemove(bot);
            return FleetResult.fail("spawn-failed:" + failure.getClass().getSimpleName());
        }
    }

    public static synchronized FleetResult remove(int ownerId) {
        Fleet fleet = fleetsByOwner.remove(ownerId);
        if (fleet == null) return FleetResult.fail("no-fleet");
        for (Character bot : fleet.bots()) safeRemove(bot);
        return new FleetResult(true, 0, fleet.worldId(), fleet.channelId(), fleet.mapId(), 0, 0, 0,
                BareBotFactory.activeBotCount(), BotClientHandler.activeClientCount(), "removed");
    }

    public static FleetResult status(int ownerId) {
        Fleet fleet = fleetsByOwner.get(ownerId);
        return fleet == null ? FleetResult.fail("no-fleet") : snapshot(fleet, true, "status");
    }

    public static Fleet get(int ownerId) {
        return fleetsByOwner.get(ownerId);
    }

    public static List<Character> bots(int ownerId) {
        Fleet fleet = fleetsByOwner.get(ownerId);
        return fleet == null ? List.of() : fleet.bots();
    }

    public static int fleetCount() {
        return fleetsByOwner.size();
    }

    private static void normalize(Character bot, int jobId, int level, int mesos) {
        stopAll(bot);
        // Synthetic ids are never persisted, so normalizing this clone cannot alter the template row.
        bot.loseExp(bot.getExp(), false, false);
        bot.setLevel(Math.max(1, Math.min(level, bot.getMaxClassLevel())));
        BotQaProfile.apply(bot, jobId);
        clearInventory(bot, InventoryType.EQUIP);
        clearInventory(bot, InventoryType.USE);
        clearInventory(bot, InventoryType.SETUP);
        clearInventory(bot, InventoryType.ETC);
        clearInventory(bot, InventoryType.CASH);

        int delta = mesos - bot.getMeso();
        if (delta != 0) bot.gainMeso(delta, false, true, false);
        InventoryManipulator.addById(bot.getClient(), 2000000, (short) 100, "", -1); // Red Potion
        InventoryManipulator.addById(bot.getClient(), 2000001, (short) 100, "", -1); // Blue Potion
        if (needsStars(jobId)) InventoryManipulator.addById(bot.getClient(), 2070000, (short) 1, "", -1);
        if (needsBullets(jobId)) InventoryManipulator.addById(bot.getClient(), 2330000, (short) 1, "", -1);
    }

    private static void clearInventory(Character bot, InventoryType type) {
        List<Item> copy = new ArrayList<>(bot.getInventory(type).list());
        for (Item item : copy) {
            if (item == null || item.getQuantity() <= 0) continue;
            try {
                InventoryManipulator.removeFromSlot(bot.getClient(), type, item.getPosition(), item.getQuantity(), false);
            } catch (RuntimeException ignored) { }
        }
    }

    private static boolean needsStars(int jobId) {
        return (jobId >= 410 && jobId <= 412) || (jobId >= 1400 && jobId <= 1412);
    }

    private static boolean needsBullets(int jobId) {
        return jobId >= 520 && jobId <= 522;
    }

    private static Point spawnPoint(MapleMap map) {
        Portal portal = map.getPortal(0);
        if (portal != null && portal.getPosition() != null) return new Point(portal.getPosition());
        return new Point(0, 0);
    }

    private static void safeRemove(Character bot) {
        if (bot == null) return;
        stopAll(bot);
        try { BotTradeDriver.cancel(bot); } catch (RuntimeException ignored) { }
        try { if (bot.getParty() != null) BotPartyDriver.leave(bot); } catch (RuntimeException ignored) { }
        try { if (bot.getStorage() != null && bot.getStorage().isStorageOpen()) BotStorageDriver.close(bot); } catch (RuntimeException ignored) { }
        try { BareBotFactory.removeBareBot(bot); } catch (RuntimeException ignored) { }
    }

    static void stopAll(Character bot) {
        if (bot == null) return;
        try { BotPqDriver.stop(bot); } catch (RuntimeException ignored) { }
        try { BotBossDriver.stop(bot); } catch (RuntimeException ignored) { }
        try { BareBotHunter.stop(bot); } catch (RuntimeException ignored) { }
        try { BareBotAutopilot.stop(bot); } catch (RuntimeException ignored) { }
        try { soloMapling.ArtificialPlayer.GCMoveSystem.GCMovement.disable(bot); } catch (RuntimeException ignored) { }
        try { BotAttackDriver.clearBot(bot.getId()); } catch (RuntimeException ignored) { }
        try { BotLootDriver.clearBot(bot.getId()); } catch (RuntimeException ignored) { }
        try { BotBuffDriver.clearBot(bot.getId()); } catch (RuntimeException ignored) { }
        try { BotConsumableDriver.clearBot(bot.getId()); } catch (RuntimeException ignored) { }
        try { BotNpcDriver.cancel(bot); } catch (RuntimeException ignored) { }
    }

    private static FleetResult snapshot(Fleet fleet, boolean success, String reason) {
        int alive = 0;
        int logged = 0;
        int autonomous = 0;
        for (Character bot : fleet.bots()) {
            if (bot != null && bot.isAlive()) alive++;
            if (bot != null && bot.isLoggedinWorld()) logged++;
            if (BareBotHunter.isHunting(bot) || BotBossDriver.isRunning(bot) || BotPqDriver.isRunning(bot)) autonomous++;
        }
        return new FleetResult(success, fleet.bots().size(), fleet.worldId(), fleet.channelId(), fleet.mapId(),
                alive, logged, autonomous, BareBotFactory.activeBotCount(), BotClientHandler.activeClientCount(), reason);
    }

    public record Fleet(int ownerId, int templateCharacterId, int worldId, int channelId, int mapId,
                        long createdAt, List<Character> bots) {
        public Fleet {
            bots = Collections.unmodifiableList(new ArrayList<>(bots));
        }
    }

    public record FleetResult(boolean success, int bots, int worldId, int channelId, int mapId, int alive,
                              int loggedInWorld, int autonomous, int globalFactoryBots, int headlessClients,
                              String reason) {
        static FleetResult fail(String reason) {
            return new FleetResult(false, 0, 0, 0, 0, 0, 0, 0,
                    BareBotFactory.activeBotCount(), BotClientHandler.activeClientCount(), reason);
        }
    }
}
