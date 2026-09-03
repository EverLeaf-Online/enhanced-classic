package soloMapling.ArtificialPlayer.BotAttackSystem;

import client.Job;
import client.inventory.WeaponType;
import constants.skills.Aran;
import constants.skills.Archer;
import constants.skills.Bandit;
import constants.skills.Bishop;
import constants.skills.BlazeWizard;
import constants.skills.Bowmaster;
import constants.skills.Brawler;
import constants.skills.Buccaneer;
import constants.skills.ChiefBandit;
import constants.skills.Cleric;
import constants.skills.Corsair;
import constants.skills.Crossbowman;
import constants.skills.Crusader;
import constants.skills.DawnWarrior;
import constants.skills.DragonKnight;
import constants.skills.Evan;
import constants.skills.FPArchMage;
import constants.skills.FPMage;
import constants.skills.FPWizard;
import constants.skills.Gunslinger;
import constants.skills.Hermit;
import constants.skills.Hero;
import constants.skills.Hunter;
import constants.skills.ILArchMage;
import constants.skills.ILMage;
import constants.skills.ILWizard;
import constants.skills.Magician;
import constants.skills.Marauder;
import constants.skills.Marksman;
import constants.skills.NightLord;
import constants.skills.NightWalker;
import constants.skills.Outlaw;
import constants.skills.Paladin;
import constants.skills.Pirate;
import constants.skills.Priest;
import constants.skills.Ranger;
import constants.skills.Rogue;
import constants.skills.Shadower;
import constants.skills.Sniper;
import constants.skills.ThunderBreaker;
import constants.skills.Warrior;
import constants.skills.WhiteKnight;
import constants.skills.WindArcher;

import java.util.EnumMap;
import java.util.Map;

import static soloMapling.ArtificialPlayer.BotAttackSystem.BotAttackProfile.magic;
import static soloMapling.ArtificialPlayer.BotAttackSystem.BotAttackProfile.magicAoe;
import static soloMapling.ArtificialPlayer.BotAttackSystem.BotAttackProfile.melee;
import static soloMapling.ArtificialPlayer.BotAttackSystem.BotAttackProfile.meleeAoe;
import static soloMapling.ArtificialPlayer.BotAttackSystem.BotAttackProfile.meleeAoeVar;
import static soloMapling.ArtificialPlayer.BotAttackSystem.BotAttackProfile.meleeMultiVar;
import static soloMapling.ArtificialPlayer.BotAttackSystem.BotAttackProfile.meleeVar;
import static soloMapling.ArtificialPlayer.BotAttackSystem.BotAttackProfile.ranged;
import static soloMapling.ArtificialPlayer.BotAttackSystem.BotAttackProfile.rangedAoe;

public final class BotAttackConfig {
    public record JobAttacks(BotAttackProfile single, BotAttackProfile aoe, BotAttackProfile ultimate) {}

    private static final Map<Job, JobAttacks> BY_JOB = new EnumMap<>(Job.class);
    private static final BotAttackProfile ROGUE_CLAW = ranged(Rogue.LUCKY_SEVEN, 2);
    private static final BotAttackProfile ROGUE_DAGGER = melee(Rogue.DOUBLE_STAB, 2);
    private static final BotAttackProfile CRUSHER = meleeMultiVar(DragonKnight.SPEAR_CRUSHER, DragonKnight.POLE_ARM_CRUSHER, 3, 3);

