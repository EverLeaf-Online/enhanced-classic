package service.enhanced;

import client.Job;

/**
 * Enhanced Classic survivability targets used to remove mandatory HP washing.
 *
 * <p>The policy intentionally exposes pure calculations first. Character mutation
 * and persistence are handled separately so the thresholds can be tested and
 * tuned without coupling them to login or level-up flows.</p>
 */
public final class SurvivabilityPolicy {

    private SurvivabilityPolicy() {
    }

    public enum Archetype {
        WARRIOR,
        BRAWLER,
        RANGED,
        MAGICIAN,
        BEGINNER
    }

    public static Archetype classify(Job job) {
        if (job == null) {
            return Archetype.BEGINNER;
        }

        if (job.isA(Job.WARRIOR) || job.isA(Job.DAWNWARRIOR1) || job.isA(Job.ARAN1)) {
            return Archetype.WARRIOR;
        }
        if (job.isA(Job.BRAWLER) || job.isA(Job.THUNDERBREAKER1)) {
            return Archetype.BRAWLER;
        }
        if (job.isA(Job.MAGICIAN) || job.isA(Job.BLAZEWIZARD1) || job.isA(Job.EVAN1)) {
            return Archetype.MAGICIAN;
        }
        if (job.isA(Job.BOWMAN) || job.isA(Job.THIEF) || job.isA(Job.GUNSLINGER)
                || job.isA(Job.WINDARCHER1) || job.isA(Job.NIGHTWALKER1)) {
            return Archetype.RANGED;
        }

        return Archetype.BEGINNER;
    }

    /**
     * Returns the minimum permanent MaxHP target for the character's current level.
     * These are development values and should be tuned against the boss ladder.
     */
    public static int minimumMaxHp(Job job, int level) {
        if (level < 1) {
            throw new IllegalArgumentException("level must be positive");
        }

        Archetype archetype = classify(job);
        int tier = tierForLevel(level);

        return switch (archetype) {
            case WARRIOR -> warriorFloor(tier);
            case BRAWLER -> brawlerFloor(tier);
            case RANGED -> rangedFloor(tier);
            case MAGICIAN -> magicianFloor(tier);
            case BEGINNER -> beginnerFloor(tier);
        };
    }

    /** Returns only the amount required to reach the current floor. */
    public static int requiredIncrease(Job job, int level, int currentMaxHp) {
        if (currentMaxHp < 0) {
            throw new IllegalArgumentException("currentMaxHp cannot be negative");
        }
        return Math.max(0, minimumMaxHp(job, level) - currentMaxHp);
    }

    static int tierForLevel(int level) {
        if (level < 50) return 0;
        if (level < 70) return 1;
        if (level < 90) return 2;
        if (level < 120) return 3;
        if (level < 150) return 4;
        if (level < 180) return 5;
        if (level < 200) return 6;
        return 7;
    }

    private static int warriorFloor(int tier) {
        return switch (tier) {
            case 0 -> 0;
            case 1 -> 3500;
            case 2 -> 5000;
            case 3 -> 7500;
            case 4 -> 10000;
            case 5 -> 13000;
            case 6 -> 16000;
            default -> 19000;
        };
    }

    private static int brawlerFloor(int tier) {
        return switch (tier) {
            case 0 -> 0;
            case 1 -> 3000;
            case 2 -> 4200;
            case 3 -> 6000;
            case 4 -> 8000;
            case 5 -> 10000;
            case 6 -> 12000;
            default -> 14000;
        };
    }

    private static int rangedFloor(int tier) {
        return switch (tier) {
            case 0 -> 0;
            case 1 -> 2200;
            case 2 -> 3000;
            case 3 -> 4200;
            case 4 -> 5500;
            case 5 -> 6800;
            case 6 -> 8000;
            default -> 9000;
        };
    }

    private static int magicianFloor(int tier) {
        return switch (tier) {
            case 0 -> 0;
            case 1 -> 1700;
            case 2 -> 2300;
            case 3 -> 3200;
            case 4 -> 4200;
            case 5 -> 5200;
            case 6 -> 6200;
            default -> 7000;
        };
    }

    private static int beginnerFloor(int tier) {
        return switch (tier) {
            case 0 -> 0;
            case 1 -> 1800;
            case 2 -> 2500;
            case 3 -> 3500;
            case 4 -> 4500;
            case 5 -> 5500;
            case 6 -> 6500;
            default -> 7500;
        };
    }
}
