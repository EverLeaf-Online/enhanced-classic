package soloMapling.ArtificialPlayer.GCMoveSystem;

import client.Character;
import server.life.Monster;
import server.maps.MapleMap;

import java.util.ArrayDeque;
import java.util.HashSet;
import java.util.Set;

/**
 * Conservative level-aware training-map selector for controlled SoloMapling QA bots.
 *
 * <p>The selector never uses a hard-coded progression table. It searches only maps that
 * are portal-reachable from the bot's current training area, loads those maps through the
 * same channel map factory used by real players, and scores their currently configured mob
 * levels against the bot's level. If no clearly better candidate exists, the bot stays put.</p>
 */
public final class BotTrainingMapSelector {
    private static final int SEARCH_DEPTH = 3;
    private static final int MAX_VISITED = 80;
    private static final int MIN_IMPROVEMENT = 3;

    private BotTrainingMapSelector() {}

    public static int select(Character bot, int currentTrainingMapId) {
        if (bot == null || bot.getMap() == null) return currentTrainingMapId;
        int playerLevel = Math.max(1, bot.getLevel());
        Candidate current = candidate(bot, currentTrainingMapId, playerLevel);
        int currentScore = current == null ? Integer.MAX_VALUE : current.score();
        Candidate best = current;

        Set<Integer> visited = new HashSet<>();
        ArrayDeque<Node> queue = new ArrayDeque<>();
        visited.add(currentTrainingMapId);
        queue.add(new Node(currentTrainingMapId, 0));

        while (!queue.isEmpty() && visited.size() <= MAX_VISITED) {
            Node node = queue.removeFirst();
            if (node.depth() >= SEARCH_DEPTH) continue;
            int[] neighbors = GCWorldGraph.get().getOrDefault(node.mapId(), new int[0]);
            for (int mapId : neighbors) {
                if (!visited.add(mapId)) continue;
                Candidate candidate = candidate(bot, mapId, playerLevel);
                if (candidate != null && (best == null || candidate.score() < best.score())) best = candidate;
                queue.addLast(new Node(mapId, node.depth() + 1));
                if (visited.size() >= MAX_VISITED) break;
            }
        }

        if (best == null) return currentTrainingMapId;
        if (best.mapId() == currentTrainingMapId) return currentTrainingMapId;
        return best.score() + MIN_IMPROVEMENT <= currentScore ? best.mapId() : currentTrainingMapId;
    }

    private static Candidate candidate(Character bot, int mapId, int playerLevel) {
        try {
            MapleMap map = bot.getWarpMap(mapId);
            if (map == null) return null;
            int count = 0;
            int total = 0;
            for (Monster monster : map.getAllMonsters()) {
                if (monster == null || monster.getStats() == null) continue;
                int level = monster.getStats().getLevel();
                if (level <= 0) continue;
                total += level;
                count++;
            }
            if (count == 0) return null;
            int average = Math.max(1, total / count);
            return new Candidate(mapId, average, score(playerLevel, average));
        } catch (RuntimeException ignored) {
            return null;
        }
    }

    static int score(int playerLevel, int monsterLevel) {
        int delta = Math.abs(playerLevel - monsterLevel);
        int tooHigh = monsterLevel > playerLevel + 8 ? 60 + (monsterLevel - playerLevel) * 4 : 0;
        int tooLow = monsterLevel < Math.max(1, playerLevel - 15) ? 20 + (playerLevel - monsterLevel) : 0;
        return delta + tooHigh + tooLow;
    }

    private record Node(int mapId, int depth) {}
    private record Candidate(int mapId, int averageMobLevel, int score) {}
}
