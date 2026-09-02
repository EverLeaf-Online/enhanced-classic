package soloMapling.ArtificialPlayer;

import client.Character;
import client.Job;
import client.Skill;
import client.SkillFactory;
import soloMapling.ArtificialPlayer.BotAttackSystem.BotAttackConfig;
import soloMapling.ArtificialPlayer.BotAttackSystem.BotAttackProfile;
import soloMapling.ArtificialPlayer.BotAttackSystem.BotBuffConfig;

import java.util.LinkedHashSet;
import java.util.Set;

/** Converts only the synthetic QA clone into a deterministic combat-class profile. */
public final class BotQaProfile {
    private BotQaProfile() {}

    public static ProfileResult apply(Character bot, int jobId) {
        if (bot == null || !BotHelpers.isBot(bot)) return new ProfileResult(false, null, 0, "not-a-bot");
        Job job = Job.getById(jobId);
        if (job == null || job == Job.GM || job == Job.SUPERGM || job == Job.MAPLELEAF_BRIGADIER) {
            return new ProfileResult(false, null, 0, "unsupported-job");
        }

        bot.changeJob(job);
        Set<Integer> skillIds = new LinkedHashSet<>();
        BotAttackConfig.JobAttacks attacks = BotAttackConfig.resolve(job, null);
        collect(skillIds, attacks.single());
        collect(skillIds, attacks.aoe());
        collect(skillIds, attacks.ultimate());
        skillIds.addAll(BotBuffConfig.buffsForJob(job));

        int learned = 0;
        for (int skillId : skillIds) {
            if (skillId <= 0) continue;
            Skill skill = SkillFactory.getSkill(skillId);
            if (skill == null || skill.getMaxLevel() <= 0) continue;
            int max = skill.getMaxLevel();
            bot.changeSkillLevel(skill, (byte) max, max, -1L);
            learned++;
        }
        BotAttackSystemCleanup.clear(bot);
        return new ProfileResult(true, job, learned, "applied");
    }

    private static void collect(Set<Integer> ids, BotAttackProfile profile) {
        if (profile == null) return;
        if (profile.skillId > 0) ids.add(profile.skillId);
        if (profile.altSkillId > 0) ids.add(profile.altSkillId);
    }

    private static final class BotAttackSystemCleanup {
        private static void clear(Character bot) {
            soloMapling.ArtificialPlayer.BotAttackSystem.BotAttackDriver.clearBot(bot.getId());
            BotBuffDriver.clearBot(bot.getId());
        }
    }

    public record ProfileResult(boolean applied, Job job, int learnedSkills, String reason) {}
}
