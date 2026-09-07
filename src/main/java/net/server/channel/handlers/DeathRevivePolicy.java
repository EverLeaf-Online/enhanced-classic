package net.server.channel.handlers;

/**
 * Pure decision helper for death-map revival. Event scripts own whether the
 * standard revive path may continue; a Wheel may only keep the player on the
 * same map when that event still owns the character after its revive callback.
 */
final class DeathRevivePolicy {
    private DeathRevivePolicy() {
    }

    static boolean canUseWheel(
            boolean eventAllowsStandardPath,
            boolean wheelRequested,
            boolean hasWheel,
            boolean eventPresent,
            boolean eventStillOwnsPlayer) {
        if (!eventAllowsStandardPath || !wheelRequested || !hasWheel) {
            return false;
        }

        return !eventPresent || eventStillOwnsPlayer;
    }
}
