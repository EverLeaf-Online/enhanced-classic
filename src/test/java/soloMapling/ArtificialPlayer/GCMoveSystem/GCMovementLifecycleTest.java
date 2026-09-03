package soloMapling.ArtificialPlayer.GCMoveSystem;

import client.Character;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.Test;
import org.mockito.MockedStatic;
import soloMapling.ArtificialPlayer.BotMovementSystem.MovementCommands;

import java.awt.Point;
import java.lang.reflect.Field;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.mockStatic;
import static org.mockito.Mockito.when;

class GCMovementLifecycleTest {
    @AfterEach
    void clearStates() throws Exception {
        states().clear();
    }

    @Test
    void moveArmsStateAndDisableTearsItDown() {
        int botId = 900_000_201;
        Character bot = mock(Character.class);
        when(bot.getId()).thenReturn(botId);
        when(bot.getMap()).thenReturn(null);
        when(bot.getMapId()).thenReturn(100000000);
        when(bot.getPosition()).thenReturn(new Point(15, 25));

        // Capture the real base profile before BotMovementProfile's static methods
        // are mocked; invoking base() inside thenReturn() leaves Mockito with a
        // nested unfinished static stubbing operation.
        BotMovementProfile baseProfile = BotMovementProfile.base();

        try (MockedStatic<ObserverTracker> observer = mockStatic(ObserverTracker.class);
             MockedStatic<BotMovementProfile> profiles = mockStatic(BotMovementProfile.class);
             MockedStatic<GCMovementDriver> driver = mockStatic(GCMovementDriver.class);
             MockedStatic<MovementCommands> movementCommands = mockStatic(MovementCommands.class);
             MockedStatic<GCFollow> follow = mockStatic(GCFollow.class);
             MockedStatic<GCTravel> travel = mockStatic(GCTravel.class);
             MockedStatic<GCFidget> fidget = mockStatic(GCFidget.class)) {

            profiles.when(() -> BotMovementProfile.fromCharacter(bot)).thenReturn(baseProfile);

            GCMovement.move(bot, 315, 225);

            assertTrue(GCMovement.isEnabled(bot));
            GCMovementDiagnostics.Snapshot active = GCMovementDiagnostics.snapshot(bot);
            assertTrue(active.enabled());
            assertEquals("MOVE", active.mode());
            assertEquals(new Point(315, 225), active.target());
            assertEquals("gcmove", active.source());

            GCMovement.disable(bot);

            assertFalse(GCMovement.isEnabled(bot));
            GCMovementDiagnostics.Snapshot disabled = GCMovementDiagnostics.snapshot(bot);
            assertFalse(disabled.enabled());
            assertEquals("IDLE", disabled.mode());
        }
    }

    @SuppressWarnings("unchecked")
    private static Map<Integer, BotMovementState> states() throws Exception {
        Field field = GCMovement.class.getDeclaredField("STATES");
        field.setAccessible(true);
        return (Map<Integer, BotMovementState>) field.get(null);
    }
}
