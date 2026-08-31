package constants.inventory;

import client.Job;

/**
 * Server-side equipment requirement helpers.
 *
 * MapleStory encodes equip job restrictions as a five-bit mask:
 * warrior=1, magician=2, bowman=4, thief=8, pirate=16.
 * EverLeaf also maps Cygnus/Aran/Evan jobs onto their matching combat family.
 */
public final class EquipmentRequirements {
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

        int familyMask = 1 << (niche - 1);
        return (reqJobMask & familyMask) != 0;
    }
}
