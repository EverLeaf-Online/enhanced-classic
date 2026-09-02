package soloMapling.server;

import java.util.concurrent.atomic.LongAdder;

/**
 * Minimal performance counters required by the staged GCMove QA runtime.
 * Additional SoloMapling-wide metrics remain out of scope until the wider
 * artificial-player scheduler is intentionally integrated.
 */
public final class BotPerfStats {
    public static final LongAdder MOVEMENT_TICKS = new LongAdder();

    private BotPerfStats() {
    }
}
