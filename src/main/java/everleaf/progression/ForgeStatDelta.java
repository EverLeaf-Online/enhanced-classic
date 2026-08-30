package everleaf.progression;

/**
 * Fixed stat changes applied by a deterministic Everleaf forge stage.
 * Zero-valued fields are intentionally allowed so recipes can target only the
 * stats appropriate for an equipment category.
 */
public record ForgeStatDelta(
        int str,
        int dex,
        int intel,
        int luk,
        int weaponAttack,
        int magicAttack,
        int weaponDefense,
        int magicDefense,
        int hp,
        int mp,
        int accuracy,
        int avoidability
) {
    public ForgeStatDelta {
        if (str < 0 || dex < 0 || intel < 0 || luk < 0 ||
                weaponAttack < 0 || magicAttack < 0 || weaponDefense < 0 || magicDefense < 0 ||
                hp < 0 || mp < 0 || accuracy < 0 || avoidability < 0) {
            throw new IllegalArgumentException("Forge deltas cannot reduce stats");
        }
    }

    public static ForgeStatDelta weaponStageOne() {
        return new ForgeStatDelta(2, 2, 2, 2, 3, 3, 0, 0, 50, 50, 5, 5);
    }

    public static ForgeStatDelta armorStageOne() {
        return new ForgeStatDelta(2, 2, 2, 2, 0, 0, 12, 12, 100, 50, 3, 3);
    }
}
