package server;

/** WZ passive-defense x values encode remaining damage in thousandths. */
public final class PassiveDamageReduction {
    private PassiveDamageReduction() {}

    public static int apply(int damage, int remainingPermille) {
        // Negative values are protocol sentinels, not damage to be reduced.
        if (damage <= 0) {
            return damage;
        }
        int factor = Math.max(0, Math.min(1000, remainingPermille));
        return (int) ((long) damage * factor / 1000);
    }
}
