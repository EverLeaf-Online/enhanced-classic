package soloMapling.ArtificialPlayer.BotAttackSystem;

import client.Character;
import client.inventory.WeaponType;
import constants.id.ItemId;
import constants.skills.Bandit;
import constants.skills.Bishop;
import constants.skills.Cleric;
import constants.skills.DragonKnight;
import constants.skills.FPArchMage;
import constants.skills.FPMage;
import constants.skills.FPWizard;
import constants.skills.Hermit;
import constants.skills.Hero;
import constants.skills.ILArchMage;
import constants.skills.ILMage;
import constants.skills.Paladin;
import constants.skills.Priest;
import constants.skills.Rogue;
import constants.skills.Shadower;

import java.util.Map;
import java.util.Set;
import java.util.concurrent.ThreadLocalRandom;

/** EverLeaf-reconciled SoloMapling v0.3 bot attack packet/action data. */
public final class BotAttackData {
    private BotAttackData() {}

    public static final int FACING_RIGHT_MASK = 0x00;
    public static final int FACING_LEFT_MASK = 0x80;
    public static final int DEFAULT_ATTACK_SPEED = 4;

    private static final int SWING_O1 = 5, SWING_O2 = 6, SWING_O3 = 7;
    private static final int SWING_T1 = 9, SWING_T2 = 10, SWING_T3 = 11;
    private static final int SWING_P1 = 13, STAB_T1 = 19;
    private static final int STAB_O1 = 16, STAB_O2 = 17;
    private static final int SHOOT_1 = 22, SHOOT_2 = 23;
    private static final int CLAW_1 = 24, CLAW_2 = 25, CLAW_3 = 26;
    private static final int WAND_1 = 28, WAND_2 = 29;
    private static final int SAVAGE = 55;
    private static final int ALERT_3 = 42;
    private static final int MAGIC_1 = 49, MAGIC_2 = 50, MAGIC_3 = 51;
    private static final int BURSTER_2 = 54;
    private static final int AVENGER = 56;
    private static final int ALERT_5 = 44;
    private static final int ASSASSINATION = 59;
    private static final int BRANDISH_1 = 63;
    private static final int SANCTUARY = 65;
    private static final int METEOR = 66;
    private static final int BLIZZARD = 68;
    private static final int GENESIS = 69;
    private static final int BLAST = 71;

    private static final int[] DEFAULT_1H_VARIANTS = {STAB_O1, STAB_O2, SWING_O1, SWING_O2, SWING_O3};
    private static final int[] HEAVY_2H_VARIANTS = {STAB_O1, STAB_O2, SWING_T1, SWING_T2, SWING_T3};
    private static final int[] POLEARM_VARIANTS = {SWING_P1, STAB_T1};
    private static final int[] WAND_VARIANTS = {WAND_1, WAND_2};
    private static final int[] CLAW_VARIANTS = {CLAW_1, CLAW_2, CLAW_3};
    private static final int[] BOW_VARIANTS = {SHOOT_1};
    private static final int[] CROSSBOW_VARIANTS = {SHOOT_2};

    private static final Map<Integer, Integer> SKILL_ACTION = Map.ofEntries(
            Map.entry(Rogue.DOUBLE_STAB, STAB_O1),
            Map.entry(FPWizard.FIRE_ARROW, SHOOT_1),
            Map.entry(Cleric.HOLY_ARROW, SHOOT_1),
            Map.entry(Bandit.SAVAGE_BLOW, SAVAGE),
            Map.entry(Hermit.AVENGER, AVENGER),
            Map.entry(FPMage.EXPLOSION, MAGIC_3),
            Map.entry(ILMage.ICE_STRIKE, MAGIC_2),
            Map.entry(ILMage.THUNDER_SPEAR, MAGIC_1),
            Map.entry(Priest.SHINING_RAY, MAGIC_2),
            Map.entry(DragonKnight.DRAGON_ROAR, ALERT_3),
            Map.entry(DragonKnight.SPEAR_CRUSHER, BURSTER_2),
            Map.entry(DragonKnight.POLE_ARM_CRUSHER, BURSTER_2),
            Map.entry(Hero.BRANDISH, BRANDISH_1),
            Map.entry(Paladin.BLAST, BLAST),
            Map.entry(Paladin.HEAVENS_HAMMER, SANCTUARY),
            Map.entry(FPArchMage.METEOR_SHOWER, METEOR),
            Map.entry(ILArchMage.BLIZZARD, BLIZZARD),
            Map.entry(Bishop.ANGEL_RAY, SHOOT_1),
            Map.entry(Bishop.GENESIS, GENESIS),
            Map.entry(Shadower.ASSASSINATE, ASSASSINATION),
            Map.entry(Shadower.BOOMERANG_STEP, ALERT_5)
    );

    public static int actionFor(int skillId, WeaponType weaponType) {
        Integer override = SKILL_ACTION.get(skillId);
        return override != null ? override : randomActionFor(weaponType);
    }

    private static final int BIG_BANG_CHARGE = 1080;
    private static final Set<Integer> CHARGE_MAGIC_SKILLS =
            Set.of(FPArchMage.BIG_BANG, ILArchMage.BIG_BANG, Bishop.BIG_BANG);

    public static int magicChargeFor(int skillId) {
        return CHARGE_MAGIC_SKILLS.contains(skillId) ? BIG_BANG_CHARGE : -1;
    }

    public static int encodeCritLine(int rawDamage) {
        return -Integer.MAX_VALUE + rawDamage - 1;
    }

    public static int decodeDamageLine(int line) {
        return line < 0 ? line + Integer.MAX_VALUE : line;
    }

    public static int randomActionFor(WeaponType weaponType) {
        int[] variants = variantsFor(weaponType);
        return variants[ThreadLocalRandom.current().nextInt(variants.length)];
    }

    private static final int ARROW_FOR_BOW = 2060000;
    private static final int ARROW_FOR_CROSSBOW = 2061000;

    public static int projectileFor(WeaponType weaponType) {
        if (weaponType == null) return 0;
        return switch (weaponType) {
            case BOW -> ARROW_FOR_BOW;
            case CROSSBOW -> ARROW_FOR_CROSSBOW;
            case CLAW -> ItemId.SUBI_THROWING_STARS;
            case GUN -> ItemId.BULLET;
            default -> 0;
        };
    }

    /** QA bots currently use safe default ammo; richer star selection can layer on later. */
    public static int projectileFor(WeaponType weaponType, Character bot) {
        return projectileFor(weaponType);
    }

    public static boolean usesAltWarriorVariant(WeaponType weaponType) {
        if (weaponType == null) return false;
        return switch (weaponType) {
            case GENERAL1H_SWING, GENERAL1H_STAB, GENERAL2H_SWING, GENERAL2H_STAB,
                    POLE_ARM_SWING, POLE_ARM_STAB -> true;
            default -> false;
        };
    }

    private static int[] variantsFor(WeaponType weaponType) {
        if (weaponType == null) return DEFAULT_1H_VARIANTS;
        return switch (weaponType) {
            case SWORD2H, GENERAL2H_SWING, GENERAL2H_STAB -> HEAVY_2H_VARIANTS;
            case SPEAR_SWING, SPEAR_STAB, POLE_ARM_SWING, POLE_ARM_STAB -> POLEARM_VARIANTS;
            case WAND, STAFF -> WAND_VARIANTS;
            case CLAW -> CLAW_VARIANTS;
            case BOW -> BOW_VARIANTS;
            case CROSSBOW -> CROSSBOW_VARIANTS;
            default -> DEFAULT_1H_VARIANTS;
        };
    }
}
