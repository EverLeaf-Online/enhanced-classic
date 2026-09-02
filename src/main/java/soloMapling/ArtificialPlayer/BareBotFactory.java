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
 * quest, or economy systems. Once the full upstream BotGeneration dependency
 * graph is reconciled, callers can move to that implementation.</p>
 */
public final class BareBotFactory {
    private static final int DEFAULT_BASE_CHARACTER_ID = 2;
    private static final AtomicInteger nextBotOffset = new AtomicInteger(100);

    private BareBotFactory() {
    }

    public static Character createBareBot(Point position, MapleMap map) throws SQLException {
        return createBareBot(DEFAULT_BASE_CHARACTER_ID, position, map);
    }

    public static Character createBareBot(int baseCharacterId, Point position, MapleMap map) throws SQLException {
        if (map == null) {
            throw new IllegalArgumentException("map must not be null");
        }
        if (position == null) {
            throw new IllegalArgumentException("position must not be null");
        }

        if (BotClientHandler.getBotClient() == null) {
            BotClientHandler.initHeadlessBotClient();
        }

        Character bot = Character.loadCharFromDB(baseCharacterId, BotClientHandler.getBotClient(), false);
        if (bot == null) {
            throw new IllegalStateException("Could not load SoloMapling base character " + baseCharacterId);
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
