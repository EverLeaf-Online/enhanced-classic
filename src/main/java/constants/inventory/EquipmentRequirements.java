package constants.inventory;

import client.Job;

/**
 * Server-side equipment requirement helpers.
 *
 * MapleStory encodes equip job restrictions as a five-bit mask:
 * warrior=1, magician=2, bowman=4, thief=8, pirate=16.
 * The v83 Character.wz corpus also uses reqJob=-1 as a legacy sentinel for
 * every combat family. It is intentionally handled after beginner/GM checks
 * so Beginner/Noblesse/Legend do not inherit combat-family access.
 * EverLeaf also maps Cygnus/Aran/Evan jobs onto their matching combat family.
 */
public final class EquipmentRequirements {
    public static final int ALL_COMBAT_FAMILIES = -1;

    private EquipmentRequirements() {
    }

    public static boolean canEquipForJob(Job job, int reqJobMask) {
        if (reqJobMask == 0) {
            return true;
        }
        if (job == null) {
            return false;
        }
        if (job == Job.GM || job == Job.SUPERGM) {
            return true;
        }

        int niche = job.getJobNiche();
        if (niche < 1 || niche > 5) {
            return false;
        }
        if (reqJobMask == ALL_COMBAT_FAMILIES) {
            return true;
        }

        int familyMask = 1 << (niche - 1);
        return (reqJobMask & familyMask) != 0;
    }
}
