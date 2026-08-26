package client.command.commands.gm0;

import client.Client;
import client.command.Command;
import everleaf.progression.EndgameTierProfile;
import everleaf.progression.WeeklyProgressionPolicy;
import service.enhanced.EndgameProgressionSnapshot;
import service.enhanced.EverleafIdentity;

/** Shows a player's current Everleaf extended-endgame progression state. */
public class ProgressCommand extends Command {
    {
        setDescription("Show your Everleaf level 200-250 progression status.");
    }

    @Override
    public void execute(Client client, String[] params) {
        int level = client.getPlayer().getLevel();
        EndgameProgressionSnapshot snapshot = EndgameProgressionSnapshot.forLevel(level);

        client.getPlayer().yellowMessage(EverleafIdentity.displayName());

        if (level < 200) {
            client.getPlayer().yellowMessage("Level " + level + " | Classic progression");
            client.getPlayer().yellowMessage("Everleaf endgame begins at level 200.");
            client.getPlayer().yellowMessage("Levels remaining: " + (200 - level));
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
    }
}
