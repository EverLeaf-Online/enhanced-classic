package service.enhanced;

import client.Job;

/**
 * Central Enhanced Classic level-cap policy.
 */
public final class LevelCapPolicy {
    public static final int PLAYER_MAX_LEVEL = 250;

    private LevelCapPolicy() {
    }

    public static int maxLevel(Job job) {
        return PLAYER_MAX_LEVEL;
    }
}
