package soloMapling.ArtificialPlayer;

import client.Character;

/**
 * Minimal GCMove map-entry compatibility hook.
 *
 * EverLeaf QA bots currently run without SoloMapling's macro/FSM scheduler, so
 * there is no macro brain to nudge on arrival. Keeping this hook explicit lets
 * GCMove preserve its call site without importing the event/social scheduler.
 */
public final class BotMapEntryResponder {
    private BotMapEntryResponder() {
    }

    public static void onBotArrivedObserved(Character bot) {
        // No-op until the wider SoloMapling macro scheduler is intentionally enabled.
    }
}
