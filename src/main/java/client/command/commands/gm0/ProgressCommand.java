package client.command.commands.gm0;

import client.Client;
import client.command.Command;
import everleaf.progression.EndgameTierProfile;
import everleaf.progression.WeeklyProgressionPolicy;
import service.enhanced.EndgameProgressionSnapshot;
import service.enhanced.EverleafIdentity;

import java.util.Arrays;

/** Shows a player's current Everleaf extended-endgame and account milestone progression state. */
public class ProgressCommand extends Command {
    {
        setDescription("Show level 200-250 progress or account milestone rings.");
    }

    @Override
    public void execute(Client client, String[] params) {
        if (params.length > 0) {
            String action = params[0];
            if ("milestones".equals(action)) {
                new MilestonesCommand().execute(client, Arrays.copyOfRange(params, 1, params.length));
                return;
            }
            if ("sync".equals(action) || "claim".equals(action)) {
                new MilestonesCommand().execute(client, params);
                return;
            }
        }

        int level = client.getPlayer().getLevel();
        EndgameProgressionSnapshot snapshot = EndgameProgressionSnapshot.forLevel(level);

        client.getPlayer().yellowMessage(EverleafIdentity.displayName());

        if (level < 200) {
            client.getPlayer().yellowMessage("Level " + level + " | Classic progression");
            client.getPlayer().yellowMessage("Everleaf endgame begins at level 200.");
            client.getPlayer().yellowMessage("Levels remaining: " + (200 - level));
            client.getPlayer().yellowMessage("Account collections: use @progress milestones.");
            return;
        }

        EndgameTierProfile profile = EndgameTierProfile.forLevel(level);
        client.getPlayer().yellowMessage(
                "Level " + level + " | Tier " + profile.tier().rank() + " - " + profile.name()
        );
        client.getPlayer().yellowMessage(profile.purpose());
        client.getPlayer().yellowMessage(
                "Weekly core budget: " + WeeklyProgressionPolicy.weeklyCorePoints(level) + " points"
        );

        if (snapshot.atLevelCap()) {
            client.getPlayer().yellowMessage("Level cap reached. Evergreen progression is active.");
        } else if (snapshot.nextMilestoneLevel() != null) {
            client.getPlayer().yellowMessage(
                    "Next milestone: Lv. " + snapshot.nextMilestoneLevel()
                            + " (" + snapshot.levelsToNextMilestone() + " levels)"
            );
        }

        client.getPlayer().yellowMessage("Unlocked tracks: " + snapshot.unlocks().size());
        client.getPlayer().yellowMessage("Account collections: use @progress milestones.");
    }
}
