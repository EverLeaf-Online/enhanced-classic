package service;

import client.Character;
import server.CashShop;
import tools.DatabaseConnection;

import java.sql.Connection;
import java.sql.Date;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.time.LocalDate;
import java.time.ZoneOffset;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;

/**
 * EverLeaf account-wide NX reward service.
 *
 * NX Credit is the canonical earnable balance. Rewards are account-scoped,
 * idempotent in SQL, and mirrored into the online character's CashShop object
 * so a later character save cannot overwrite a freshly granted balance.
 */
public final class NxRewardService {
    public static final int DAILY_NX = 1_000;
    public static final int SEVEN_DAY_STREAK_BONUS_NX = 1_000;
    public static final int PLAYTIME_STEP_SECONDS = 30 * 60;
    public static final int PLAYTIME_NX_PER_STEP = 500;
    public static final int PLAYTIME_MAX_STEPS_PER_DAY = 4;
    public static final int DEFAULT_VOTE_NX = 1_500;

    private static final NxRewardService INSTANCE = new NxRewardService();

    private final Map<Integer, SessionState> sessions = new ConcurrentHashMap<>();
    private final ScheduledExecutorService ticker = Executors.newSingleThreadScheduledExecutor(r -> {
        Thread t = new Thread(r, "everleaf-nx-rewards");
        t.setDaemon(true);
        return t;
    });

    private NxRewardService() {
        ticker.scheduleAtFixedRate(this::tickOnlineSessions, 60, 60, TimeUnit.SECONDS);
    }

    public static NxRewardService getInstance() {
        return INSTANCE;
    }

    public void startSession(Character player) {
        sessions.put(player.getAccountID(), new SessionState(player, System.currentTimeMillis()));
    }

    public RewardSummary claimAvailable(Character player) throws SQLException {
        int daily = claimDaily(player);
        int playtime = claimPlaytime(player);
        int votes = claimPendingVotes(player);
        return new RewardSummary(daily, playtime, votes, getStatus(player.getAccountID()));
    }

    public int claimDaily(Character player) throws SQLException {
        int accountId = player.getAccountID();
        LocalDate today = LocalDate.now(ZoneOffset.UTC);
        int reward = 0;

        try (Connection con = DatabaseConnection.getConnection()) {
            con.setAutoCommit(false);
            try {
                ensureAccountState(con, accountId, today);

                LocalDate lastDaily = null;
                int streak = 0;
                try (PreparedStatement ps = con.prepareStatement(
                        "SELECT last_daily_utc, daily_streak FROM everleaf_nx_rewards WHERE account_id=? FOR UPDATE")) {
                    ps.setInt(1, accountId);
                    try (ResultSet rs = ps.executeQuery()) {
                        if (rs.next()) {
                            Date d = rs.getDate("last_daily_utc");
                            lastDaily = d == null ? null : d.toLocalDate();
                            streak = rs.getInt("daily_streak");
                        }
                    }
                }

                if (!today.equals(lastDaily)) {
                    streak = today.minusDays(1).equals(lastDaily) ? streak + 1 : 1;
                    reward = DAILY_NX + (streak % 7 == 0 ? SEVEN_DAY_STREAK_BONUS_NX : 0);

                    try (PreparedStatement ps = con.prepareStatement(
                            "UPDATE everleaf_nx_rewards SET last_daily_utc=?, daily_streak=? WHERE account_id=?")) {
                        ps.setDate(1, Date.valueOf(today));
                        ps.setInt(2, streak);
                        ps.setInt(3, accountId);
                        ps.executeUpdate();
                    }
                    creditNx(con, accountId, reward);
                }

                con.commit();
            } catch (SQLException e) {
                con.rollback();
                throw e;
            } finally {
                con.setAutoCommit(true);
            }
        }

        mirrorOnlineCash(player, reward);
        return reward;
    }

    public int claimPlaytime(Character player) throws SQLException {
        SessionState session = sessions.computeIfAbsent(
                player.getAccountID(), id -> new SessionState(player, System.currentTimeMillis()));
        accrueSession(session);
        return claimPlaytimeSteps(player);
    }

    /**
     * Queue a verified vote without touching the account balance immediately.
     * A unique provider/external id pair makes retries idempotent. The online
     * player later claims it through @nx, keeping DB and CashShop memory synced.
     */
    public boolean queueVerifiedVote(int accountId, String provider, String externalVoteId) throws SQLException {
        return queueVerifiedVote(accountId, provider, externalVoteId, DEFAULT_VOTE_NX);
    }

