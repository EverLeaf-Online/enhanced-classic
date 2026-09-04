package everleaf.content;

import tools.DatabaseConnection;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;

/** Character-scoped Knight Stronghold prerequisite progression. */
public final class EmpressStrongholdProgressService {
    public static final int FIRST_ADVANCED_KNIGHT = 8610010;
    public static final int LAST_ADVANCED_KNIGHT = 8610014;
    public static final int COMPLETE_MASK = 0b1_1111;

    private EmpressStrongholdProgressService() {
    }

    public static boolean start(int characterId) {
        String sql = "INSERT IGNORE INTO everleaf_empress_stronghold_progress (character_id, advanced_knight_mask) VALUES (?, 0)";
        try (Connection con = DatabaseConnection.getConnection();
             PreparedStatement ps = con.prepareStatement(sql)) {
            ps.setInt(1, characterId);
            ps.executeUpdate();
            return true;
        } catch (SQLException e) {
            e.printStackTrace();
            return false;
        }
    }

    public static boolean isStarted(int characterId) {
        return mask(characterId) >= 0;
    }

    public static boolean isComplete(int characterId) {
        return mask(characterId) == COMPLETE_MASK;
    }

    public static int mask(int characterId) {
        String sql = "SELECT advanced_knight_mask FROM everleaf_empress_stronghold_progress WHERE character_id = ?";
        try (Connection con = DatabaseConnection.getConnection();
             PreparedStatement ps = con.prepareStatement(sql)) {
            ps.setInt(1, characterId);
            try (ResultSet rs = ps.executeQuery()) {
                return rs.next() ? rs.getInt(1) : -1;
            }
        } catch (SQLException e) {
            e.printStackTrace();
            return -1;
        }
    }

    /**
     * Records one of Advanced Knights A-E. Returns true only when this kill
     * changes the character from incomplete to complete.
     */
    public static boolean recordAdvancedKnightKill(int characterId, int mobId) {
        if (mobId < FIRST_ADVANCED_KNIGHT || mobId > LAST_ADVANCED_KNIGHT) {
            return false;
        }

        int oldMask = mask(characterId);
        if (oldMask < 0 || oldMask == COMPLETE_MASK) {
            return false;
        }

        int bit = 1 << (mobId - FIRST_ADVANCED_KNIGHT);
        int newMask = oldMask | bit;
        String sql = "UPDATE everleaf_empress_stronghold_progress "
                + "SET advanced_knight_mask = ?, completed_at = CASE WHEN ? = ? THEN COALESCE(completed_at, CURRENT_TIMESTAMP) ELSE completed_at END "
                + "WHERE character_id = ?";
        try (Connection con = DatabaseConnection.getConnection();
             PreparedStatement ps = con.prepareStatement(sql)) {
            ps.setInt(1, newMask);
            ps.setInt(2, newMask);
            ps.setInt(3, COMPLETE_MASK);
            ps.setInt(4, characterId);
            ps.executeUpdate();
            return oldMask != COMPLETE_MASK && newMask == COMPLETE_MASK;
        } catch (SQLException e) {
            e.printStackTrace();
            return false;
        }
    }

    public static String statusText(int characterId) {
        int mask = mask(characterId);
        if (mask < 0) {
            return "Not started";
        }
        if (mask == COMPLETE_MASK) {
            return "Complete - Empress expedition unlocked";
        }

        String[] names = {"Advanced Knight A", "Advanced Knight B", "Advanced Knight C", "Advanced Knight D", "Advanced Knight E"};
        StringBuilder out = new StringBuilder("Defeat one of each: ");
        for (int i = 0; i < names.length; i++) {
            if (i > 0) out.append(", ");
            out.append(names[i]).append((mask & (1 << i)) != 0 ? " [done]" : " [needed]");
        }
        return out.toString();
    }
}
