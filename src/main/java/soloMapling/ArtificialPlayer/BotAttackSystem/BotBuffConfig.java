package soloMapling.ArtificialPlayer.BotAttackSystem;

import client.Job;
import constants.skills.Archer;
import constants.skills.Assassin;
import constants.skills.Bandit;
import constants.skills.Bishop;
import constants.skills.Bowmaster;
import constants.skills.ChiefBandit;
import constants.skills.Cleric;
import constants.skills.Crossbowman;
import constants.skills.Crusader;
import constants.skills.DarkKnight;
import constants.skills.DragonKnight;
import constants.skills.FPArchMage;
import constants.skills.FPMage;
import constants.skills.FPWizard;
import constants.skills.Fighter;
import constants.skills.Hermit;
import constants.skills.Hero;
import constants.skills.Hunter;
import constants.skills.ILArchMage;
import constants.skills.ILMage;
import constants.skills.ILWizard;
import constants.skills.Magician;
import constants.skills.Marksman;
import constants.skills.NightLord;
import constants.skills.Page;
import constants.skills.Paladin;
import constants.skills.Priest;
import constants.skills.Shadower;
import constants.skills.Spearman;
import constants.skills.Warrior;
import constants.skills.WhiteKnight;

import java.util.ArrayList;
import java.util.Collections;
import java.util.EnumMap;
import java.util.List;
import java.util.Map;

/** SoloMapling bot buff lineage registry used by combat rendering. */
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
