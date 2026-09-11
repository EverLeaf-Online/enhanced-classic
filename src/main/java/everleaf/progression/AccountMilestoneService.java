package everleaf.progression;

import javax.sql.DataSource;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;

/**
 * Computes bounded account-wide collection and alt-progression milestones from
 * authoritative persisted character state.
 */
public final class AccountMilestoneService {
    public static final int LINKED_CHARACTER_CAP = 4;
    public static final int LINKED_LEVEL_CAP_PER_CHARACTER = 200;

    private static final String MONSTER_BOOK_SQL = """
            SELECT COUNT(DISTINCT mb.cardid)
            FROM monsterbook mb
            INNER JOIN characters c ON c.id = mb.charid
            WHERE c.accountid = ? AND c.gm = 0 AND mb.level > 0
            """;

    private static final String QUEST_SQL = """
            SELECT COUNT(DISTINCT qs.quest)
            FROM queststatus qs
            INNER JOIN characters c ON c.id = qs.characterid
            WHERE c.accountid = ? AND c.gm = 0 AND qs.status = 2
            """;

    private static final String LINKED_LEVEL_SQL = """
            SELECT level
            FROM characters
            WHERE accountid = ? AND gm = 0
            ORDER BY level DESC, id ASC
            LIMIT 4
            """;

    private final DataSource dataSource;

    public AccountMilestoneService(DataSource dataSource) {
        if (dataSource == null) {
            throw new IllegalArgumentException("dataSource cannot be null");
        }
        this.dataSource = dataSource;
    }

    public AccountMilestoneSnapshot snapshot(int accountId) {
        if (accountId < 0) {
            throw new IllegalArgumentException("accountId cannot be negative");
        }

        try (Connection con = dataSource.getConnection()) {
            int cards = queryCount(con, MONSTER_BOOK_SQL, accountId);
            int quests = queryCount(con, QUEST_SQL, accountId);
            List<Integer> levels = queryLinkedLevels(con, accountId);
            return new AccountMilestoneSnapshot(
                    accountId,
                    cards,
                    quests,
                    linkedLevelScore(levels),
                    Math.min(levels.size(), LINKED_CHARACTER_CAP)
            );
        } catch (SQLException e) {
            throw new IllegalStateException("Unable to load account milestone progression", e);
        }
    }

    private static int queryCount(Connection con, String sql, int accountId) throws SQLException {
        try (PreparedStatement ps = con.prepareStatement(sql)) {
            ps.setInt(1, accountId);
            try (ResultSet rs = ps.executeQuery()) {
                return rs.next() ? rs.getInt(1) : 0;
            }
        }
    }

    private static List<Integer> queryLinkedLevels(Connection con, int accountId) throws SQLException {
        List<Integer> levels = new ArrayList<>(LINKED_CHARACTER_CAP);
        try (PreparedStatement ps = con.prepareStatement(LINKED_LEVEL_SQL)) {
            ps.setInt(1, accountId);
            try (ResultSet rs = ps.executeQuery()) {
                while (rs.next()) {
                    levels.add(Math.max(0, rs.getInt("level")));
                }
            }
        }
        return levels;
    }

    /**
     * Linked-level score uses only the four highest-level characters and caps
     * each character at level 200. The account can therefore earn at most 800
     * score and gains no extra power from creating an unlimited mule roster.
     */
    public static int linkedLevelScore(List<Integer> characterLevels) {
        if (characterLevels == null || characterLevels.isEmpty()) {
            return 0;
        }

        return characterLevels.stream()
                .filter(level -> level != null && level > 0)
                .sorted(Comparator.reverseOrder())
                .limit(LINKED_CHARACTER_CAP)
                .mapToInt(level -> Math.min(level, LINKED_LEVEL_CAP_PER_CHARACTER))
                .sum();
    }
}
