package soloMapling.ArtificialPlayer.BotAttackSystem;

import client.Character;
import client.Job;
import client.inventory.WeaponType;
import constants.skills.Cleric;
import constants.skills.Hermit;
import server.life.Monster;
import server.maps.MapObject;
import server.maps.MapObjectType;
import soloMapling.ArtificialPlayer.BotCommandsPack.BotAttack;
import soloMapling.ArtificialPlayer.GCMoveSystem.GCMovement;

import java.awt.Point;
import java.awt.Rectangle;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ThreadLocalRandom;

/**
 * EverLeaf-reconciled SoloMapling class-aware attack driver.
 *
 * <p>Preserves the donor's job/weapon profiles, facing, AoE selection, cooldowns,
 * critical-line rendering and visible attack routes. Terrain and movement remain
 * owned by the already-integrated GCMove runtime.</p>
 */
public final class BotAttackDriver {
    private static final Map<Integer, Long> nextAttackByBot = new ConcurrentHashMap<>();
    private static final Map<Integer, Long> nextUltimateByBot = new ConcurrentHashMap<>();
    private static final long FULL_MAP_ULTIMATE_COOLDOWN_MS = 25_000;
    private static final int SEEK_RANGE = 700;
    private static final double SEEK_RANGE_SQ = (double) SEEK_RANGE * SEEK_RANGE;
    private static final int BACK_MARGIN = 25;
    private static final int BOSS_Y_PAD = 300;
    private static final BotAttackProfile HEAL_PROFILE = BotAttackProfile.magicAoe(Cleric.HEAL, 1);

    private BotAttackDriver() {}

    public record AttackResult(boolean hit, String monsterName, int damage, boolean killed, String reason) {
        static AttackResult hit(String name, int damage, boolean killed) {
            return new AttackResult(true, name, damage, killed, null);
        }
        static AttackResult miss(String reason) {
            return new AttackResult(false, null, 0, false, reason);
        }
    }

    public enum Choice { AUTO, SINGLE, AOE, ULTIMATE }

    public static AttackResult botAttack(Character bot) {
        return attack(bot, false, Choice.AUTO);
    }

    public static AttackResult forceSingle(Character bot) {
        return attack(bot, true, Choice.SINGLE);
    }

    public static AttackResult forceAoe(Character bot) {
        return attack(bot, true, Choice.AOE);
    }

    public static AttackResult forceUltimate(Character bot) {
        return attack(bot, true, Choice.ULTIMATE);
    }

    public static void clearBot(int botId) {
        nextAttackByBot.remove(botId);
        nextUltimateByBot.remove(botId);
    }

    public static int attackReachX(Character bot) {
        BotAttackProfile p = primaryProfile(bot);
        return p != null ? p.reachX : 0;
    }

    public static int attackReachY(Character bot) {
        BotAttackProfile p = primaryProfile(bot);
        return p != null ? p.reachY : 0;
    }

    public static boolean hasAoeAttack(Character bot) {
        if (bot == null) return false;
        BotAttackConfig.JobAttacks attacks = BotAttackConfig.resolve(bot.getJob(), BotAttack.resolveEquippedWeaponType(bot));
        return attacks.aoe() != null || attacks.ultimate() != null;
    }

    private static BotAttackProfile primaryProfile(Character bot) {
        if (bot == null) return null;
        BotAttackConfig.JobAttacks attacks = BotAttackConfig.resolve(bot.getJob(), BotAttack.resolveEquippedWeaponType(bot));
        if (attacks.single() != null) return attacks.single();
        return attacks.aoe() != null ? attacks.aoe() : attacks.ultimate();
    }

