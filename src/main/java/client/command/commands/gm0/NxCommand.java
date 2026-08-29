package client.command.commands.gm0;

import client.Character;
import client.Client;
import client.command.Command;
import service.NxRewardService;

import java.sql.SQLException;

public class NxCommand extends Command {
    {
        setDescription("Claim available NX rewards and show reward status.");
    }

    @Override
    public void execute(Client client, String[] params) {
        Character player = client.getPlayer();
        NxRewardService rewards = NxRewardService.getInstance();

        try {
            NxRewardService.RewardSummary summary = rewards.claimAvailable(player);
            NxRewardService.RewardStatus status = summary.status();

            if (summary.totalNx() > 0) {
                player.yellowMessage("EverLeaf NX claimed: +" + summary.totalNx() + " NX Credit"
                        + " (daily " + summary.dailyNx()
                        + ", playtime " + summary.playtimeNx()
                        + ", vote " + summary.voteNx() + ").");
            } else {
                player.yellowMessage("No NX rewards are ready to claim right now.");
            }

            int minutes = status.playtimeSecondsToday() / 60;
            player.yellowMessage("NX status: daily " + (status.dailyClaimedToday() ? "claimed" : "ready")
                    + " | streak " + status.dailyStreak()
                    + " | playtime today " + minutes + "m"
                    + " | playtime claims " + status.playtimeStepsClaimedToday()
                    + "/" + NxRewardService.PLAYTIME_MAX_STEPS_PER_DAY
                    + " | pending vote NX " + status.pendingVoteNx() + ".");
        } catch (SQLException e) {
            player.yellowMessage("NX rewards are temporarily unavailable. Please report this to staff.");
        }
    }
}