    static {
        put(Job.WARRIOR, melee(Warrior.POWER_STRIKE, 1), meleeAoe(Warrior.SLASH_BLAST, 1));
        put(Job.CRUSADER, meleeVar(Crusader.SWORD_PANIC, Crusader.AXE_PANIC, 1), meleeAoeVar(Crusader.SWORD_COMA, Crusader.AXE_COMA, 1));
        put(Job.WHITEKNIGHT, melee(WhiteKnight.CHARGE_BLOW, 1), null);
        put(Job.DRAGONKNIGHT, CRUSHER, CRUSHER, meleeAoe(DragonKnight.DRAGON_ROAR, 1));
        put(Job.HERO, melee(Hero.BRANDISH, 2), null);
        put(Job.PALADIN, melee(Paladin.BLAST, 1), meleeAoe(Paladin.HEAVENS_HAMMER, 1));

        put(Job.MAGICIAN, magic(Magician.MAGIC_CLAW, 2), null);
        put(Job.FP_WIZARD, magic(FPWizard.FIRE_ARROW, 1), null);
        put(Job.IL_WIZARD, magic(ILWizard.COLD_BEAM, 1), magicAoe(ILWizard.THUNDERBOLT, 1));
        put(Job.CLERIC, magic(Cleric.HOLY_ARROW, 1), null);
        put(Job.FP_MAGE, null, magicAoe(FPMage.EXPLOSION, 1));
        put(Job.IL_MAGE, magic(ILMage.THUNDER_SPEAR, 1), magicAoe(ILMage.ICE_STRIKE, 1));
        put(Job.PRIEST, null, magicAoe(Priest.SHINING_RAY, 1));
        put(Job.FP_ARCHMAGE, magic(FPArchMage.BIG_BANG, 1), null, magicAoe(FPArchMage.METEOR_SHOWER, 1));
        put(Job.IL_ARCHMAGE, magic(ILArchMage.BIG_BANG, 1), null, magicAoe(ILArchMage.BLIZZARD, 1));
        put(Job.BISHOP, magic(Bishop.ANGEL_RAY, 1), null, magicAoe(Bishop.GENESIS, 1));

        put(Job.BOWMAN, ranged(Archer.DOUBLE_SHOT, 2), null);
        put(Job.HUNTER, null, rangedAoe(Hunter.ARROW_BOMB, 1));
        put(Job.CROSSBOWMAN, null, rangedAoe(Crossbowman.IRON_ARROW, 1));
        put(Job.RANGER, ranged(Ranger.STRAFE, 4), rangedAoe(Ranger.ARROW_RAIN, 1));
        put(Job.SNIPER, ranged(Sniper.STRAFE, 4), rangedAoe(Sniper.ARROW_ERUPTION, 1));
        put(Job.BOWMASTER, ranged(Bowmaster.HURRICANE, 1), null);
        put(Job.MARKSMAN, ranged(Marksman.SNIPE, 1), null);

        put(Job.HERMIT, null, rangedAoe(Hermit.AVENGER, 1));
        put(Job.NIGHTLORD, ranged(NightLord.TRIPLE_THROW, 3), null);
        put(Job.BANDIT, melee(Bandit.SAVAGE_BLOW, 6), null);
        put(Job.CHIEFBANDIT, null, meleeAoe(ChiefBandit.BAND_OF_THIEVES, 1));
        put(Job.SHADOWER, melee(Shadower.ASSASSINATE, 3), meleeAoe(Shadower.BOOMERANG_STEP, 2));

        // Pirates: keep the same EverLeaf damage/death path as every other bot class.
        put(Job.PIRATE, ranged(Pirate.DOUBLE_SHOT, 2), meleeAoe(Pirate.SOMERSAULT_KICK, 1));
        put(Job.BRAWLER, melee(Brawler.DOUBLE_UPPERCUT, 2), meleeAoe(Brawler.BACK_SPIN_BLOW, 1));
        put(Job.MARAUDER, null, meleeAoe(Marauder.ENERGY_BLAST, 1));
        put(Job.BUCCANEER, melee(Buccaneer.BARRAGE, 6), meleeAoe(Buccaneer.DRAGON_STRIKE, 1));
        put(Job.GUNSLINGER, ranged(Gunslinger.INVISIBLE_SHOT, 1), rangedAoe(Gunslinger.GRENADE, 1));
        put(Job.OUTLAW, ranged(Pirate.DOUBLE_SHOT, 2), rangedAoe(Outlaw.FLAME_THROWER, 1));
        put(Job.CORSAIR, ranged(Corsair.RAPID_FIRE, 1), rangedAoe(Corsair.AERIAL_STRIKE, 1));

        // Cygnus Knights.
        put(Job.DAWNWARRIOR1, melee(DawnWarrior.POWER_STRIKE, 1), meleeAoe(DawnWarrior.SLASH_BLAST, 1));
        put(Job.DAWNWARRIOR2, null, meleeAoe(DawnWarrior.SOUL_BLADE, 1));
        put(Job.DAWNWARRIOR3, melee(DawnWarrior.BRANDISH, 2), meleeAoe(DawnWarrior.SOUL_DRIVER, 1));
        put(Job.DAWNWARRIOR4, melee(DawnWarrior.BRANDISH, 2), meleeAoe(DawnWarrior.SOUL_DRIVER, 1));

        put(Job.BLAZEWIZARD1, magic(BlazeWizard.MAGIC_CLAW, 2), null);
        put(Job.BLAZEWIZARD2, magic(BlazeWizard.FIRE_ARROW, 1), magicAoe(BlazeWizard.FIRE_PILLAR, 1));
        put(Job.BLAZEWIZARD3, magic(BlazeWizard.FIRE_STRIKE, 1), null, magicAoe(BlazeWizard.METEOR_SHOWER, 1));
        put(Job.BLAZEWIZARD4, magic(BlazeWizard.FIRE_STRIKE, 1), null, magicAoe(BlazeWizard.METEOR_SHOWER, 1));

        put(Job.WINDARCHER1, ranged(WindArcher.DOUBLE_SHOT, 2), null);
        put(Job.WINDARCHER2, null, rangedAoe(WindArcher.STORM_BREAK, 1));
        put(Job.WINDARCHER3, ranged(WindArcher.STRAFE, 4), rangedAoe(WindArcher.ARROW_RAIN, 1));
        put(Job.WINDARCHER4, ranged(WindArcher.HURRICANE, 1), rangedAoe(WindArcher.ARROW_RAIN, 1));

        put(Job.NIGHTWALKER1, ranged(NightWalker.LUCKY_SEVEN, 2), null);
        put(Job.NIGHTWALKER2, null, rangedAoe(NightWalker.VAMPIRE, 1));
        put(Job.NIGHTWALKER3, ranged(NightWalker.TRIPLE_THROW, 3), rangedAoe(NightWalker.AVENGER, 1));
        put(Job.NIGHTWALKER4, ranged(NightWalker.TRIPLE_THROW, 3), rangedAoe(NightWalker.AVENGER, 1));

        put(Job.THUNDERBREAKER1, melee(ThunderBreaker.FIRST_STRIKE, 1), meleeAoe(ThunderBreaker.SOMERSAULT_KICK, 1));
        put(Job.THUNDERBREAKER2, null, meleeAoe(ThunderBreaker.ENERGY_BLAST, 1));
        put(Job.THUNDERBREAKER3, melee(ThunderBreaker.BARRAGE, 6), meleeAoe(ThunderBreaker.SHARK_WAVE, 1));
        put(Job.THUNDERBREAKER4, melee(ThunderBreaker.BARRAGE, 6), meleeAoe(ThunderBreaker.SHARK_WAVE, 1));

        // Aran. Combo-consumer finishers are deliberately avoided so the bot can exercise
        // ordinary sustained combat without inventing combo state.
        put(Job.ARAN1, melee(Aran.DOUBLE_SWING, 2), null);
        put(Job.ARAN2, melee(Aran.TRIPLE_SWING, 3), null);
        put(Job.ARAN3, melee(Aran.FULL_SWING, 3), meleeAoe(Aran.ROLLING_SPIN, 1));
        put(Job.ARAN4, melee(Aran.OVER_SWING, 3), meleeAoe(Aran.ROLLING_SPIN, 1));

        // Evan compatibility only; this does not touch the parked Evan content/progression work.
        put(Job.EVAN1, magic(Evan.MAGIC_MISSILE, 1), null);
        put(Job.EVAN2, magic(Evan.FIRE_CIRCLE, 1), magicAoe(Evan.FIRE_CIRCLE, 1));
        put(Job.EVAN3, magic(Evan.LIGHTNING_BOLT, 1), null);
        put(Job.EVAN4, magic(Evan.LIGHTNING_BOLT, 1), null);
        put(Job.EVAN5, magic(Evan.ICE_BREATH, 1), magicAoe(Evan.ICE_BREATH, 1));
        put(Job.EVAN6, magic(Evan.MAGIC_FLARE, 1), null);
        put(Job.EVAN7, magic(Evan.MAGIC_FLARE, 1), magicAoe(Evan.DRAGON_THRUST, 1));
        put(Job.EVAN8, magic(Evan.KILLER_WINGS, 1), magicAoe(Evan.FIRE_BREATH, 1));
        put(Job.EVAN9, magic(Evan.PHANTOM_IMPRINT, 1), magicAoe(Evan.EARTHQUAKE, 1));
        put(Job.EVAN10, magic(Evan.ILLUSION, 4), magicAoe(Evan.FLAME_WHEEL, 1), magicAoe(Evan.DARK_FOG, 1));
    }

