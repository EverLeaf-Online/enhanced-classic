package server.maps;

/**
 * Represents a rope or ladder climbable object parsed from WZ ladderRope data.
 * isLadder is true when the WZ l field is 1, false for rope.
 */
public record Rope(int x, int y1, int y2, boolean isLadder) {
    public int topY() {
        return Math.min(y1, y2);
    }

    public int bottomY() {
        return Math.max(y1, y2);
    }
}
