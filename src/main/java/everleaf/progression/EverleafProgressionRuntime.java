package everleaf.progression;

import tools.DatabaseConnection;

/**
 * Lazy access point for Everleaf progression services after the main database
 * pool has been initialized by the server bootstrap.
 */
public final class EverleafProgressionRuntime {
    private EverleafProgressionRuntime() {
    }

    private static final class Holder {
        private static final WeeklyProgressRepository WEEKLY_REPOSITORY =
                new JdbcWeeklyProgressRepository(DatabaseConnection.getDataSource());
        private static final WeeklyProgressionService WEEKLY_SERVICE =
                new WeeklyProgressionService(WEEKLY_REPOSITORY);
    }

    public static WeeklyProgressionService weeklyService() {
        return Holder.WEEKLY_SERVICE;
    }

    public static WeeklyProgressRepository weeklyRepository() {
        return Holder.WEEKLY_REPOSITORY;
    }
}
