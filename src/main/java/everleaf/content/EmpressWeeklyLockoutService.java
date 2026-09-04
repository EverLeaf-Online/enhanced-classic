package everleaf.content;

import everleaf.progression.WeeklyWindow;
import tools.DatabaseConnection;

import java.sql.Connection;
import java.sql.Date;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.time.Instant;

/**
 * Account-scoped weekly Empress clear lockout.
 *
 * A clear is recorded only after final Cygnus (8850011) dies. Entry checks use
 * the same Monday 00:00 UTC window as EverLeaf's other weekly progression.
 */
public final class EmpressWeeklyLockoutService {
    private EmpressWeeklyLockoutService() {
    }

    public static boolean canEnter(int accountId) {
        return !hasClearedThisWeek(accountId);
    }

    public static boolean hasClearedThisWeek(int accountId) {
        WeeklyWindow window = WeeklyWindow.forInstant(Instant.now());
        String sql = "SELECT 1 FROM everleaf_empress_weekly_clear WHERE account_id = ? AND week_start_utc = ? LIMIT 1";

        try (Connection con = DatabaseConnection.getConnection();
             PreparedStatement ps = con.prepareStatement(sql)) {
            ps.setInt(1, accountId);
            ps.setDate(2, Date.valueOf(window.startDate()));
            try (ResultSet rs = ps.executeQuery()) {
                return rs.next();
            }
        } catch (SQLException e) {
            // Fail closed: a persistence outage must not create duplicate weekly
            // reward eligibility. Operators can inspect the server SQL error.
            e.printStackTrace();
            return true;
        }
    }

    public static boolean markClear(int accountId) {
        WeeklyWindow window = WeeklyWindow.forInstant(Instant.now());
        String sql = "INSERT IGNORE INTO everleaf_empress_weekly_clear (account_id, week_start_utc) VALUES (?, ?)";

        try (Connection con = DatabaseConnection.getConnection();
             PreparedStatement ps = con.prepareStatement(sql)) {
            ps.setInt(1, accountId);
            ps.setDate(2, Date.valueOf(window.startDate()));
            return ps.executeUpdate() > 0;
        } catch (SQLException e) {
            e.printStackTrace();
            return false;
        }
    }
}
