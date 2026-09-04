package soloMapling.ArtificialPlayer;

import client.Character;
import client.Job;
import client.inventory.InventoryType;
import client.inventory.Item;
import client.inventory.manipulator.InventoryManipulator;

/**
 * Deterministic, disposable combat loadouts for synthetic QA characters.
 *
 * <p>QA clones should not inherit arbitrary equipment/AP from the template GM. This helper gives
 * them ordinary class-shaped base stats and a real low-level weapon so combat exercises EverLeaf's
 * character stat/equipment calculations instead of a naked or mismatched template profile.</p>
 */
public final class BotQaLoadout {
    private static final short WEAPON_SLOT = -11;

    private static final int SWORD = 1302000;
    private static final int WAND = 1372000;
    private static final int DAGGER = 1332000;
    private static final int POLEARM = 1442000;
    private static final int BOW = 1452002;
    private static final int CLAW = 1472000;
    private static final int KNUCKLE = 1482000;
    private static final int GUN = 1492000;

    private BotQaLoadout() {}

    public static LoadoutResult apply(Character bot, int jobId) {
        if (bot == null || !BotHelpers.isBot(bot)) return LoadoutResult.fail("not-a-bot");
        Job job = Job.getById(jobId);
        if (job == null) return LoadoutResult.fail("unknown-job");

        StatProfile stats = statsForJob(jobId);
        bot.updateStrDexIntLuk(4);
        bot.gainAp(-bot.getRemainingAp(), true);
        int strDelta = stats.str() - 4;
        int dexDelta = stats.dex() - 4;
        int intDelta = stats.intel() - 4;
        int lukDelta = stats.luk() - 4;
        int neededAp = strDelta + dexDelta + intDelta + lukDelta;
        bot.gainAp(neededAp, true);
        if (!bot.assignStrDexIntLuk(strDelta, dexDelta, intDelta, lukDelta)) {
            return LoadoutResult.fail("stat-profile-rejected");
        }

        int weaponId = weaponForJob(jobId);
        if (!InventoryManipulator.addById(bot.getClient(), weaponId, (short) 1, "EverLeaf-QA", -1)) {
            return LoadoutResult.fail("weapon-create-failed:" + weaponId);
        }
        Item weapon = bot.getInventory(InventoryType.EQUIP).findById(weaponId);
        if (weapon == null) return LoadoutResult.fail("weapon-missing-after-create:" + weaponId);

        InventoryManipulator.equip(bot.getClient(), weapon.getPosition(), WEAPON_SLOT);
        Item equipped = bot.getInventory(InventoryType.EQUIPPED).getItem(WEAPON_SLOT);
        if (equipped == null || equipped.getItemId() != weaponId) {
            return LoadoutResult.fail("weapon-equip-failed:" + weaponId);
        }

        bot.healHpMp();
        return new LoadoutResult(true, weaponId, stats, "applied");
    }

    public static int weaponForJob(int jobId) {
        Job job = Job.getById(jobId);
        if (job == null) return SWORD;
        if (job.isA(Job.EVAN1) || job.isA(Job.BLAZEWIZARD1) || job.isA(Job.MAGICIAN)) return WAND;
        if (job.isA(Job.ARAN1)) return POLEARM;
        if (job.isA(Job.WINDARCHER1) || job.isA(Job.BOWMAN)) return BOW;
        if (job.isA(Job.NIGHTWALKER1) || job.isA(Job.ASSASSIN)) return CLAW;
        if (job.isA(Job.BANDIT)) return DAGGER;
        if (job.isA(Job.GUNSLINGER)) return GUN;
        if (job.isA(Job.BRAWLER) || job.isA(Job.THUNDERBREAKER1)) return KNUCKLE;
        return SWORD;
    }

    public static StatProfile statsForJob(int jobId) {
        Job job = Job.getById(jobId);
        if (job == null) return new StatProfile(300, 50, 4, 4);
        if (job.isA(Job.EVAN1) || job.isA(Job.BLAZEWIZARD1) || job.isA(Job.MAGICIAN)) {
            return new StatProfile(4, 4, 300, 50);
        }
        if (job.isA(Job.NIGHTWALKER1) || job.isA(Job.THIEF)) {
            return new StatProfile(4, 70, 4, 280);
        }
        if (job.isA(Job.WINDARCHER1) || job.isA(Job.BOWMAN) || job.isA(Job.GUNSLINGER)) {
            return new StatProfile(50, 300, 4, 4);
        }
        return new StatProfile(300, 50, 4, 4);
    }

    public record StatProfile(int str, int dex, int intel, int luk) {}

    public record LoadoutResult(boolean success, int weaponId, StatProfile stats, String reason) {
        static LoadoutResult fail(String reason) {
            return new LoadoutResult(false, 0, new StatProfile(4, 4, 4, 4), reason);
        }
    }
}
