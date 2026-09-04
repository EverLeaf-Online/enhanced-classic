package soloMapling.ArtificialPlayer;

import client.Character;
import client.Skill;
import client.SkillFactory;
import server.StatEffect;
import soloMapling.ArtificialPlayer.BotAttackSystem.BotBuffConfig;

import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

/** Applies only buffs the cloned QA character has actually learned. */
public final class BotBuffDriver {
    private static final long MIN_RETRY_MS = 5_000L;
    private static final long EARLY_REBUFF_MS = 5_000L;
    private static final Map<Long, Long> nextAttemptAt = new ConcurrentHashMap<>();

    private BotBuffDriver() {}

    public static BuffResult tick(Character bot) {
        if (bot == null || !BotHelpers.isBot(bot) || !bot.isAlive()) {
            return BuffResult.none("not-eligible");
        }

        long now = System.currentTimeMillis();
        for (int skillId : BotBuffConfig.buffsForJob(bot.getJob())) {
            long key = (((long) bot.getId()) << 32) ^ (skillId & 0xffffffffL);
            if (now < nextAttemptAt.getOrDefault(key, 0L)) continue;

            Skill skill;
            try {
                skill = SkillFactory.getSkill(skillId);
            } catch (RuntimeException ex) {
                nextAttemptAt.put(key, now + MIN_RETRY_MS);
                continue;
            }
            if (skill == null) {
                nextAttemptAt.put(key, now + MIN_RETRY_MS);
                continue;
            }
            int level = bot.getSkillLevel(skill);
            if (level <= 0) {
                nextAttemptAt.put(key, now + MIN_RETRY_MS);
                continue;
            }

            // Some imported/legacy skill definitions can resolve the Skill object while
            // still lacking a usable effect node for a learned level. Skill#getEffect
            // then fails inside StatEffect.loadFromData before applyTo() is reached.
            // A missing optional QA buff must not terminate the autonomous hunter.
            StatEffect effect;
            try {
                effect = skill.getEffect(level);
            } catch (RuntimeException ex) {
                nextAttemptAt.put(key, now + MIN_RETRY_MS);
                continue;
            }
            if (effect == null) {
                nextAttemptAt.put(key, now + MIN_RETRY_MS);
                continue;
            }

            boolean applied;
            try {
                applied = effect.applyTo(bot);
            } catch (RuntimeException ex) {
                nextAttemptAt.put(key, now + MIN_RETRY_MS);
                continue;
            }
            if (!applied) {
                nextAttemptAt.put(key, now + MIN_RETRY_MS);
                continue;
            }

            long durationMs = Math.max(MIN_RETRY_MS, effect.getDuration() * 1_000L);
            nextAttemptAt.put(key, now + Math.max(MIN_RETRY_MS, durationMs - EARLY_REBUFF_MS));
            return new BuffResult(true, skillId, level, "applied");
        }
        return BuffResult.none("nothing-due");
    }

    public static void clearBot(int botId) {
        long prefix = ((long) botId) << 32;
        nextAttemptAt.keySet().removeIf(key -> (key & 0xffffffff00000000L) == (prefix & 0xffffffff00000000L));
    }

    public static record BuffResult(boolean applied, int skillId, int level, String reason) {
        static BuffResult none(String reason) {
            return new BuffResult(false, 0, 0, reason);
        }
    }
}
