package soloMapling.ArtificialPlayer;

import client.Character;
import net.server.Server;
import net.server.channel.Channel;
import net.server.world.World;
import server.maps.MapleMap;
import soloMapling.server.SoloMaplingConstants;

import java.awt.Point;
import java.sql.SQLException;
import java.util.concurrent.atomic.AtomicInteger;

/**
 * Minimal dependency-closed slice of SoloMapling's BotGeneration flow.
 *
 * <p>This exists only to get the first controlled EverLeaf headless-bot smoke
 * test running without pulling in decoration, chatter, Free Market, party,
 * quest, or economy systems. Unlike upstream's hard-coded character-id 2
 * template, EverLeaf requires the caller to choose an existing persisted
 * character explicitly, so no special database seed row is required.</p>
 */
public final class BareBotFactory {
    private static final AtomicInteger nextBotOffset = new AtomicInteger(100);

    private BareBotFactory() {
    }

    public static Character createBareBot(int templateCharacterId, Point position, MapleMap map) throws SQLException {
        if (templateCharacterId <= 0) {
            throw new IllegalArgumentException("template character id must be positive");
        }
        if (map == null) {
            throw new IllegalArgumentException("map must not be null");
        }
        if (position == null) {
            throw new IllegalArgumentException("position must not be null");
        }

        if (BotClientHandler.getBotClient() == null) {
            BotClientHandler.initHeadlessBotClient();
        }

        Character bot = Character.loadCharFromDB(templateCharacterId, BotClientHandler.getBotClient(), false);
        if (bot == null) {
            throw new IllegalStateException("Could not load QA bot template character " + templateCharacterId);
        }

        int botId = SoloMaplingConstants.GameConstants.BOT_BASE_ID + nextBotOffset.getAndIncrement();
        bot.setClient(BotClientHandler.getBotClient());
        bot.setID(botId);
        bot.setName("EverLeafQA" + botId);
        bot.setFame(botId);
        bot.setMap(map);
        bot.setPosition(position);
        bot.setStance(5);

        Server server = Server.getInstance();
        Channel channel = server.getChannel(
                SoloMaplingConstants.GameConstants.WORLD_SCANIA,
                SoloMaplingConstants.GameConstants.CHANNEL_1);
        World world = server.getWorld(SoloMaplingConstants.GameConstants.WORLD_SCANIA);
        if (channel == null || world == null) {
            throw new IllegalStateException("SoloMapling QA world/channel is not available");
        }

        // loadCharFromDB does not execute the normal PlayerLoggedinHandler rate
        // initialization. Apply the current EverLeaf world rates so bot-attributed
        // EXP/meso/drop smoke tests use the same world multipliers as players.
        bot.setWorldRates();

        channel.addPlayer(bot);
        world.getPlayerStorage().addPlayer(bot);
        map.addPlayer(bot);
        return bot;
    }

    public static void removeBareBot(Character bot) {
        if (bot == null) {
            return;
        }

        if (bot.getMap() != null) {
            bot.getMap().removePlayer(bot);
        }

        Server server = Server.getInstance();
        Channel channel = server.getChannel(
                SoloMaplingConstants.GameConstants.WORLD_SCANIA,
                SoloMaplingConstants.GameConstants.CHANNEL_1);
        World world = server.getWorld(SoloMaplingConstants.GameConstants.WORLD_SCANIA);
        if (channel != null) {
            channel.removePlayer(bot);
        }
        if (world != null) {
            world.getPlayerStorage().removePlayer(bot.getId());
        }
    }
}