    private BotAttackConfig() {}

    private static final double CRIT_THIEF = 0.50;
    private static final double CRIT_BOWMAN = 0.50;
    private static final double CRIT_WARRIOR = 0.01;
    private static final double CRIT_MAGE = 0.01;
    private static final double CRIT_DEFAULT = 0.01;
    public static final double CRIT_MULTIPLIER = 1.5;

    public static double critChanceFor(Job job) {
        if (job == null) return 0.0;
        if (job.isA(Job.ASSASSIN) || job.isA(Job.HERMIT) || job.isA(Job.NIGHTLORD)
                || job.isA(Job.NIGHTWALKER1)) return CRIT_THIEF;
        if (job.isA(Job.BOWMAN) || job.isA(Job.WINDARCHER1)) return CRIT_BOWMAN;
        if (job.isA(Job.WARRIOR) || job.isA(Job.DAWNWARRIOR1) || job.isA(Job.ARAN1)) return CRIT_WARRIOR;
        if (job.isA(Job.MAGICIAN) || job.isA(Job.BLAZEWIZARD1) || job.isA(Job.EVAN1)) return CRIT_MAGE;
        return CRIT_DEFAULT;
    }

    private static void put(Job job, BotAttackProfile single, BotAttackProfile aoe) {
        put(job, single, aoe, null);
    }

