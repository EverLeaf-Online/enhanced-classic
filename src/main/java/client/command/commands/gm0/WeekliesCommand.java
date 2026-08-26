package client.command.commands.gm0;

import client.Client;
import client.command.Command;
import everleaf.progression.WeeklyObjectiveCatalog;
import everleaf.progression.WeeklyObjectiveDefinition;
import everleaf.progression.WeeklyProgressionPolicy;

import java.util.List;

/** Shows the weekly objective templates currently available to the player. */
public class WeekliesCommand extends Command {
    {
        setDescription("Show your current Everleaf weekly endgame objectives.");
    }

    @Override
    public void execute(Client client, String[] params) {
        int level = client.getPlayer().getLevel();
        if (level < 200) {
            client.getPlayer().yellowMessage("Everleaf weekly endgame objectives unlock at level 200.");
            return;
        }

        List<WeeklyObjectiveDefinition> objectives = WeeklyObjectiveCatalog.eligibleForLevel(level);
        client.getPlayer().yellowMessage(
                "Everleaf Weeklies | Core budget: " + WeeklyProgressionPolicy.weeklyCorePoints(level)
                        + " | Catch-up bank: " + WeeklyProgressionPolicy.catchUpBankCap(level)
        );

        for (WeeklyObjectiveDefinition objective : objectives) {
            int reward = WeeklyProgressionPolicy.clampAward(level, objective.pointReward());
            client.getPlayer().yellowMessage(
                    "- " + objective.displayName() + " x" + objective.targetCount()
                            + " [" + objective.lane().name() + "] +" + reward
            );
        }
    }
}
