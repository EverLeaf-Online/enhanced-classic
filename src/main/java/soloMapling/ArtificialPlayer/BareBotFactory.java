package soloMapling.ArtificialPlayer;

import client.Character;
import client.Client;
import net.server.Server;
import net.server.channel.Channel;
import net.server.world.World;
import server.maps.MapleMap;
import soloMapling.server.SoloMaplingConstants;

import java.awt.Point;
import java.sql.SQLException;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicInteger;

/**
 * Dependency-closed EverLeaf bot factory built around SoloMapling's headless-player model.
 *
 * <p>Each synthetic player is loaded through EverLeaf's normal Character path, but receives
 * a collision-free high character id and a dedicated headless Client. That keeps inventory,
 * party, trade, quest and storage APIs server-authoritative while preventing synthetic players
 * from owning a real login/account session.</p>
 */
public final class BareBotFactory {
    private static final AtomicInteger nextBotOffset = new AtomicInteger(100);
    private static final int MAX_SYNTHETIC_OFFSET = 99_000_000;
    private static final Map<Integer, Registration> registrations = new ConcurrentHashMap<>();

    private BareBotFactory() {}

    /** Backwards-compatible controlled QA spawn on world 0/channel 1. */
    public static Character createBareBot(int templateCharacterId, Point position, MapleMap map) throws SQLException {
        return createBareBot(templateCharacterId, position, map,
                SoloMaplingConstants.GameConstants.WORLD_SCANIA,
                SoloMaplingConstants.GameConstants.CHANNEL_1);
    }

    /**
     * Creates one isolated synthetic player in the requested world/channel.
     * The supplied map must belong to that channel's map factory.
     */
    public static Character createBareBot(
            int templateCharacterId,
            Point position,
            MapleMap map,
            int worldId,
            int channelId) throws SQLException {
        if (templateCharacterId <= 0) {
            throw new IllegalArgumentException("template character id must be positive");
        }
        if (map == null) {
            throw new IllegalArgumentException("map must not be null");
        }
        if (position == null) {
            throw new IllegalArgumentException("position must not be null");
        }

        Server server = Server.getInstance();
        Channel channel = server.getChannel(worldId, channelId);
        World world = server.getWorld(worldId);
        if (channel == null || world == null) {
            throw new IllegalStateException("SoloMapling QA world/channel is not available: "
                    + worldId + "/" + channelId);
        }

        Client botClient = BotClientHandler.createHeadlessBotClient(worldId, channelId);

        // Channel loading gives the bot the same quest/inventory/login-facing state normal
        // map players use, while BotClient suppresses network/account-session side effects.
        Character bot = Character.loadCharFromDB(templateCharacterId, botClient, true);
        if (bot == null) {
            throw new IllegalStateException("Could not load QA bot template character " + templateCharacterId);
        }

        int botId = allocateSyntheticId(channel, world);
        int displayOffset = botId - SoloMaplingConstants.GameConstants.BOT_BASE_ID;
        bot.setClient(botClient);
        bot.setID(botId);
        bot.setName("ELQA" + displayOffset);
        bot.setFame(0);

        // The persisted character is only a visual/stat/template source. Never let cloned
        // administrative or social state leak into a synthetic player.
        bot.setGMLevel(0);
        bot.setParty(null);
        bot.setMessenger(null);
        bot.setGuildId(0);

        bot.setMap(map);
        bot.setPosition(position);
        bot.setStance(5);
        bot.setWorldRates();

        botClient.setPlayer(bot);
        BotClientHandler.registerBotClient(botId, botClient);

        boolean registered = false;
        try {
            channel.addPlayer(bot);
            world.getPlayerStorage().addPlayer(bot);
            bot.setEnteredChannelWorld();
            if (!bot.isLoggedinWorld()) {
                throw new IllegalStateException("SoloMapling QA bot failed to enter logged-in channel world state");
            }
            map.addPlayer(bot);
            registrations.put(botId, new Registration(channel, world, botClient));
            registered = true;
            return bot;
        } finally {
            if (!registered) {
                BotClientHandler.unregisterBotClient(botId);
                botClient.setPlayer(null);
                try { channel.removePlayer(bot); } catch (RuntimeException ignored) { }
                try { world.getPlayerStorage().removePlayer(botId); } catch (RuntimeException ignored) { }
            }
        }
    }

    private static int allocateSyntheticId(Channel channel, World world) {
        for (int attempts = 0; attempts < 10_000; attempts++) {
            int offset = nextBotOffset.getAndIncrement();
            if (offset > MAX_SYNTHETIC_OFFSET) {
                throw new IllegalStateException("SoloMapling QA synthetic bot id range exhausted");
            }
            int candidate = SoloMaplingConstants.GameConstants.BOT_BASE_ID + offset;
            if (channel.getPlayerStorage().getCharacterById(candidate) == null
                    && world.getPlayerStorage().getCharacterById(candidate) == null
                    && !registrations.containsKey(candidate)) {
                return candidate;
            }
        }
        throw new IllegalStateException("Could not allocate a collision-free SoloMapling QA bot id");
    }

    public static void removeBareBot(Character bot) {
        if (bot == null) return;

        BareBotHunter.stop(bot);
        BareBotAutopilot.stop(bot);
        try {
            soloMapling.ArtificialPlayer.GCMoveSystem.GCMovement.disable(bot);
        } catch (RuntimeException ignored) { }

        if (bot.getMap() != null) {
            try { bot.getMap().removePlayer(bot); } catch (RuntimeException ignored) { }
        }

        Registration registration = registrations.remove(bot.getId());
        if (registration != null) {
            try { registration.channel().removePlayer(bot); } catch (RuntimeException ignored) { }
            try { registration.world().getPlayerStorage().removePlayer(bot.getId()); } catch (RuntimeException ignored) { }
        } else {
            // Compatibility fallback for a bot created by an older build before the registry existed.
            Server server = Server.getInstance();
            Channel channel = server.getChannel(
                    SoloMaplingConstants.GameConstants.WORLD_SCANIA,
                    SoloMaplingConstants.GameConstants.CHANNEL_1);
            World world = server.getWorld(SoloMaplingConstants.GameConstants.WORLD_SCANIA);
            if (channel != null) {
                try { channel.removePlayer(bot); } catch (RuntimeException ignored) { }
            }
            if (world != null) {
                try { world.getPlayerStorage().removePlayer(bot.getId()); } catch (RuntimeException ignored) { }
            }
        }

        Client client = BotClientHandler.unregisterBotClient(bot.getId());
        if (client == null) client = bot.getClient();
        if (client != null && client.getPlayer() == bot) {
            client.setPlayer(null);
        }
    }

    public static int activeBotCount() {
        return registrations.size();
    }

    private record Registration(Channel channel, World world, Client client) {}
}