    private static AttackResult attack(Character bot, boolean force, Choice choice) {
        if (bot == null || bot.getMap() == null || bot.getPosition() == null) {
            return AttackResult.miss("bot or map is null");
        }
        long now = System.currentTimeMillis();
        if (!force && now < nextAttackByBot.getOrDefault(bot.getId(), 0L)) {
            return AttackResult.miss("on cooldown");
        }

        WeaponType weapon = BotAttack.resolveEquippedWeaponType(bot);
        BotAttackConfig.JobAttacks attacks = BotAttackConfig.resolve(bot.getJob(), weapon);
        BotAttackProfile single = attacks.single();
        BotAttackProfile aoe = attacks.aoe();
        BotAttackProfile ultimate = attacks.ultimate();

        if (choice == Choice.SINGLE && single == null) return AttackResult.miss("no single-target attack");
        if (choice == Choice.AOE && aoe == null) return AttackResult.miss("no AoE attack");
        if (choice == Choice.ULTIMATE && ultimate == null) return AttackResult.miss("no ultimate attack");

        Monster nearest = nearestMob(bot);
        if (nearest == null) return AttackResult.miss("no targetable mobs within " + SEEK_RANGE + "px");
        boolean facingLeft = nearest.getPosition().x < bot.getPosition().x;
        if (GCMovement.isEnabled(bot)) GCMovement.face(bot, facingLeft);

        BotAttackProfile profile;
        boolean healUndead = false;
        if (choice == Choice.SINGLE) profile = single;
        else if (choice == Choice.AOE) profile = aoe;
        else if (choice == Choice.ULTIMATE) profile = ultimate;
        else if (isClericVsUndead(bot, nearest)) {
            profile = HEAL_PROFILE;
            healUndead = true;
        } else {
            boolean ultimateReady = ultimate != null && now >= nextUltimateByBot.getOrDefault(bot.getId(), 0L);
            BotAttackProfile pack = ultimateReady ? ultimate : aoe;
            boolean usePack = pack != null && mobsInReach(bot, pack, facingLeft).size() >= 2;
            profile = usePack ? pack : (single != null ? single : (aoe != null ? aoe : ultimate));
        }
        if (profile == null) return AttackResult.miss("no configured attack profile");

        List<Monster> targets = cap(mobsInReach(bot, profile, facingLeft), profile.numAttacked);
        if (healUndead) targets = undeadOnly(targets);
        if (targets.isEmpty()) return AttackResult.miss("nearest mob is outside attack reach");

        int skillId = profile.skillFor(weapon);
        int bodyActionId = BotAttackData.actionFor(skillId, weapon);
        int facingMask = facingLeft ? BotAttackData.FACING_LEFT_MASK : BotAttackData.FACING_RIGHT_MASK;
        int linesPerMob = shadowDoubled(bot, profile.numDamage);
        double critChance = BotAttackConfig.critChanceFor(bot.getJob());
        ThreadLocalRandom rng = ThreadLocalRandom.current();
        Map<Monster, List<Integer>> hits = new LinkedHashMap<>();
        int reported = 0;

        for (Monster mob : targets) {
            List<Integer> lines = new ArrayList<>(linesPerMob);
            for (int i = 0; i < linesPerMob; i++) {
                int damage = profile.rollDamage(bot.getLevel(), bot.getJob());
                if (rng.nextDouble() < critChance) {
                    damage = (int) Math.round(damage * BotAttackConfig.CRIT_MULTIPLIER);
                    lines.add(BotAttackData.encodeCritLine(damage));
                } else {
                    lines.add(damage);
                }
                reported += damage;
            }
            hits.put(mob, lines);
        }

        boolean killed = switch (profile.route) {
            case CLOSE -> BotAttackEffects.meleeStrike(bot, hits, skillId, profile.skillLevel,
                    bodyActionId, facingMask, profile.speed, profile.hitDelayMs);
            case RANGED -> BotAttackEffects.rangedStrike(bot, hits, skillId, profile.skillLevel,
                    BotAttackData.projectileFor(weapon, bot), bodyActionId, facingMask, profile.speed, profile.hitDelayMs);
            case MAGIC -> BotAttackEffects.magicStrike(bot, hits, skillId, profile.skillLevel,
                    bodyActionId, facingMask, profile.speed, profile.hitDelayMs);
        };

        nextAttackByBot.put(bot.getId(), now + profile.cooldownMs);
        if (profile == ultimate) nextUltimateByBot.put(bot.getId(), now + FULL_MAP_ULTIMATE_COOLDOWN_MS);
        String label = targets.size() > 1 ? targets.size() + " mobs (nearest '" + targets.get(0).getName() + "')" : targets.get(0).getName();
        return AttackResult.hit(label, reported, killed);
    }

