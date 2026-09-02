package soloMapling.ArtificialPlayer;

import client.Character;
import net.server.Server;
import net.server.channel.Channel;
import server.maps.MapItem;
import server.maps.MapObject;
import soloMapling.server.SoloMaplingConstants;

import java.awt.Point;
import java.awt.Rectangle;
import java.util.List;
import java.util.Random;

/** EverLeaf-safe subset of SoloMapling bot helpers. */
public final class BotHelpers {
    private static final int BOT_ID_LIMIT_EXCLUSIVE = 1_000_000_000;

    private BotHelpers() {}

    public static Character getCharFromChannelStorage(int cid) {
        Channel channel = Server.getInstance().getChannel(
                SoloMaplingConstants.GameConstants.WORLD_SCANIA,
                SoloMaplingConstants.GameConstants.CHANNEL_1);
        if (channel == null) return null;
        Character character = channel.getPlayerStorage().getCharacterById(cid);
        return isBot(character) ? character : null;
    }

    public static boolean isBot(Character character) {
        return character != null && isBot(character.getId());
    }

    /**
     * EverLeaf reserves 900,000,000..999,999,999 for in-memory artificial players.
     * Do not use upstream's broad id > 20000 heuristic: legitimate persisted players can
     * exceed that value on a long-running server.
     */
    public static boolean isBot(int id) {
        return id >= SoloMaplingConstants.GameConstants.BOT_BASE_ID && id < BOT_ID_LIMIT_EXCLUSIVE;
    }

    public static boolean blockingSleep(long milliseconds) {
        try {
            Thread.sleep(milliseconds);
            return true;
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            return false;
        }
    }

    public static Point getRandomizedPointXAxis(Point original) {
        return getRandomizedPointXAxis(original, 50);
    }

    public static Point getRandomizedPointXAxis(Point original, int range) {
        int minX = original.x - range;
        int maxX = original.x + range;
        int randomX = new Random().nextInt(maxX - minX + 1) + minX;
        return new Point(randomX, original.y);
    }

    public static Rectangle createRectangle(Point center, int width, int height) {
        int halfWidth = width / 2;
        int halfHeight = height / 2;
        int verticalOffset = (int) (height * 0.2);
        int centerYAdjusted = center.y - halfHeight + verticalOffset;
        return new Rectangle(center.x - halfWidth, centerYAdjusted - halfHeight, width, height);
    }

    public static boolean checkSecondListInsideFirstList(List<MapObject> list1, List<MapObject> list2) {
        if (list1.size() < list2.size()) return false;
        for (MapObject candidate : list2) {
            boolean found = false;
            for (MapObject existing : list1) {
                if (areObjectsEqual(existing, candidate)) {
                    found = true;
                    break;
                }
            }
            if (!found) return false;
        }
        return true;
    }

    private static boolean areObjectsEqual(MapObject first, MapObject second) {
        if (first == second) return true;
        if (!(first instanceof MapItem left) || !(second instanceof MapItem right)) return false;
        return left.getItemId() == right.getItemId()
                && left.getOwnerId() == right.getOwnerId()
                && left.getItem().getQuantity() == right.getItem().getQuantity();
    }
}
