package soloMapling.ArtificialPlayer.GCMoveSystem;

import server.maps.MapleMap;

import java.awt.Point;
import java.util.List;

/**
 * Immutable analytic movement plan from SoloMapling's GCMove LOD layer.
 */
final class MovementPlan {
    enum Kind {
        IN_MAP,
        CROSS_MAP
    }

    final Kind kind;
    final int mapId;
    final List<BotNavigationGraph.Edge> edges;
    private final long[] cumStartMs;
    final long totalTimeMs;

    private MovementPlan(Kind kind, int mapId, List<BotNavigationGraph.Edge> edges,
                         long[] cumStartMs, long totalTimeMs) {
        this.kind = kind;
        this.mapId = mapId;
        this.edges = edges;
        this.cumStartMs = cumStartMs;
        this.totalTimeMs = totalTimeMs;
    }

    static MovementPlan inMap(int mapId, List<BotNavigationGraph.Edge> edges) {
        if (edges == null || edges.isEmpty()) {
            return null;
        }
        long[] cumStart = new long[edges.size()];
        long acc = 0;
        for (int i = 0; i < edges.size(); i++) {
            cumStart[i] = acc;
            acc += Math.max(0, edges.get(i).cost);
        }
        return new MovementPlan(Kind.IN_MAP, mapId, List.copyOf(edges), cumStart, acc);
    }

    /**
     * Build an analytic in-map plan from the same live navigation graph/pathfinder
     * used by the physics driver. Keeping this overload alongside the edge-list
     * constructor preserves EverLeaf's staged interpolation contract while making
     * the permanently vendored SoloMapling driver dependency-complete.
     */
    static MovementPlan inMap(BotNavigationGraph graph, MapleMap map, Point startPos, Point targetPos) {
        if (graph == null || map == null || startPos == null || targetPos == null) {
            return null;
        }
        int startRegion = graph.findRegionId(map, startPos);
        int targetRegion = graph.findRegionId(map, targetPos);
        if (startRegion < 0 || targetRegion < 0) {
            return null;
        }
        List<BotNavigationGraph.Edge> edges =
                BotNavigationManager.findPath(graph, map, startPos, startRegion, targetRegion, targetPos);
        return inMap(map.getId(), edges);
    }

    boolean isComplete(long elapsedMs) {
        return elapsedMs >= totalTimeMs;
    }

    Point positionAt(long elapsedMs) {
        if (edges.isEmpty()) {
            return null;
        }
        if (elapsedMs <= 0) {
            return new Point(edges.get(0).startPoint);
        }
        if (elapsedMs >= totalTimeMs) {
            return new Point(edges.get(edges.size() - 1).endPoint);
        }
        int i = edgeIndexAt(elapsedMs);
        BotNavigationGraph.Edge edge = edges.get(i);
        long into = elapsedMs - cumStartMs[i];
        long duration = Math.max(1, edge.cost);
        double t = Math.min(1.0, (double) into / duration);
        int x = (int) Math.round(edge.startPoint.x + (edge.endPoint.x - edge.startPoint.x) * t);
        int y = (int) Math.round(edge.startPoint.y + (edge.endPoint.y - edge.startPoint.y) * t);
        return new Point(x, y);
    }

    int edgeIndexAt(long elapsedMs) {
        int index = 0;
        for (int i = 0; i < edges.size(); i++) {
            if (elapsedMs >= cumStartMs[i]) {
                index = i;
            } else {
                break;
            }
        }
        return index;
    }
}
