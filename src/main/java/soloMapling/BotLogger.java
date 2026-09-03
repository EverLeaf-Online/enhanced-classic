package soloMapling;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * SoloMapling logging compatibility routed through EverLeaf's normal logger
 * instead of writing an unmanaged BotLog.txt file in the server directory.
 */
public final class BotLogger {
    private static final Logger LOG = LoggerFactory.getLogger(BotLogger.class);

    private BotLogger() {
    }

    public static void log(String message) {
        LOG.debug("[SoloMapling] {}", message);
    }
}