    public boolean queueVerifiedVote(int accountId, String provider, String externalVoteId, int amount) throws SQLException {
        if (accountId <= 0 || provider == null || provider.isBlank() || externalVoteId == null || externalVoteId.isBlank()) {
            throw new IllegalArgumentException("Invalid vote reward identity");
        }
        if (amount <= 0 || amount > 100_000) {
            throw new IllegalArgumentException("Invalid vote reward amount");
        }

        try (Connection con = DatabaseConnection.getConnection();
             PreparedStatement ps = con.prepareStatement(
                     "INSERT IGNORE INTO everleaf_vote_rewards " +
                             "(account_id, provider, external_vote_id, nx_amount) VALUES (?, ?, ?, ?)")) {
            ps.setInt(1, accountId);
            ps.setString(2, provider);
            ps.setString(3, externalVoteId);
            ps.setInt(4, amount);
            return ps.executeUpdate() == 1;
        }
    }

    public RewardStatus getStatus(int accountId) throws SQLException {
        LocalDate today = LocalDate.now(ZoneOffset.UTC);
        try (Connection con = DatabaseConnection.getConnection()) {
            ensureAccountState(con, accountId, today);
            try (PreparedStatement ps = con.prepareStatement(
                    "SELECT last_daily_utc, daily_streak, playtime_date_utc, playtime_seconds, playtime_steps_claimed, " +
                            "(SELECT COALESCE(SUM(nx_amount),0) FROM everleaf_vote_rewards v WHERE v.account_id=r.account_id AND v.claimed_at IS NULL) pending_vote_nx " +
                            "FROM everleaf_nx_rewards r WHERE account_id=?")) {
                ps.setInt(1, accountId);
                try (ResultSet rs = ps.executeQuery()) {
                    if (!rs.next()) {
                        throw new SQLException("NX reward state missing for account " + accountId);
                    }
                    Date lastDailyDate = rs.getDate("last_daily_utc");
                    LocalDate lastDaily = lastDailyDate == null ? null : lastDailyDate.toLocalDate();
                    return new RewardStatus(
                            today.equals(lastDaily),
                            rs.getInt("daily_streak"),
                            rs.getInt("playtime_seconds"),
                            rs.getInt("playtime_steps_claimed"),
                            rs.getInt("pending_vote_nx"));
                }
            }
        }
    }

    private void tickOnlineSessions() {
        for (Map.Entry<Integer, SessionState> entry : sessions.entrySet()) {
            SessionState session = entry.getValue();
            Character player = session.player;
            try {
                if (player.getClient() == null || player.getClient().getPlayer() != player) {
                    sessions.remove(entry.getKey(), session);
                    continue;
                }
                accrueSession(session);
                int reward = claimPlaytimeSteps(player);
                if (reward > 0) {
                    player.yellowMessage("EverLeaf playtime reward: +" + reward + " NX Credit. Use @nx to view rewards.");
                }
            } catch (Exception ignored) {
                // Reward failures must never take down the game scheduler.
            }
        }
    }

    private void accrueSession(SessionState session) throws SQLException {
        long now = System.currentTimeMillis();
        long elapsedMillis = Math.max(0L, now - session.lastCheckpointMillis);
        int elapsedSeconds = (int) Math.min(Integer.MAX_VALUE, elapsedMillis / 1000L);
        if (elapsedSeconds < 1) {
            return;
        }
        session.lastCheckpointMillis += elapsedSeconds * 1000L;

        LocalDate today = LocalDate.now(ZoneOffset.UTC);
        try (Connection con = DatabaseConnection.getConnection()) {
            ensureAccountState(con, session.player.getAccountID(), today);
            try (PreparedStatement ps = con.prepareStatement(
                    "UPDATE everleaf_nx_rewards SET " +
                            "playtime_seconds = CASE WHEN playtime_date_utc=? THEN playtime_seconds + ? ELSE ? END, " +
                            "playtime_steps_claimed = CASE WHEN playtime_date_utc=? THEN playtime_steps_claimed ELSE 0 END, " +
                            "playtime_date_utc=? WHERE account_id=?")) {
                ps.setDate(1, Date.valueOf(today));
                ps.setInt(2, elapsedSeconds);
                ps.setInt(3, elapsedSeconds);
                ps.setDate(4, Date.valueOf(today));
                ps.setDate(5, Date.valueOf(today));
                ps.setInt(6, session.player.getAccountID());
                ps.executeUpdate();
            }
        }
    }

