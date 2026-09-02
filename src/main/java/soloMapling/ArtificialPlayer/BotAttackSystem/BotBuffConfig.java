package soloMapling.ArtificialPlayer.BotAttackSystem;

import client.Job;
import constants.skills.Aran;
import constants.skills.Archer;
import constants.skills.Assassin;
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
import constants.skills.DarkKnight;
import constants.skills.DawnWarrior;
import constants.skills.DragonKnight;
import constants.skills.Evan;
import constants.skills.FPArchMage;
import constants.skills.FPMage;
import constants.skills.FPWizard;
import constants.skills.Fighter;
import constants.skills.Gunslinger;
import constants.skills.Hermit;
import constants.skills.Hero;
import constants.skills.Hunter;
import constants.skills.ILArchMage;
import constants.skills.ILMage;
import constants.skills.ILWizard;
import constants.skills.Magician;
import constants.skills.Marksman;
import constants.skills.NightLord;
import constants.skills.NightWalker;
import constants.skills.Page;
import constants.skills.Paladin;
import constants.skills.Priest;
import constants.skills.Shadower;
import constants.skills.Spearman;
import constants.skills.ThunderBreaker;
import constants.skills.Warrior;
import constants.skills.WhiteKnight;
import constants.skills.WindArcher;

import java.util.ArrayList;
import java.util.Collections;
import java.util.EnumMap;
import java.util.List;
import java.util.Map;

/** Learned self-buff registry used by the headless QA combat loop. */
public final class BotBuffConfig {
    private static final Map<Job, int[]> BUFFS_BY_JOB = new EnumMap<>(Job.class);

