package soloMapling.ArtificialPlayer.BotAttackSystem;

import client.Job;

/*
 * Original fixed-damage attack profile; the attack-plan concept is inspired by GreenCatMS. Credit: NutNNut for the idea.
 * One bot attack: its route, the skill that renders, how many mobs/lines it hits, its reach box,
 * and timing. Pure data - build them with the per-route factories (melee/meleeAoe/magic/ranged/...)
 * so reach/cooldown defaults stay in one place. Per-line damage is NOT a property of the profile;
 * it comes from the bot's job tier + level via BotDamageModel (see rollDamage). altSkillId covers
 * warrior skills with a second weapon form (sword vs axe, spear vs pole-arm).
 */
public final class BotAttackProfile {

    public enum Route { CLOSE, RANGED, MAGIC }

    public final Route route;
    public final int numAttacked;
    public final int numDamage;
    public final int reachX;
    public final int reachY;
    public final int cooldownMs;
    public final short hitDelayMs;
    public final int speed;
    public final int skillId;
    public final int skillLevel;
    public final int altSkillId;

    private BotAttackProfile(Route route, int numAttacked, int numDamage, int reachX, int reachY,
                             int cooldownMs, short hitDelayMs, int speed,
                             int skillId, int altSkillId) {
        this.route = route;
        this.numAttacked = numAttacked;
        this.numDamage = numDamage;
        this.reachX = reachX;
        this.reachY = reachY;
        this.cooldownMs = cooldownMs;
        this.hitDelayMs = hitDelayMs;
        this.speed = speed;
        this.skillId = skillId;
        this.skillLevel = skillId == 0 ? 0 : SKILL_LEVEL;
        this.altSkillId = altSkillId;
    }

    private static final int SKILL_LEVEL = 20;
    private static final int AOE_MOBS = 6;
    private static final int MELEE_SPEED = 4;

    public static BotAttackProfile melee(int skill, int lines) {
        return new BotAttackProfile(Route.CLOSE, 1, lines, 90, 60, 720, (short) 300, MELEE_SPEED, skill, 0);
    }

    public static BotAttackProfile meleeVar(int skill, int altSkill, int lines) {
        return new BotAttackProfile(Route.CLOSE, 1, lines, 90, 60, 720, (short) 300, MELEE_SPEED, skill, altSkill);
    }

    public static BotAttackProfile meleeAoe(int skill, int lines) {
        return new BotAttackProfile(Route.CLOSE, AOE_MOBS, lines, 130, 80, 780, (short) 320, MELEE_SPEED, skill, 0);
    }

    public static BotAttackProfile meleeAoeVar(int skill, int altSkill, int lines) {
        return new BotAttackProfile(Route.CLOSE, AOE_MOBS, lines, 130, 80, 780, (short) 320, MELEE_SPEED, skill, altSkill);
    }

    public static BotAttackProfile meleeMultiVar(int skill, int altSkill, int mobs, int lines) {
        return new BotAttackProfile(Route.CLOSE, mobs, lines, 130, 80, 720, (short) 300, MELEE_SPEED, skill, altSkill);
    }

    public static BotAttackProfile basicSwing() {
        return new BotAttackProfile(Route.CLOSE, 1, 1, 90, 60, 720, (short) 300, MELEE_SPEED, 0, 0);
    }

    public static BotAttackProfile ranged(int skill, int lines) {
        return new BotAttackProfile(Route.RANGED, 1, lines, 450, 150, 780, (short) 340, MELEE_SPEED, skill, 0);
    }

    public static BotAttackProfile rangedAoe(int skill, int lines) {
        return new BotAttackProfile(Route.RANGED, AOE_MOBS, lines, 450, 200, 820, (short) 360, MELEE_SPEED, skill, 0);
    }

    public static BotAttackProfile magic(int skill, int lines) {
        return new BotAttackProfile(Route.MAGIC, 1, lines, 450, 150, 840, (short) 360, MELEE_SPEED, skill, 0);
    }

    public static BotAttackProfile magicAoe(int skill, int lines) {
        return new BotAttackProfile(Route.MAGIC, AOE_MOBS, lines, 450, 210, 900, (short) 380, MELEE_SPEED, skill, 0);
    }

    public int skillFor(client.inventory.WeaponType weapon) {
        return (altSkillId != 0 && BotAttackData.usesAltWarriorVariant(weapon)) ? altSkillId : skillId;
    }

    public int rollDamage(int level, Job job) {
        return BotDamageModel.rollLine(jobTier(job), level, numDamage);
    }

    /**
     * Cosmic's Job enum in EverLeaf predates SoloMapling's getJobTier() helper, so derive
     * the same 0..4 combat tier from the canonical v83 job ids.  Cygnus/Aran follow the
     * same x100/x10/final-digit progression; Evan's ten mastery stages are grouped into
     * four practical damage tiers.  GM jobs are treated as fourth-job for QA smoke damage.
     */
    static int jobTier(Job job) {
        if (job == null) {
            return 0;
        }

        int id = job.getId();
        if (job == Job.GM || job == Job.SUPERGM || job == Job.MAPLELEAF_BRIGADIER) {
            return 4;
        }
        if (job == Job.BEGINNER || job == Job.NOBLESSE || job == Job.LEGEND || job == Job.EVAN) {
            return 0;
        }

        // Evan mastery stages: 2200, 2210..2218.
        if (id == 2200) return 1;
        if (id >= 2210 && id <= 2212) return 2;
        if (id >= 2213 && id <= 2215) return 3;
        if (id >= 2216 && id <= 2218) return 4;

        // Ordinary, Cygnus and Aran families all encode advancement depth in the
        // trailing digits: x00 first, xx10 second, xx11 third, xx12 fourth.
        int lastTwo = id % 100;
        if (lastTwo == 0) return 1;
        if (lastTwo % 10 == 0) return 2;
        if (lastTwo % 10 == 1) return 3;
        if (lastTwo % 10 == 2) return 4;

        return 1;
    }
}
