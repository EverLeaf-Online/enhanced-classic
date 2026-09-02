package soloMapling.ArtificialPlayer.GCMoveSystem;

import client.Character;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.Test;

import java.awt.Point;
import java.lang.reflect.Field;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

class GCMovementDiagnosticsTest {
    @AfterEach
    void clearStates() throws Exception {
        states().clear();
    }

    @Test
    void reportsDisabledBotWithoutStartingRuntime() {
        Character bot = mock(Character.class);
        when(bot.getId()).thenReturn(900_000_100);
        when(bot.getMapId()).thenReturn(100000000);
        when(bot.getPosition()).thenReturn(new Point(25, 40));

        GCMovementDiagnostics.Snapshot snapshot = GCMovementDiagnostics.snapshot(bot);

        assertFalse(snapshot.enabled());
        assertEquals("IDLE", snapshot.mode());
        assertEquals(100000000, snapshot.mapId());
        assertEquals(new Point(25, 40), snapshot.position());
        assertEquals(-1L, snapshot.progressAgeMs());
    }

    @Test
    void exposesActiveNavigationEvidenceForStagingSmoke() throws Exception {
        int botId = 900_000_101;
        Character bot = mock(Character.class);
        when(bot.getId()).thenReturn(botId);
        when(bot.getMapId()).thenReturn(100000000);
        when(bot.getPosition()).thenReturn(new Point(120, 75));

        BotMovementState state = new BotMovementState(bot, null);
        state.moveTarget = new Point(420, 75);
        state.moveTargetPrecise = true;
        state.moveTargetSource = "gcmove";
        state.moveProgressAtMs = System.currentTimeMillis() - 250L;
        state.navTargetRegionId = 8;
        state.navEdge = new BotNavigationGraph.Edge(
                7,
                8,
                BotNavigationGraph.EdgeType.WALK,
                new Point(120, 75),
                new Point(420, 75),
                1,
                -1,
                0,
                0,
                0,
                900);
        state.lastNavDecision = "walk-right";
        state.lastEdgeBlockReason = "test-block";
        state.stuckMs = 120;
        state.graphWarmupFallback = true;
        states().put(botId, state);

        GCMovementDiagnostics.Snapshot snapshot = GCMovementDiagnostics.snapshot(bot);

        assertTrue(snapshot.enabled());
        assertEquals("NAV", snapshot.mode());
        assertEquals(new Point(420, 75), snapshot.target());
        assertEquals("gcmove", snapshot.source());
        assertEquals("WALK:7->8", snapshot.navEdge());
        assertEquals(8, snapshot.targetRegionId());
        assertEquals("walk-right", snapshot.lastDecision());
        assertEquals("test-block", snapshot.blockReason());
        assertEquals(120, snapshot.stuckMs());
        assertTrue(snapshot.progressAgeMs() >= 200L);
        assertTrue(snapshot.graphWarmupFallback());

        String report = GCMovementDiagnostics.describe(bot);
        assertNotNull(report);
        assertTrue(report.contains("mode=NAV"));
        assertTrue(report.contains("target=420,75"));
        assertTrue(report.contains("edge=WALK:7->8"));
        assertTrue(report.contains("targetRegion=8"));
        assertTrue(report.contains("warmupFallback=true"));
    }

    @SuppressWarnings("unchecked")
    private static Map<Integer, BotMovementState> states() throws Exception {
        Field field = GCMovement.class.getDeclaredField("STATES");
        field.setAccessible(true);
        return (Map<Integer, BotMovementState>) field.get(null);
    }
}
