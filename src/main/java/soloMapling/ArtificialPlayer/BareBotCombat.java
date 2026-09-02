package soloMapling.ArtificialPlayer;

import client.Character;
import server.life.Monster;

import java.util.Comparator;

/**
 * Dependency-light combat probe used before SoloMapling's full class/skill attack
 * renderer is vendored. Damage goes through EverLeaf's normal MapleMap damage
 * path so attribution, death, EXP/drop handling and map cleanup are exercised.
 */
public final class BareBotCombat {
    private static final int DEFAULT_DAMAGE = 1;
    private static final int MAX_SMOKE_DAMAGE = 1_000_000;
    private static final double MAX_TARGET_DISTANCE_SQ = 700.0 * 700.0;

    private BareBotCombat() {
    }

    public record StrikeResult(boolean hit, boolean killed, String monsterName, int monsterId,
                               int damage, long remainingHp, String reason) {
        static StrikeResult miss(String reason) {
            return new StrikeResult(false, false, null, 0, 0, 0, reason);
        }
    }

    public static StrikeResult strikeNearest(Character bot) {
        return strikeNearest(bot, DEFAULT_DAMAGE);
    }

    public static StrikeResult strikeNearest(Character bot, int requestedDamage) {
        if (bot == null || bot.getMap() == null) {
            return StrikeResult.miss("bot or map is null");
        }
        if (requestedDamage < 1 || requestedDamage > MAX_SMOKE_DAMAGE) {
            return StrikeResult.miss("damage must be between 1 and " + MAX_SMOKE_DAMAGE);
        }

        Monster target = bot.getMap().getAllMonsters().stream()
                .filter(monster -> monster != null && monster.getHp() > 0)
                .filter(monster -> bot.getPosition().distanceSq(monster.getPosition()) <= MAX_TARGET_DISTANCE_SQ)
                .min(Comparator.comparingDouble(monster -> bot.getPosition().distanceSq(monster.getPosition())))
                .orElse(null);

        if (target == null) {
            return StrikeResult.miss("no living monster within 700px");
        }

        String name = target.getName();
        int monsterId = target.getId();
        boolean killed = bot.getMap().damageMonster(bot, target, requestedDamage);
        long remainingHp = killed ? 0 : Math.max(0, target.getHp());
        return new StrikeResult(true, killed, name, monsterId, requestedDamage, remainingHp, null);
    }
}
