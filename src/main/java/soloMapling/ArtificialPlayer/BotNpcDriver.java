package soloMapling.ArtificialPlayer;

import client.Character;
import client.Client;
import scripting.npc.NPCScriptManager;
import server.life.NPC;
import server.maps.MapObject;
import server.maps.MapObjectType;

import java.awt.Point;
import java.util.List;

/** Server-authoritative NPC interaction helpers for headless QA bots. */
public final class BotNpcDriver {
    private static final double INTERACT_RANGE_SQ = 250.0 * 250.0;

    private BotNpcDriver() {}

    public static NPC nearestNpc(Character bot, boolean requireShop) {
        if (bot == null || bot.getMap() == null || bot.getPosition() == null) return null;
        Point from = bot.getPosition();
        NPC best = null;
        double bestDistance = Double.MAX_VALUE;
        for (MapObject object : bot.getMap().getMapObjectsInRange(from, Double.MAX_VALUE, List.of(MapObjectType.NPC))) {
            if (!(object instanceof NPC npc)) continue;
            if (requireShop && !npc.hasShop()) continue;
            if (npc.getPosition() == null) continue;
            double distance = from.distanceSq(npc.getPosition());
            if (distance < bestDistance) {
                bestDistance = distance;
                best = npc;
            }
        }
        return best;
    }

    public static NPC findNpc(Character bot, int npcId) {
        if (bot == null || bot.getMap() == null || bot.getPosition() == null) return null;
        for (MapObject object : bot.getMap().getMapObjectsInRange(bot.getPosition(), Double.MAX_VALUE, List.of(MapObjectType.NPC))) {
            if (object instanceof NPC npc && npc.getId() == npcId) return npc;
        }
        return null;
    }

    public static InteractionResult startNearest(Character bot) {
        NPC npc = nearestNpc(bot, false);
        return npc == null ? InteractionResult.fail("no-npc") : start(bot, npc.getId());
    }

    public static InteractionResult start(Character bot, int npcId) {
        if (!eligible(bot)) return InteractionResult.fail("not-eligible");
        NPC npc = findNpc(bot, npcId);
        if (npc == null) return InteractionResult.fail("npc-not-on-map");
        if (bot.getPosition().distanceSq(npc.getPosition()) > INTERACT_RANGE_SQ) return InteractionResult.fail("npc-too-far");

        Client client = bot.getClient();
        NPCScriptManager scripts = NPCScriptManager.getInstance();
        scripts.dispose(client);
        boolean started = scripts.start(client, npc.getId(), npc.getObjectId(), bot);
        return started
                ? new InteractionResult(true, npc.getId(), npc.getName(), "started")
                : new InteractionResult(false, npc.getId(), npc.getName(), "script-unavailable");
    }

    public static InteractionResult next(Character bot, int selection) {
        if (!eligible(bot)) return InteractionResult.fail("not-eligible");
        NPCScriptManager scripts = NPCScriptManager.getInstance();
        if (scripts.getCM(bot.getClient()) == null) return InteractionResult.fail("no-active-dialogue");
        int npcId = scripts.getCM(bot.getClient()).getNpc();
        scripts.action(bot.getClient(), (byte) 1, (byte) 0, selection);
        return new InteractionResult(true, npcId, "", "advanced");
    }

    public static void cancel(Character bot) {
        if (bot != null && bot.getClient() != null) NPCScriptManager.getInstance().dispose(bot.getClient());
    }

    private static boolean eligible(Character bot) {
        return bot != null && BotHelpers.isBot(bot) && bot.getClient() != null && bot.getMap() != null && bot.getPosition() != null;
    }

    public record InteractionResult(boolean success, int npcId, String npcName, String reason) {
        static InteractionResult fail(String reason) {
            return new InteractionResult(false, 0, "", reason);
        }
    }
}
