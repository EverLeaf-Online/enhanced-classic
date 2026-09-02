package soloMapling.ArtificialPlayer.GCMoveSystem;

import client.Character;

import java.awt.Point;

/** Read-only runtime diagnostics for controlled EverLeaf SoloMapling staging smoke tests. */
public final class GCMovementDiagnostics {
    private GCMovementDiagnostics() {
    }

    public record Snapshot(
            boolean enabled,
            String mode,
            int mapId,
            Point position,
            Point target,
            String source,
            String navEdge,
            int targetRegionId,
            String lastDecision,
            String blockReason,
            int stuckMs,
            long progressAgeMs,
            boolean graphWarmupFallback) {
    }

    public static Snapshot snapshot(Character bot) {
        if (bot == null) {
            return new Snapshot(false, "NONE", -1, null, null, null, null, -1, "-", null, 0, -1L, false);
        }

        BotMovementState state = null;
        for (BotMovementState candidate : GCMovement.enabledStates()) {
            if (candidate.bot != null && candidate.bot.getId() == bot.getId()) {
                state = candidate;
                break;
            }
        }

        Point position = bot.getPosition() == null ? null : new Point(bot.getPosition());
        if (state == null) {
            return new Snapshot(false, "IDLE", bot.getMapId(), position, null, null, null, -1, "-", null, 0, -1L, false);
        }

        Point target = state.moveTarget == null ? null : new Point(state.moveTarget);
        String edge = state.navEdge == null
                ? null
                : state.navEdge.type + ":" + state.navEdge.fromRegionId + "->" + state.navEdge.toRegionId;
        long progressAge = state.moveProgressAtMs <= 0L
                ? -1L
                : Math.max(0L, System.currentTimeMillis() - state.moveProgressAtMs);

        return new Snapshot(
                true,
                mode(state),
                bot.getMapId(),
                position,
                target,
                state.moveTargetSource,
                edge,
                state.navTargetRegionId,
                state.lastNavDecision,
                state.lastEdgeBlockReason,
                state.stuckMs,
                progressAge,
                state.graphWarmupFallback);
    }

    public static String describe(Character bot) {
        Snapshot s = snapshot(bot);
        String position = point(s.position());
        String target = point(s.target());
        String edge = s.navEdge() == null ? "-" : s.navEdge();
        String source = s.source() == null ? "-" : s.source();
        String decision = s.lastDecision() == null ? "-" : s.lastDecision();
        String block = s.blockReason() == null ? "-" : s.blockReason();
        String progress = s.progressAgeMs() < 0 ? "-" : s.progressAgeMs() + "ms";
        return "GCMove diag: enabled=" + s.enabled()
                + " mode=" + s.mode()
                + " map=" + s.mapId()
                + " pos=" + position
                + " target=" + target
                + " source=" + source
                + " edge=" + edge
                + " targetRegion=" + s.targetRegionId()
                + " decision=" + decision
                + " block=" + block
                + " stuck=" + s.stuckMs() + "ms"
                + " progressAge=" + progress
                + " warmupFallback=" + s.graphWarmupFallback();
    }

    private static String mode(BotMovementState state) {
        if (state.climbing) return "CLIMB";
        if (state.swimming) return "SWIM";
        if (state.inAir) return "AIR";
        if (state.following) return "FOLLOW";
        if (state.coarseActive) return "COARSE";
        if (state.navEdge != null) return "NAV";
        if (state.moveTarget != null) return "MOVE";
        return "IDLE";
    }

    private static String point(Point point) {
        return point == null ? "-" : point.x + "," + point.y;
    }
}
