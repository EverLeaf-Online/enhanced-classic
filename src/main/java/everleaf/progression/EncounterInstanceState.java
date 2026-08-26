package everleaf.progression;

/** Lifecycle for one dedicated Everleaf party encounter instance. */
public enum EncounterInstanceState {
    CREATED,
    ACTIVE,
    CLEARED,
    FAILED,
    EXPIRED,
    CANCELLED;

    public boolean terminal() {
        return this == CLEARED || this == FAILED || this == EXPIRED || this == CANCELLED;
    }
}
