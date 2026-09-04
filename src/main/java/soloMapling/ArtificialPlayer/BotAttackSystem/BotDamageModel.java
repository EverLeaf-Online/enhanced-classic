package soloMapling.ArtificialPlayer.BotAttackSystem;

import client.Character;
import client.Skill;
import client.SkillFactory;
import client.inventory.WeaponType;
import server.StatEffect;

import java.util.concurrent.ThreadLocalRandom;

/** Damage rolls for QA bots using the same Character base-damage inputs as normal EverLeaf combat. */
public final class BotDamageModel {
    private static final double MIN_VARIANCE = 0.80;
    private static final double MAX_VARIANCE = 1.00;

    private BotDamageModel() {}

    public static int rollLine(Character bot, BotAttackProfile profile, WeaponType weapon) {
        if (bot == null || profile == null) return 1;

        final int maxBase;
        if (profile.route == BotAttackProfile.Route.MAGIC) {
            int matk = Math.max(bot.getTotalMagic(), 14);
            maxBase = Math.max(1, bot.calculateMaxBaseMagicDamage(matk));
        } else {
            int watk = Math.max(bot.getTotalWatk(), 14);
            maxBase = weapon == null
                    ? Math.max(1, bot.calculateMaxBaseDamage(watk))
                    : Math.max(1, bot.calculateMaxBaseDamage(watk, weapon));
        }

        double skillMultiplier = 1.0;
        int skillId = profile.skillFor(weapon);
        if (skillId > 0) {
            Skill skill = SkillFactory.getSkill(skillId);
            if (skill != null) {
                int level = bot.getSkillLevel(skill);
                if (level > 0) {
                    StatEffect effect = skill.getEffect(level);
                    if (effect != null && effect.getDamage() > 0) {
                        skillMultiplier = effect.getDamage() / 100.0;
                    }
                }
            }
        }

        double variance = MIN_VARIANCE
                + ThreadLocalRandom.current().nextDouble() * (MAX_VARIANCE - MIN_VARIANCE);
        long rolled = Math.round(maxBase * skillMultiplier * variance);
        return (int) Math.max(1L, Math.min(Integer.MAX_VALUE, rolled));
    }
}
