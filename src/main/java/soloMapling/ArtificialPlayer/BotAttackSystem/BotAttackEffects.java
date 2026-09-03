package soloMapling.ArtificialPlayer.BotAttackSystem;

import client.Character;
import net.packet.Packet;
import net.server.channel.handlers.AbstractDealDamageHandler.AttackTarget;
import server.life.Monster;
import soloMapling.ArtificialPlayer.GCMoveSystem.GCMovement;
import tools.PacketCreator;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * EverLeaf reconciliation of SoloMapling's visible bot attack effects.
 *
 * <p>The donor packet construction is retained so clients see normal melee/ranged/magic
 * animations and damage lines. Actual HP/death/EXP/drop processing stays on EverLeaf's
 * authoritative MapleMap.damageMonster path instead of copying SoloMapling's older
 * custom drop implementation.</p>
 */
public final class BotAttackEffects {
    private BotAttackEffects() {}

    public static boolean meleeStrike(Character bot, Map<Monster, List<Integer>> hits, int skillId,
                                      int skillLevel, int bodyActionId, int facingMask, int speed, short hitDelay) {
        if (notReady(bot, hits)) return false;
        Packet packet = PacketCreator.closeRangeAttack(bot, skillId, skillLevel, facingMask,
                numAttackedAndDamage(hits), toTargets(hits, hitDelay), speed, bodyActionId, 0);
        return broadcastAndApply(bot, packet, hits);
    }

    public static boolean rangedStrike(Character bot, Map<Monster, List<Integer>> hits, int skillId,
                                       int skillLevel, int projectile, int bodyActionId, int facingMask,
                                       int speed, short hitDelay) {
        if (notReady(bot, hits)) return false;
        Packet packet = PacketCreator.rangedAttack(bot, skillId, skillLevel, facingMask,
                numAttackedAndDamage(hits), projectile, toTargets(hits, hitDelay), speed, bodyActionId, 0);
        return broadcastAndApply(bot, packet, hits);
    }

    public static boolean magicStrike(Character bot, Map<Monster, List<Integer>> hits, int skillId,
                                      int skillLevel, int bodyActionId, int facingMask, int speed, short hitDelay) {
        if (notReady(bot, hits)) return false;
        Packet packet = PacketCreator.magicAttack(bot, skillId, skillLevel, facingMask,
                numAttackedAndDamage(hits), toTargets(hits, hitDelay),
                BotAttackData.magicChargeFor(skillId), speed, bodyActionId, 0);
        return broadcastAndApply(bot, packet, hits);
    }

    private static boolean notReady(Character bot, Map<Monster, List<Integer>> hits) {
        return bot == null || bot.getMap() == null || hits == null || hits.isEmpty();
    }

    private static int numAttackedAndDamage(Map<Monster, List<Integer>> hits) {
        int numDamage = hits.values().iterator().next().size();
        return (hits.size() << 4) | numDamage;
    }

    private static Map<Integer, AttackTarget> toTargets(Map<Monster, List<Integer>> hits, short hitDelay) {
        Map<Integer, AttackTarget> targets = new HashMap<>();
        for (Map.Entry<Monster, List<Integer>> hit : hits.entrySet()) {
            targets.put(hit.getKey().getObjectId(), new AttackTarget(hitDelay, hit.getValue()));
        }
        return targets;
    }

    private static boolean broadcastAndApply(Character bot, Packet packet, Map<Monster, List<Integer>> hits) {
        bot.getMap().broadcastMessage(bot, packet, false);
        GCMovement.markAlerted(bot);
        boolean killedAny = false;
        for (Map.Entry<Monster, List<Integer>> hit : hits.entrySet()) {
            Monster target = hit.getKey();
            if (target == null || !target.isAlive()) continue;
            int total = 0;
            for (int line : hit.getValue()) {
                total += BotAttackData.decodeDamageLine(line);
            }
            long before = target.getHp();
            bot.getMap().damageMonster(bot, target, total);
            if (before > 0 && !target.isAlive()) {
                killedAny = true;
            }
        }
        return killedAny;
    }
}
