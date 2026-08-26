package everleaf.progression;

import java.util.List;

/** Fixed, reviewable phase timings for the first playable Rooted Zakum pass. */
public final class RootedZakumMechanicPolicy {
    private RootedZakumMechanicPolicy() {}

    public record AddWave(int phase, int delayMinutes, int monsterId, int count, int hitPoints) {
        public AddWave {
            if (phase < 1 || delayMinutes < 1 || monsterId < 1 || count < 1 || hitPoints < 1) {
                throw new IllegalArgumentException("invalid Rooted Zakum add wave");
            }
        }
    }

    private static final List<AddWave> WAVES = List.of(
            new AddWave(1, 7, 8140200, 4, 2_000_000),
            new AddWave(2, 14, 8140100, 6, 3_000_000),
            new AddWave(3, 21, 8140000, 8, 4_000_000)
    );

    public static List<AddWave> waves() { return WAVES; }
    public static int enrageWarningMinute() { return 25; }
    public static int hardEnrageMinute() { return 30; }
}
