package soloMapling.ArtificialPlayer;

import client.Character;
import net.server.Server;
import net.server.channel.Channel;
import server.maps.MapItem;
import server.maps.MapObject;

import java.awt.Point;
import java.awt.Rectangle;
import java.util.List;
import java.util.Random;

/**
 * Dependency-light subset of SoloMapling's BotHelpers used by the staged
 * EverLeaf integration. Keep identity semantics compatible with upstream so
 * later framework slices can use the same bot detection rules.
 */
public final class BotHelpers {
    private BotHelpers() {
    }

    public static Character getCharFromChannelStorage(int cid) {
        if (cid < 1000) {
            cid += 20000;
        }
        Channel channel = Server.getInstance().getChannel(0, 1);
        if (channel == null) {
            return null;
        }
        Character character = channel.getPlayerStorage().getCharacterById(cid);
        return isBot(character) ? character : null;
    }

    public static boolean isBot(Character character) {
        return character != null && isBot(character.getId());
    }

    public static boolean isBot(int id) {
        return id > 20000 || id == 999;
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
        if (list1.size() < list2.size()) {
            return false;
        }
        for (MapObject candidate : list2) {
            boolean found = false;
            for (MapObject existing : list1) {
                if (areObjectsEqual(existing, candidate)) {
                    found = true;
                    break;
                }
            }
            if (!found) {
                return false;
            }
        }
        return true;
    }

    private static boolean areObjectsEqual(MapObject first, MapObject second) {
        if (first == second) {
            return true;
        }
        if (!(first instanceof MapItem left) || !(second instanceof MapItem right)) {
            return false;
        }
        return left.getItemId() == right.getItemId()
                && left.getOwnerId() == right.getOwnerId()
                && left.getItem().getQuantity() == right.getItem().getQuantity();
    }
}
