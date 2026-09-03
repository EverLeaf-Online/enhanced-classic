package soloMapling.ArtificialPlayer;

import client.BotClient;
import client.Client;
import soloMapling.server.SoloMaplingConstants.GameConstants;

import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

/**
 * Headless-client registry for SoloMapling artificial players.
 *
 * <p>The original controlled integration used one shared client because only one
 * QA bot could exist at a time. Autonomous/E2E testing needs multiple bots, and
 * server APIs such as party, trade and storage resolve their acting character
 * from {@link Client#getPlayer()}. Every live bot therefore gets its own
 * headless client so one bot can never accidentally act as another.</p>
 */
public final class BotClientHandler {
    private static volatile Client bootstrapBotClient;
    private static final Map<Integer, Client> botClients = new ConcurrentHashMap<>();

    private BotClientHandler() {}

    /**
     * Keeps the existing bootstrap/compatibility probe available. Production bot
     * instances should use {@link #createHeadlessBotClient(int, int)} instead.
     */
    public static synchronized void initHeadlessBotClient() {
        if (bootstrapBotClient == null) {
            bootstrapBotClient = createHeadlessBotClient(GameConstants.WORLD_SCANIA, GameConstants.CHANNEL_1);
        }
    }

    public static Client createHeadlessBotClient(int world, int channel) {
        return new BotClient(world, channel);
    }

    public static void registerBotClient(int botId, Client client) {
        if (botId <= 0 || client == null) {
            throw new IllegalArgumentException("bot id/client must be valid");
        }
        Client previous = botClients.putIfAbsent(botId, client);
        if (previous != null && previous != client) {
            throw new IllegalStateException("Headless client already registered for bot " + botId);
        }
    }

    public static Client unregisterBotClient(int botId) {
        return botClients.remove(botId);
    }

    public static Client getBotClient(int botId) {
        return botClients.get(botId);
    }

    /** Legacy bootstrap client used by compatibility probes and startup wiring. */
    public static Client getBotClient() {
        return bootstrapBotClient;
    }

    public static int activeClientCount() {
        return botClients.size();
    }
}
