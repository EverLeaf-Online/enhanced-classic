package soloMapling.ArtificialPlayer.BotAttackSystem;

import client.inventory.WeaponType;

import java.util.concurrent.ThreadLocalRandom;

/**
 * Basic attack body-action data ported from SoloMapling's BotAttackData.
 *
 * <p>The full donor attack profile registry can be layered on this without changing the
 * QA bot control surface. These canonical v83 action ids are enough to render the correct
 * basic attack family for the bot's equipped weapon while EverLeaf remains authoritative
 * for damage, EXP and drops.</p>
 */
public final class BotAttackData {
    public static final int FACING_RIGHT_MASK = 0x00;
    public static final int FACING_LEFT_MASK = 0x80;
    public static final int DEFAULT_ATTACK_SPEED = 4;

    private static final int SWING_O1 = 5;
    private static final int SWING_O2 = 6;
    private static final int SWING_O3 = 7;
    private static final int SWING_T1 = 9;
    private static final int SWING_T2 = 10;
    private static final int SWING_T3 = 11;
    private static final int SWING_P1 = 13;
    private static final int STAB_O1 = 16;
    private static final int STAB_O2 = 17;
    private static final int STAB_T1 = 19;
    private static final int SHOOT_1 = 22;
    private static final int SHOOT_2 = 23;
    private static final int CLAW_1 = 24;
    private static final int CLAW_2 = 25;
    private static final int CLAW_3 = 26;
    private static final int WAND_1 = 28;
    private static final int WAND_2 = 29;

    private static final int[] DEFAULT_1H = {STAB_O1, STAB_O2, SWING_O1, SWING_O2, SWING_O3};
    private static final int[] HEAVY_2H = {STAB_O1, STAB_O2, SWING_T1, SWING_T2, SWING_T3};
    private static final int[] POLEARM = {SWING_P1, STAB_T1};
    private static final int[] WAND = {WAND_1, WAND_2};
    private static final int[] CLAW = {CLAW_1, CLAW_2, CLAW_3};
    private static final int[] BOW = {SHOOT_1};
    private static final int[] CROSSBOW = {SHOOT_2};

    private BotAttackData() {
    }

    public static int randomActionFor(WeaponType weaponType) {
        int[] variants = variantsFor(weaponType);
        return variants[ThreadLocalRandom.current().nextInt(variants.length)];
    }

    private static int[] variantsFor(WeaponType weaponType) {
        if (weaponType == null) {
            return DEFAULT_1H;
        }
        return switch (weaponType) {
            case SWORD2H, GENERAL2H_SWING, GENERAL2H_STAB -> HEAVY_2H;
            case SPEAR_SWING, SPEAR_STAB, POLE_ARM_SWING, POLE_ARM_STAB -> POLEARM;
            case WAND, STAFF -> WAND;
            case CLAW -> CLAW;
            case BOW -> BOW;
            case CROSSBOW -> CROSSBOW;
            default -> DEFAULT_1H;
        };
    }
}
