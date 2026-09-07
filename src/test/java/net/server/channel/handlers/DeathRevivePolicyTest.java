package net.server.channel.handlers;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

class DeathRevivePolicyTest {
    @Test
    void allowsNormalWheelReviveOutsideEvents() {
        assertTrue(DeathRevivePolicy.canUseWheel(true, true, true, false, false));
    }

    @Test
    void allowsWheelWhenEventExplicitlyContinuesAndStillOwnsPlayer() {
        assertTrue(DeathRevivePolicy.canUseWheel(true, true, true, true, true));
    }

    @Test
    void blocksWheelAfterEventCallbackUnregistersPlayer() {
        assertFalse(DeathRevivePolicy.canUseWheel(true, true, true, true, false));
    }

    @Test
    void blocksWheelWhenEventHandledReviveItself() {
        assertFalse(DeathRevivePolicy.canUseWheel(false, true, true, true, true));
    }

    @Test
    void blocksMissingItemAndUnrequestedWheel() {
        assertFalse(DeathRevivePolicy.canUseWheel(true, true, false, false, false));
        assertFalse(DeathRevivePolicy.canUseWheel(true, false, true, false, false));
    }
}