    private static void put(Job job, BotAttackProfile single, BotAttackProfile aoe, BotAttackProfile ultimate) {
        BY_JOB.put(job, new JobAttacks(single, aoe, ultimate));
    }

    public static JobAttacks resolve(Job job, WeaponType weapon) {
        if (job == null) return new JobAttacks(null, null, null);
        BotAttackProfile single = null, aoe = null, ultimate = null;
        int bestSingleId = -1, bestAoeId = -1, bestUltId = -1;
        for (Map.Entry<Job, JobAttacks> entry : BY_JOB.entrySet()) {
            Job j = entry.getKey();
            if (!job.isA(j)) continue;
            JobAttacks a = entry.getValue();
            if (a.single() != null && j.getId() > bestSingleId) { single = a.single(); bestSingleId = j.getId(); }
            if (a.aoe() != null && j.getId() > bestAoeId) { aoe = a.aoe(); bestAoeId = j.getId(); }
            if (a.ultimate() != null && j.getId() > bestUltId) { ultimate = a.ultimate(); bestUltId = j.getId(); }
        }
        if (single == null && job.isA(Job.THIEF)) {
            single = (weapon == WeaponType.CLAW) ? ROGUE_CLAW : ROGUE_DAGGER;
        }
        if (single == null && aoe == null && ultimate == null) {
            single = BotAttackProfile.basicSwing();
        }
        return new JobAttacks(single, aoe, ultimate);
    }
}
