package client.command.commands.gm0;

import client.Client;
import client.command.Command;
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
        client.getPlayer().yellowMessage("Level " + level + " | " + snapshot.tier().name().replace('_', ' '));

        if (snapshot.atLevelCap()) {
            client.getPlayer().yellowMessage("Level cap reached. Capstone progression is unlocked.");
        } else if (snapshot.nextMilestoneLevel() != null) {
            client.getPlayer().yellowMessage(
                    "Next milestone: Lv. " + snapshot.nextMilestoneLevel()
                            + " (" + snapshot.levelsToNextMilestone() + " levels)"
            );
        }

        if (snapshot.unlocks().isEmpty()) {
            client.getPlayer().yellowMessage("Extended endgame begins at level 200.");
        } else {
            client.getPlayer().yellowMessage("Unlocked tracks: " + snapshot.unlocks().size());
        }
    }
}
