package soloMapling.ArtificialPlayer.GCMoveSystem;

import client.Character;
import client.Job;
import client.inventory.InventoryType;
import client.inventory.Item;
import net.server.world.Party;
import net.server.world.PartyCharacter;
import server.ItemInformationProvider;
import server.maps.FieldLimit;
import server.maps.MapleMap;

import java.io.Serial;
import java.io.Serializable;
import java.util.Map;

/**
 * SoloMapling GCMove movement profile, reconciled for staged EverLeaf integration.
 *
 * <p>The profile/stat logic is retained from SoloMapling v0.3. Physics constants
 * are temporarily kept local so this data model can compile before the heavier
 * BotPhysicsEngine/BotMovementManager slice is vendored.</p>
 */
record BotMovementProfile(int totalSpeedStat, int totalJumpStat, boolean snowShoes)
        implements Serializable {
    @Serial
    private static final long serialVersionUID = 1L;

    static final int BASE_TOTAL_STAT = 100;
    static final int STAT_BUCKET_SIZE = 5;
    static final int MAX_EFFECTIVE_SPEED_STAT = 200;
    static final int MAX_EFFECTIVE_JUMP_STAT = 123;
    static final BotMovementProfile BASE = new BotMovementProfile(BASE_TOTAL_STAT, BASE_TOTAL_STAT);

    private static final int HASTE_MAX_SPEED = 155;
    private static final int HASTE_MAX_JUMP = MAX_EFFECTIVE_JUMP_STAT;
    private static final int YOUNG_THIEF_SPEED = 150;
    private static final int YOUNG_THIEF_JUMP = 115;
    private static final int HASTE_SELF_MAX_LEVEL = 55;
    private static final int PARTY_HASTE_THIEF_LEVEL = 60;

    // v83 physics baselines used by SoloMapling. These become direct references
    // to BotPhysicsEngine/BotMovementManager when that dependency slice lands.
    private static final double BASE_WALK_VELOCITY_PXS = 125.0;
    private static final double BASE_HORIZONTAL_FORCE_PXS = 16.667;
    private static final float BASE_JUMP_SPEED_PXS = 555.0f;
    private static final float BASE_ROPE_JUMP_SPEED_PXS = 375.0f;

    BotMovementProfile {
        totalSpeedStat = bucketStat(totalSpeedStat);
        totalJumpStat = bucketStat(totalJumpStat);
        totalSpeedStat = Math.min(totalSpeedStat, MAX_EFFECTIVE_SPEED_STAT);
        totalJumpStat = Math.min(totalJumpStat, MAX_EFFECTIVE_JUMP_STAT);
    }

    BotMovementProfile(int totalSpeedStat, int totalJumpStat) {
        this(totalSpeedStat, totalJumpStat, false);
    }

    static BotMovementProfile base() {
        return BASE;
    }

    static BotMovementProfile fromCharacter(Character character) {
        if (character == null || hasForcedBaseMovementStats(character)) {
            return BASE;
        }

        int level = character.getLevel();
        boolean hasteThief = hasHasteSkill(character.getJob());

        int speedBaseline;
        int jumpBaseline;
        if (hasteThief && level >= HASTE_SELF_MAX_LEVEL) {
            speedBaseline = HASTE_MAX_SPEED;
            jumpBaseline = HASTE_MAX_JUMP;
        } else if (hasteThief) {
            speedBaseline = YOUNG_THIEF_SPEED;
            jumpBaseline = YOUNG_THIEF_JUMP;
        } else {
            speedBaseline = levelSpeedStat(level);
            jumpBaseline = levelJumpStat(level);
        }

        if (partyGrantsHaste(character)) {
            speedBaseline = Math.max(speedBaseline, HASTE_MAX_SPEED);
        }

        int totalSpeed = speedBaseline + (character.getTotalMoveSpeedStat() - BASE_TOTAL_STAT);
        int totalJump = jumpBaseline + (character.getTotalJumpStat() - BASE_TOTAL_STAT);
        return new BotMovementProfile(totalSpeed, totalJump, wearsSnowShoes(character));
    }

    private static boolean hasHasteSkill(Job job) {
        return job != null && (job.isA(Job.ASSASSIN) || job.isA(Job.BANDIT));
    }

    private static boolean partyGrantsHaste(Character character) {
        Party party = character.getParty();
        if (party == null) {
            return false;
        }
        for (PartyCharacter member : party.getMembers()) {
            if (member == null || member.getId() == character.getId() || !member.isOnline()) {
                continue;
            }
            if (member.getLevel() >= PARTY_HASTE_THIEF_LEVEL && hasHasteSkill(member.getJob())) {
                return true;
            }
        }
        return false;
    }

    private static int levelSpeedStat(int level) {
        if (level <= 9) return 115;
        if (level <= 29) return 125;
        if (level <= 50) return 130;
        if (level <= 69) return 135;
        if (level <= 100) return 145;
        return 155;
    }

    private static int levelJumpStat(int level) {
        if (level <= 9) return 100;
        if (level <= 29) return 105;
        if (level <= 50) return 110;
        if (level <= 69) return 115;
        if (level <= 100) return 120;
        return HASTE_MAX_JUMP;
    }

    private static boolean wearsSnowShoes(Character character) {
        try {
            Item shoe = character.getInventory(InventoryType.EQUIPPED).getItem((short) -7);
            if (shoe == null) {
                return false;
            }
            Map<String, Integer> stats = ItemInformationProvider.getInstance().getEquipStats(shoe.getItemId());
            return stats != null && stats.getOrDefault("fs", 0) >= 1;
        } catch (Throwable ignored) {
            return false;
        }
    }

    private static boolean hasForcedBaseMovementStats(Character character) {
        MapleMap map = character.getMap();
        return map != null && FieldLimit.MOVEMENTSKILLS.check(map.getFieldLimit());
    }

    private static int bucketStat(int stat) {
        int clamped = Math.max(1, stat);
        if (clamped < STAT_BUCKET_SIZE) {
            return clamped;
        }
        return (int) (Math.round(clamped / (double) STAT_BUCKET_SIZE) * STAT_BUCKET_SIZE);
    }

    double speedMultiplier() {
        return totalSpeedStat / (double) BASE_TOTAL_STAT;
    }

    double jumpMultiplier() {
        return totalJumpStat / (double) BASE_TOTAL_STAT;
    }

    double walkVelocityPxs() {
        return BASE_WALK_VELOCITY_PXS * speedMultiplier();
    }

    double hForcePxs() {
        return BASE_HORIZONTAL_FORCE_PXS * speedMultiplier();
    }

    float jumpSpeedPxs() {
        return (float) (BASE_JUMP_SPEED_PXS * jumpMultiplier());
    }

    float ropeJumpSpeedPxs() {
        return (float) (BASE_ROPE_JUMP_SPEED_PXS * jumpMultiplier());
    }
}
