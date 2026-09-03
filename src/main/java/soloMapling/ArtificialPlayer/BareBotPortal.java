package soloMapling.ArtificialPlayer;

import client.Character;
import server.maps.MapleMap;
import server.maps.Portal;

/**
 * Controlled client-free portal entry based on SoloMapling GCPortals.
 *
 * <p>The shared headless BotClient cannot safely call portal.enterPortal(client),
 * because that API resolves the character through the client. Resolve the
 * destination from the bot's current server-side map instead and change the
 * Character directly.</p>
 */
public final class BareBotPortal {
    private BareBotPortal() {
    }

    public record PortalResult(boolean success, int fromMapId, int toMapId, String reason) {
    }

    public static PortalResult enter(Character bot, int portalId) {
        if (bot == null || bot.getMap() == null) {
            return new PortalResult(false, -1, -1, "bot is not on a map");
        }

        MapleMap from = bot.getMap();
        Portal portal = from.getPortal(portalId);
        if (portal == null) {
            return new PortalResult(false, from.getId(), -1, "portal " + portalId + " does not exist");
        }

        int targetMapId = portal.getTargetMapId();
        if (targetMapId < 0) {
            return new PortalResult(false, from.getId(), targetMapId,
                    "portal " + portalId + " has no direct target map");
        }

        try {
            MapleMap to = bot.getEventInstance() == null
                    ? from.getChannelServer().getMapFactory().getMap(targetMapId)
                    : bot.getEventInstance().getMapInstance(targetMapId);
            if (to == null) {
                return new PortalResult(false, from.getId(), targetMapId,
                        "destination map could not be resolved");
            }

            Portal targetPortal = to.getPortal(portal.getTarget());
            if (targetPortal == null) {
                targetPortal = to.getPortal(0);
            }
            if (targetPortal == null) {
                return new PortalResult(false, from.getId(), targetMapId,
                        "destination has no target or fallback portal");
            }

            bot.changeMap(to, targetPortal);
            return new PortalResult(bot.getMapId() == targetMapId, from.getId(), targetMapId,
                    bot.getMapId() == targetMapId ? null : "changeMap did not reach destination");
        } catch (RuntimeException e) {
            return new PortalResult(false, from.getId(), targetMapId, e.getMessage());
        }
    }
}
