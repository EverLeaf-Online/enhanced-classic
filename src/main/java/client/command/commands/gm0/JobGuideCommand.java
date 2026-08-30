/*
    EverLeaf quality-of-life command.
*/
package client.command.commands.gm0;

import client.Job;
import client.Client;
import client.command.Command;

public class JobGuideCommand extends Command {
    {
        setDescription("Show your next job advancement level.");
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
                return "Explorer first advancement: Magician at Lv. 8; Warrior, Bowman, Thief, or Pirate at Lv. 10. Visit the appropriate job instructor when ready.";

            case WARRIOR:
            case MAGICIAN:
            case BOWMAN:
            case THIEF:
            case PIRATE:
                return advancementMessage(level, 30, "2nd Job", "your class instructor");

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
                return advancementMessage(level, 70, "3rd Job", "your 3rd Job advancement quest");

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
                return advancementMessage(level, 120, "4th Job", "your 4th Job advancement quest");

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
                return "You have reached 4th Job. There is no further Explorer job advancement.";

            case NOBLESSE:
                return advancementMessage(level, 10, "Cygnus Knight 1st Job", "the appropriate Knight instructor in Ereve");

            case DAWNWARRIOR1:
            case BLAZEWIZARD1:
            case WINDARCHER1:
            case NIGHTWALKER1:
            case THUNDERBREAKER1:
                return advancementMessage(level, 30, "2nd Job", "your Cygnus advancement quest");

            case DAWNWARRIOR2:
            case BLAZEWIZARD2:
            case WINDARCHER2:
            case NIGHTWALKER2:
            case THUNDERBREAKER2:
                return advancementMessage(level, 70, "3rd Job", "your Cygnus advancement quest");

            case DAWNWARRIOR3:
            case BLAZEWIZARD3:
            case WINDARCHER3:
            case NIGHTWALKER3:
            case THUNDERBREAKER3:
                return advancementMessage(level, 120, "4th Job", "your Cygnus advancement quest");

            case DAWNWARRIOR4:
            case BLAZEWIZARD4:
            case WINDARCHER4:
            case NIGHTWALKER4:
            case THUNDERBREAKER4:
                return "You have reached your final Cygnus Knight advancement.";

            case LEGEND:
                return advancementMessage(level, 10, "Aran 1st Job", "the Aran advancement quest in Rien");

            case ARAN1:
                return advancementMessage(level, 30, "Aran 2nd Job", "your Aran advancement quest");
            case ARAN2:
                return advancementMessage(level, 70, "Aran 3rd Job", "your Aran advancement quest");
            case ARAN3:
                return advancementMessage(level, 120, "Aran 4th Job", "your Aran advancement quest");
            case ARAN4:
                return "You have reached Aran's final job advancement.";

            default:
                return "Follow your current job questline for advancement information. Your current job is " + job.name() + ".";
        }
    }

    private String advancementMessage(int currentLevel, int requiredLevel, String advancement, String destination) {
        if (currentLevel >= requiredLevel) {
            return advancement + " is available now (Lv. " + requiredLevel + "). Continue through " + destination + ".";
        }

        return "Next: " + advancement + " at Lv. " + requiredLevel + ". You need " + (requiredLevel - currentLevel) + " more level(s). Then continue through " + destination + ".";
    }
}
