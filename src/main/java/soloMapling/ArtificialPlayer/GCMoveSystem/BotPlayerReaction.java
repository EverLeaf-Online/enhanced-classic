package soloMapling.ArtificialPlayer.GCMoveSystem;

import client.Character;

/**
 * EverLeaf QA intentionally disables SoloMapling's ambient social-reaction layer.
 *
 * Automated gameplay validation needs deterministic movement/combat/travel, not
 * chat/emote behavior. This avoids importing the larger social-bot framework
 * while preserving the GCMove driver call site.
 */
final class BotPlayerReaction {
    private BotPlayerReaction() {
    }

    static void maybeReact(BotMovementState entry, Character bot) {
        // Deliberately disabled for deterministic QA bots.
    }
}
