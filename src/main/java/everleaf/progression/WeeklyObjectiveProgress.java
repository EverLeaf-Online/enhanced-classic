package everleaf.progression;

/**
 * Immutable objective-progress state suitable for DB persistence later.
 */
public record WeeklyObjectiveProgress(
        String weeklyKey,
        String objectiveId,
        int progress,
        boolean claimed
) {
    public WeeklyObjectiveProgress {
        if (weeklyKey == null || weeklyKey.isBlank()) throw new IllegalArgumentException("weeklyKey cannot be blank");
        WeeklyObjectiveDefinition definition = WeeklyObjectiveCatalog.byId(objectiveId);
        if (progress < 0 || progress > definition.targetCount()) {
            throw new IllegalArgumentException("progress outside objective target range");
        }
        if (claimed && progress < definition.targetCount()) {
            throw new IllegalArgumentException("incomplete objective cannot be claimed");
        }
    }

    public static WeeklyObjectiveProgress fresh(String weeklyKey, String objectiveId) {
        return new WeeklyObjectiveProgress(weeklyKey, objectiveId, 0, false);
    }

    public WeeklyObjectiveProgress addProgress(int amount) {
        if (amount <= 0 || claimed) return this;
        WeeklyObjectiveDefinition definition = WeeklyObjectiveCatalog.byId(objectiveId);
        return new WeeklyObjectiveProgress(
                weeklyKey,
                objectiveId,
                Math.min(definition.targetCount(), progress + amount),
                false
        );
    }

    public boolean complete() {
        return progress >= WeeklyObjectiveCatalog.byId(objectiveId).targetCount();
    }

    public WeeklyObjectiveProgress claim() {
        if (!complete()) throw new IllegalStateException("objective is not complete");
        if (claimed) return this;
        return new WeeklyObjectiveProgress(weeklyKey, objectiveId, progress, true);
    }
}
