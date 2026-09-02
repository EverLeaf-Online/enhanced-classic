package soloMapling.server;

import net.server.Server;
import net.server.channel.Channel;

public class SoloMaplingConstants {

    public static final Channel mainChannel = Server.getInstance().getChannel(0, 1);

    public static class GameConstants {
        public static final int WORLD_SCANIA = 0;
        public static final int CHANNEL_1 = 1;

        // EverLeaf reserves a high, in-memory-only range for artificial players.
        // Upstream SoloMapling starts near 20k, which can collide with legitimate
        // auto-increment character IDs on a long-running public server. This stays
        // below MapleMap's ~1,000,000,001 dynamic map-object OID range while still
        // satisfying SoloMapling's existing id > 20000 bot identity convention.
        public static final int BOT_BASE_ID = 900_000_000;
    }

}
