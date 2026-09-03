package soloMapling.ArtificialPlayer.BotTravelSystem;

import server.maps.MapleMap;
import server.maps.Portal;

import java.awt.Point;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * Curated scripted-portal edges needed by GCMove travel.
 *
 * EverLeaf keeps its own content policy authoritative; these edges supplement
 * the normal WZ portal graph without enforcing SoloMapling's old version gate.
 */
public final class BotScriptedWarp {
    private BotScriptedWarp() {
    }

    public record WarpEdge(int fromMapId, String portalName, int toMapId, int toPortalId) {
    }

    private static final WarpEdge[] EDGES = {
            new WarpEdge(103000100, "in00", 103000101, 3),
    };

    private static final Map<Integer, List<WarpEdge>> BY_FROM = buildEdges();

    private static Map<Integer, List<WarpEdge>> buildEdges() {
        Map<Integer, List<WarpEdge>> byFrom = new HashMap<>();
        for (WarpEdge edge : EDGES) {
            byFrom.computeIfAbsent(edge.fromMapId(), ignored -> new ArrayList<>()).add(edge);
        }
        Map<Integer, List<WarpEdge>> immutable = new HashMap<>();
        for (Map.Entry<Integer, List<WarpEdge>> entry : byFrom.entrySet()) {
            immutable.put(entry.getKey(), List.copyOf(entry.getValue()));
        }
        return Map.copyOf(immutable);
    }

    public static List<WarpEdge> from(int mapId) {
        return BY_FROM.getOrDefault(mapId, List.of());
    }

    public static WarpEdge edge(int fromMapId, int toMapId) {
        for (WarpEdge edge : from(fromMapId)) {
            if (edge.toMapId() == toMapId) {
                return edge;
            }
        }
        return null;
    }

    public static int[] destinations(int mapId) {
        List<WarpEdge> edges = from(mapId);
        int[] destinations = new int[edges.size()];
        for (int i = 0; i < edges.size(); i++) {
            destinations[i] = edges.get(i).toMapId();
        }
        return destinations;
    }

    public static Point portalPos(MapleMap map, String portalName) {
        if (map == null) {
            return null;
        }
        Portal portal = map.getPortal(portalName);
        return portal == null ? null : portal.getPosition();
    }
}
