package soloMapling.server;

/**
 * EverLeaf compatibility policy for SoloMapling version filters.
 *
 * EverLeaf intentionally backports and adds content newer than strict stock
 * v83 data. GCMove may consult these helpers while building travel graphs, but
 * the QA integration must not silently hide valid EverLeaf NPCs or portals.
 */
public final class MapleVersionManager {
    private MapleVersionManager() {
    }

    public static int getVersion() {
        return 83;
    }

    public static int getItemPoolVersion() {
        return 83;
    }

    public static boolean isNPCinCurrentVersion(int npcId) {
        return true;
    }

    public static boolean isPortalinCurrentVersion(int portalId) {
        return true;
    }
}
