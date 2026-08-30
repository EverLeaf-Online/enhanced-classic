/*
    EverLeaf quality-of-life command.
*/
package client.command.commands.gm0;

import client.Client;
import client.Job;
import client.command.Command;

public class JobGuideCommand extends Command {
    {
        setDescription("Show your next job advancement and where to go.");
    }

    @Override
    public void execute(Client client, String[] params) {
        Job job = client.getPlayer().getJob();
        int level = client.getPlayer().getLevel();
        String message = getGuidance(job, level);

        client.getPlayer().yellowMessage("EverLeaf Job Guide: " + message);
    }

    private String getGuidance(Job job, int level) {
        if (job == null) {
            return "Your current job could not be identified. Please report this in EverLeaf's bug-report channel.";
        }

        switch (job) {
            case BEGINNER:
                if (level >= 10) {
                    return "You are ready for your first Explorer job. Warrior: Perion; Magician: Ellinia; Bowman: Henesys; Thief: Kerning City; Pirate: Nautilus Harbor.";
                }
                if (level >= 8) {
                    return "Magician is available now in Ellinia. Warrior, Bowman, Thief, and Pirate become available at Lv. 10.";
                }
                return "First advancement: Magician at Lv. 8; Warrior, Bowman, Thief, or Pirate at Lv. 10.";

            case WARRIOR:
                return advancementMessage(level, 30, "2nd Job", "Perion — return to Dances with Balrog");
            case MAGICIAN:
                return advancementMessage(level, 30, "2nd Job", "Ellinia — return to Grendel the Really Old");
            case BOWMAN:
                return advancementMessage(level, 30, "2nd Job", "Henesys — return to Athena Pierce");
            case THIEF:
                return advancementMessage(level, 30, "2nd Job", "Kerning City — return to Dark Lord");
            case PIRATE:
                return advancementMessage(level, 30, "2nd Job", "Nautilus Harbor — return to Kyrin");

            case FIGHTER:
            case PAGE:
            case SPEARMAN:
            case FP_WIZARD:
            case IL_WIZARD:
            case CLERIC:
            case HUNTER:
            case CROSSBOWMAN:
            case ASSASSIN:
            case BANDIT:
            case BRAWLER:
            case GUNSLINGER:
                return advancementMessage(level, 70, "3rd Job", "El Nath — speak with the appropriate 3rd Job Instructor");

            case CRUSADER:
            case WHITEKNIGHT:
            case DRAGONKNIGHT:
            case FP_MAGE:
            case IL_MAGE:
            case PRIEST:
            case RANGER:
            case SNIPER:
            case HERMIT:
            case CHIEFBANDIT:
            case MARAUDER:
            case OUTLAW:
                return advancementMessage(level, 120, "4th Job", "Leafre — begin your class's 4th Job advancement quest");

            case HERO:
            case PALADIN:
            case DARKKNIGHT:
            case FP_ARCHMAGE:
            case IL_ARCHMAGE:
            case BISHOP:
            case BOWMASTER:
            case MARKSMAN:
            case NIGHTLORD:
            case SHADOWER:
            case BUCCANEER:
            case CORSAIR:
                return "You have reached the final Explorer job advancement for your branch.";

            case NOBLESSE:
                return advancementMessage(level, 10, "Cygnus Knight 1st Job", "Ereve — speak with the appropriate Knight instructor");

            case DAWNWARRIOR1:
            case BLAZEWIZARD1:
            case WINDARCHER1:
            case NIGHTWALKER1:
            case THUNDERBREAKER1:
                return advancementMessage(level, 30, "Cygnus Knight 2nd Job", "Ereve — return to your job instructor");

            case DAWNWARRIOR2:
            case BLAZEWIZARD2:
            case WINDARCHER2:
            case NIGHTWALKER2:
            case THUNDERBREAKER2:
                return advancementMessage(level, 70, "Cygnus Knight 3rd Job", "Ereve — return to your job instructor");

            case DAWNWARRIOR3:
            case BLAZEWIZARD3:
            case WINDARCHER3:
            case NIGHTWALKER3:
            case THUNDERBREAKER3:
                return advancementMessage(level, 120, "Cygnus Knight final advancement", "Ereve — return to your job instructor");

            case DAWNWARRIOR4:
            case BLAZEWIZARD4:
            case WINDARCHER4:
            case NIGHTWALKER4:
            case THUNDERBREAKER4:
                return "You have reached your final Cygnus Knight advancement.";

            case LEGEND:
                return advancementMessage(level, 10, "Aran 1st Job", "Rien — continue the Aran storyline");
            case ARAN1:
                return advancementMessage(level, 30, "Aran 2nd Job", "Rien — continue the Aran advancement questline");
            case ARAN2:
                return advancementMessage(level, 70, "Aran 3rd Job", "Rien — continue the Aran advancement questline");
            case ARAN3:
                return advancementMessage(level, 120, "Aran final advancement", "Rien — continue the Aran advancement questline");
            case ARAN4:
                return "You have reached Aran's final job advancement.";

            default:
                return "Follow your current job questline for advancement information. Current job: " + job.name() + ".";
        }
    }

    private String advancementMessage(int currentLevel, int requiredLevel, String advancement, String destination) {
        if (currentLevel >= requiredLevel) {
            return "You are ready for " + advancement + ". Destination: " + destination + ".";
        }

        return "Next: " + advancement + " at Lv. " + requiredLevel + ". You need " + (requiredLevel - currentLevel) + " more level(s). Destination when ready: " + destination + ".";
    }
}
