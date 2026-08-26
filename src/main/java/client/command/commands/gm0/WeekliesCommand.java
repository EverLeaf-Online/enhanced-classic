package client.command.commands.gm0;

import client.Client;
import client.command.Command;
import everleaf.progression.AccountWeeklyState;
import everleaf.progression.CharacterObjectiveState;
import everleaf.progression.EverleafProgressionRuntime;
import everleaf.progression.WeeklyObjectiveCatalog;
import everleaf.progression.WeeklyObjectiveDefinition;
import everleaf.progression.WeeklyProgressRepository;
import everleaf.progression.WeeklyProgressionPolicy;
import everleaf.progression.WeeklyWindow;

import java.time.Instant;
import java.time.LocalDate;
import java.util.List;

/** Shows the weekly objective templates and persisted progress for the player. */
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

        LocalDate week = WeeklyWindow.forInstant(Instant.now()).startDate();
        WeeklyProgressRepository repository = EverleafProgressionRuntime.weeklyRepository();
        AccountWeeklyState account = repository.findAccountState(client.getPlayer().getAccountID(), week)
                .orElse(new AccountWeeklyState(client.getPlayer().getAccountID(), week, 0, 0));

        int coreBudget = WeeklyProgressionPolicy.weeklyCorePoints(level);
        int availableBudget = coreBudget + account.catchupPointsBank();
        int remainingBudget = Math.max(0, availableBudget - account.rewardPointsClaimed());

        List<WeeklyObjectiveDefinition> objectives = WeeklyObjectiveCatalog.eligibleForLevel(level);
        client.getPlayer().yellowMessage(
                "Everleaf Weeklies | Week " + week
                        + " | Account reward budget: " + account.rewardPointsClaimed() + "/" + availableBudget
                        + " (" + remainingBudget + " remaining)"
        );

        for (WeeklyObjectiveDefinition objective : objectives) {
            CharacterObjectiveState state = repository.findCharacterObjective(
                    client.getPlayer().getId(), week, objective.id()
            ).orElse(new CharacterObjectiveState(
                    client.getPlayer().getId(), week, objective.id(), 0, null, null
            ));

            int reward = WeeklyProgressionPolicy.clampAward(level, objective.pointReward());
            String status = state.claimed()
                    ? "CLAIMED"
                    : state.completed() ? "COMPLETE" : state.progressCount() + "/" + objective.targetCount();
            client.getPlayer().yellowMessage(
                    "- " + objective.displayName() + " [" + objective.lane().name() + "] "
                            + status + " | +" + reward + " weekly points"
            );
        }
    }
}
