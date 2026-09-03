package soloMapling.ArtificialPlayer.GCMoveSystem;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertTrue;

class BotTrainingMapSelectorTest {
    @Test
    void prefersMonstersNearPlayerLevel() {
        int player = 50;
        int near = BotTrainingMapSelector.score(player, 48);
        int low = BotTrainingMapSelector.score(player, 20);
        int high = BotTrainingMapSelector.score(player, 75);
        assertTrue(near < low);
        assertTrue(near < high);
    }

    @Test
    void penalizesDangerousOverlevelMapsMoreThanSmallLevelGaps() {
        int player = 30;
        assertTrue(BotTrainingMapSelector.score(player, 38) < BotTrainingMapSelector.score(player, 50));
    }

    @Test
    void keepsSlightlyLowerMobsViable() {
        int player = 70;
        assertTrue(BotTrainingMapSelector.score(player, 62) < BotTrainingMapSelector.score(player, 40));
    }
}