    static {
        put(Job.WARRIOR, Warrior.IRON_BODY);
        put(Job.MAGICIAN, Magician.MAGIC_GUARD, Magician.MAGIC_ARMOR);
        put(Job.BOWMAN, Archer.FOCUS);

        put(Job.FIGHTER, Fighter.RAGE, Fighter.POWER_GUARD, Fighter.SWORD_BOOSTER);
        put(Job.PAGE, Page.POWER_GUARD, Page.SWORD_BOOSTER);
        put(Job.SPEARMAN, Spearman.IRON_WILL, Spearman.HYPER_BODY, Spearman.SPEAR_BOOSTER);
        put(Job.FP_WIZARD, FPWizard.MEDITATION);
        put(Job.IL_WIZARD, ILWizard.MEDITATION);
        put(Job.CLERIC, Cleric.BLESS, Cleric.INVINCIBLE);
        put(Job.HUNTER, Hunter.SOUL_ARROW, Hunter.BOW_BOOSTER);
        put(Job.CROSSBOWMAN, Crossbowman.SOUL_ARROW, Crossbowman.CROSSBOW_BOOSTER);
        put(Job.ASSASSIN, Assassin.HASTE, Assassin.CLAW_BOOSTER);
        put(Job.BANDIT, Bandit.HASTE, Bandit.DAGGER_BOOSTER);

        put(Job.CRUSADER, Crusader.COMBO);
        put(Job.WHITEKNIGHT, WhiteKnight.SWORD_FIRE_CHARGE);
        put(Job.DRAGONKNIGHT, DragonKnight.DRAGON_BLOOD);
        put(Job.FP_MAGE, FPMage.SPELL_BOOSTER);
        put(Job.IL_MAGE, ILMage.SPELL_BOOSTER);
        put(Job.PRIEST, Priest.HOLY_SYMBOL);
        put(Job.HERMIT, Hermit.SHADOW_PARTNER, Hermit.MESO_UP);
        put(Job.CHIEFBANDIT, ChiefBandit.MESO_GUARD);

        put(Job.HERO, Hero.MAPLE_WARRIOR, Hero.ENRAGE);
        put(Job.PALADIN, Paladin.MAPLE_WARRIOR, Paladin.SWORD_HOLY_CHARGE);
        put(Job.DARKKNIGHT, DarkKnight.MAPLE_WARRIOR, DarkKnight.BERSERK);
        put(Job.FP_ARCHMAGE, FPArchMage.MAPLE_WARRIOR, FPArchMage.INFINITY, FPArchMage.MANA_REFLECTION);
        put(Job.IL_ARCHMAGE, ILArchMage.MAPLE_WARRIOR, ILArchMage.INFINITY, ILArchMage.MANA_REFLECTION);
        put(Job.BISHOP, Bishop.MAPLE_WARRIOR, Bishop.HOLY_SHIELD, Bishop.INFINITY, Bishop.MANA_REFLECTION);
        put(Job.BOWMASTER, Bowmaster.MAPLE_WARRIOR, Bowmaster.SHARP_EYES, Bowmaster.CONCENTRATE);
        put(Job.MARKSMAN, Marksman.MAPLE_WARRIOR, Marksman.SHARP_EYES);
        put(Job.NIGHTLORD, NightLord.MAPLE_WARRIOR, NightLord.SHADOW_STARS);
        put(Job.SHADOWER, Shadower.MAPLE_WARRIOR);

        put(Job.BRAWLER, Brawler.KNUCKLER_BOOSTER);
        put(Job.BUCCANEER, Buccaneer.MAPLE_WARRIOR, Buccaneer.SPEED_INFUSION);
        put(Job.GUNSLINGER, Gunslinger.GUN_BOOSTER);
        put(Job.CORSAIR, Corsair.MAPLE_WARRIOR, Corsair.SPEED_INFUSION);

        put(Job.DAWNWARRIOR1, DawnWarrior.IRON_BODY);
        put(Job.DAWNWARRIOR2, DawnWarrior.SWORD_BOOSTER, DawnWarrior.RAGE);
        put(Job.DAWNWARRIOR3, DawnWarrior.COMBO, DawnWarrior.SOUL_CHARGE);
        put(Job.BLAZEWIZARD1, BlazeWizard.MAGIC_GUARD, BlazeWizard.MAGIC_ARMOR);
        put(Job.BLAZEWIZARD2, BlazeWizard.MEDITATION, BlazeWizard.SPELL_BOOSTER);
        put(Job.WINDARCHER1, WindArcher.FOCUS);
        put(Job.WINDARCHER2, WindArcher.BOW_BOOSTER, WindArcher.SOUL_ARROW);
        put(Job.NIGHTWALKER2, NightWalker.CLAW_BOOSTER, NightWalker.HASTE);
        put(Job.NIGHTWALKER3, NightWalker.SHADOW_PARTNER);
        put(Job.THUNDERBREAKER2, ThunderBreaker.KNUCKLER_BOOSTER, ThunderBreaker.LIGHTNING_CHARGE);
        put(Job.THUNDERBREAKER3, ThunderBreaker.SPEED_INFUSION);

        put(Job.ARAN1, Aran.POLEARM_BOOSTER);
        put(Job.ARAN2, Aran.BODY_PRESSURE, Aran.COMBO_DRAIN);
        put(Job.ARAN3, Aran.SNOW_CHARGE, Aran.SMART_KNOCKBACK);
        put(Job.ARAN4, Aran.MAPLE_WARRIOR, Aran.FREEZE_STANDING, Aran.COMBO_BARRIER);

        put(Job.EVAN3, Evan.MAGIC_GUARD);
        put(Job.EVAN5, Evan.ELEMENTAL_RESET);
        put(Job.EVAN6, Evan.MAGIC_SHIELD);
        put(Job.EVAN7, Evan.MAGIC_BOOSTER);
        put(Job.EVAN8, Evan.MAGIC_RESISTANCE);
        put(Job.EVAN10, Evan.MAPLE_WARRIOR);
    }

    private BotBuffConfig() {}

    private static void put(Job job, int... skillIds) {
        BUFFS_BY_JOB.put(job, skillIds);
    }

    public static List<Integer> buffsForJob(Job job) {
        if (job == null) return Collections.emptyList();
        List<Integer> result = new ArrayList<>();
        for (Map.Entry<Job, int[]> entry : BUFFS_BY_JOB.entrySet()) {
            if (job.isA(entry.getKey())) {
                for (int id : entry.getValue()) result.add(id);
            }
        }
        return result;
    }
}