    private int claimPlaytimeSteps(Character player) throws SQLException {
        int accountId = player.getAccountID();
        LocalDate today = LocalDate.now(ZoneOffset.UTC);
        int reward = 0;

        try (Connection con = DatabaseConnection.getConnection()) {
            con.setAutoCommit(false);
            try {
                ensureAccountState(con, accountId, today);
                int seconds;
                int claimed;
                try (PreparedStatement ps = con.prepareStatement(
                        "SELECT playtime_date_utc, playtime_seconds, playtime_steps_claimed FROM everleaf_nx_rewards WHERE account_id=? FOR UPDATE")) {
                    ps.setInt(1, accountId);
                    try (ResultSet rs = ps.executeQuery()) {
                        rs.next();
                        Date date = rs.getDate("playtime_date_utc");
                        if (date == null || !today.equals(date.toLocalDate())) {
                            seconds = 0;
                            claimed = 0;
                        } else {
                            seconds = rs.getInt("playtime_seconds");
                            claimed = rs.getInt("playtime_steps_claimed");
                        }
                    }
                }

                int earnedSteps = Math.min(PLAYTIME_MAX_STEPS_PER_DAY, seconds / PLAYTIME_STEP_SECONDS);
                int newSteps = Math.max(0, earnedSteps - claimed);
                if (newSteps > 0) {
                    reward = newSteps * PLAYTIME_NX_PER_STEP;
                    try (PreparedStatement ps = con.prepareStatement(
                            "UPDATE everleaf_nx_rewards SET playtime_steps_claimed=? WHERE account_id=?")) {
                        ps.setInt(1, earnedSteps);
                        ps.setInt(2, accountId);
                        ps.executeUpdate();
                    }
                    creditNx(con, accountId, reward);
                }

                con.commit();
            } catch (SQLException e) {
                con.rollback();
                throw e;
            } finally {
                con.setAutoCommit(true);
            }
        }

        mirrorOnlineCash(player, reward);
        return reward;
    }

    private int claimPendingVotes(Character player) throws SQLException {
        int accountId = player.getAccountID();
        int reward = 0;

        try (Connection con = DatabaseConnection.getConnection()) {
            con.setAutoCommit(false);
            try {
                try (PreparedStatement ps = con.prepareStatement(
                        "SELECT COALESCE(SUM(nx_amount),0) total FROM everleaf_vote_rewards WHERE account_id=? AND claimed_at IS NULL FOR UPDATE")) {
                    ps.setInt(1, accountId);
                    try (ResultSet rs = ps.executeQuery()) {
                        rs.next();
                        reward = rs.getInt("total");
                    }
                }
                if (reward > 0) {
                    try (PreparedStatement ps = con.prepareStatement(
                            "UPDATE everleaf_vote_rewards SET claimed_at=CURRENT_TIMESTAMP WHERE account_id=? AND claimed_at IS NULL")) {
                        ps.setInt(1, accountId);
                        ps.executeUpdate();
                    }
                    creditNx(con, accountId, reward);
                }
                con.commit();
            } catch (SQLException e) {
                con.rollback();
                throw e;
            } finally {
                con.setAutoCommit(true);
            }
        }

        mirrorOnlineCash(player, reward);
        return reward;
    }

    private void ensureAccountState(Connection con, int accountId, LocalDate today) throws SQLException {
        try (PreparedStatement ps = con.prepareStatement(
                "INSERT IGNORE INTO everleaf_nx_rewards (account_id, playtime_date_utc) VALUES (?, ?)")) {
            ps.setInt(1, accountId);
            ps.setDate(2, Date.valueOf(today));
            ps.executeUpdate();
        }
    }

    private void creditNx(Connection con, int accountId, int amount) throws SQLException {
        if (amount <= 0) {
            return;
        }
        try (PreparedStatement ps = con.prepareStatement(
                "UPDATE accounts SET nxCredit=COALESCE(nxCredit,0)+? WHERE id=?")) {
            ps.setInt(1, amount);
            ps.setInt(2, accountId);
            if (ps.executeUpdate() != 1) {
                throw new SQLException("Could not credit NX for account " + accountId);
            }
        }
    }

    private void mirrorOnlineCash(Character player, int amount) {
        if (amount > 0 && player.getCashShop() != null) {
            player.getCashShop().gainCash(CashShop.NX_CREDIT, amount);
        }
    }

    private static final class SessionState {
        private final Character player;
        private volatile long lastCheckpointMillis;

        private SessionState(Character player, long lastCheckpointMillis) {
            this.player = player;
            this.lastCheckpointMillis = lastCheckpointMillis;
        }
    }

    public record RewardStatus(boolean dailyClaimedToday, int dailyStreak, int playtimeSecondsToday,
                               int playtimeStepsClaimedToday, int pendingVoteNx) {
    }

    public record RewardSummary(int dailyNx, int playtimeNx, int voteNx, RewardStatus status) {
        public int totalNx() {
            return dailyNx + playtimeNx + voteNx;
        }
    }
}