    private static int shadowDoubled(Character bot, int baseLines) {
        return BotBuffConfig.buffsForJob(bot.getJob()).contains(Hermit.SHADOW_PARTNER) ? baseLines * 2 : baseLines;
    }

    private static boolean isClericVsUndead(Character bot, Monster nearest) {
        return nearest != null && bot.getJob() != null && bot.getJob().isA(Job.CLERIC)
                && nearest.getStats() != null && nearest.getStats().isUndead();
    }

    private static List<Monster> undeadOnly(List<Monster> mobs) {
        List<Monster> out = new ArrayList<>();
        for (Monster mob : mobs) {
            if (mob.getStats() != null && mob.getStats().isUndead()) out.add(mob);
        }
        return out;
    }

    private static List<Monster> mobsInReach(Character bot, BotAttackProfile profile, boolean facingLeft) {
        Point p = bot.getPosition();
        Rectangle box = new Rectangle(p.x - profile.reachX, p.y - profile.reachY,
                profile.reachX * 2, profile.reachY * 2);
        if (profile.route != BotAttackProfile.Route.MAGIC || profile.numAttacked <= 1) {
            box = clipForward(box, p.x, facingLeft);
        }
        Rectangle reach = box;
        List<Monster> found = new ArrayList<>();
        for (MapObject object : bot.getMap().getMapObjectsInRange(p, SEEK_RANGE_SQ, List.of(MapObjectType.MONSTER))) {
            Monster mob = (Monster) object;
            if (!mob.isAlive() || mob.getPosition() == null) continue;
            Rectangle test = mob.isBoss()
                    ? new Rectangle(reach.x, reach.y - BOSS_Y_PAD, reach.width, reach.height + BOSS_Y_PAD * 2)
                    : reach;
            if (test.contains(mob.getPosition()) && onAttackableSurface(bot, mob)) found.add(mob);
        }
        found.sort((a, b) -> Double.compare(p.distanceSq(a.getPosition()), p.distanceSq(b.getPosition())));
        return found;
    }

    private static Rectangle clipForward(Rectangle box, int botX, boolean facingLeft) {
        if (facingLeft) {
            int right = Math.min(box.x + box.width, botX + BACK_MARGIN);
            return new Rectangle(box.x, box.y, Math.max(0, right - box.x), box.height);
        }
        int left = Math.max(box.x, botX - BACK_MARGIN);
        return new Rectangle(left, box.y, Math.max(0, box.x + box.width - left), box.height);
    }

    private static Monster nearestMob(Character bot) {
        Point p = bot.getPosition();
        Monster nearest = null;
        double best = Double.MAX_VALUE;
        for (MapObject object : bot.getMap().getMapObjectsInRange(p, SEEK_RANGE_SQ, List.of(MapObjectType.MONSTER))) {
            Monster mob = (Monster) object;
            if (!mob.isAlive() || mob.getPosition() == null || !onAttackableSurface(bot, mob)) continue;
            double distance = p.distanceSq(mob.getPosition());
            if (distance < best) {
                best = distance;
                nearest = mob;
            }
        }
        return nearest;
    }

    private static boolean onAttackableSurface(Character bot, Monster mob) {
        if (mob.isBoss()) return true;
        Point bp = bot.getPosition();
        Point mp = mob.getPosition();
        return mp == null || !GCMovement.onDifferentLedge(bot.getMap(), bp.x, bp.y, mp.x, mp.y);
    }

    private static List<Monster> cap(List<Monster> mobs, int max) {
        return mobs.size() <= max ? mobs : new ArrayList<>(mobs.subList(0, max));
    }
}
