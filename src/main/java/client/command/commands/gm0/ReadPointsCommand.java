package client.command.commands.gm0;

import client.Character;
import client.Client;
import client.command.Command;
import service.NxRewardService;

import java.sql.SQLException;

public class ReadPointsCommand extends Command {
    {
        setDescription("Show points or claim EverLeaf NX rewards.");
    }

    @Override
    public void execute(Client client, String[] params) {
        Character player = client.getPlayer();
        NxRewardService rewards = NxRewardService.getInstance();
        rewards.startSession(player);

        if (params.length > 1) {
            player.yellowMessage("Syntax: @points (rp|vp|nx|daily|all)");
            return;
        }

        if (params.length == 0 || "all".equals(params[0])) {
            player.yellowMessage("RewardPoints: " + player.getRewardPoints() + " | "
                    + "VotePoints: " + player.getClient().getVotePoints() + " | "
                    + "NX Credit: " + player.getCashShop().getCash(1));
            player.yellowMessage("Use @points nx to claim daily, playtime, and verified vote NX.");
            return;
        }

        switch (params[0]) {
            case "rp" -> player.yellowMessage("RewardPoints: " + player.getRewardPoints());
            case "vp" -> player.yellowMessage("VotePoints: " + player.getClient().getVotePoints());
            case "daily" -> claimDaily(player, rewards);
            case "nx" -> claimNx(player, rewards);
            default -> player.yellowMessage("Syntax: @points (rp|vp|nx|daily|all)");
        }
    }

    private void claimDaily(Character player, NxRewardService rewards) {
        try {
            int nx = rewards.claimDaily(player);
            if (nx > 0) {
                player.yellowMessage("Daily reward claimed: +" + nx + " NX Credit.");
            } else {
                NxRewardService.RewardStatus status = rewards.getStatus(player.getAccountID());
                player.yellowMessage("Daily NX already claimed today. Current streak: " + status.dailyStreak() + " day(s).");
            }
        } catch (SQLException e) {
            player.yellowMessage("Daily NX is temporarily unavailable. Please report this to staff.");
        }
    }

    private void claimNx(Character player, NxRewardService rewards) {
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
            player.yellowMessage("NX Credit: " + player.getCashShop().getCash(1)
                    + " | streak " + status.dailyStreak()
                    + " | playtime " + (status.playtimeSecondsToday() / 60) + "m"
                    + " | playtime claims " + status.playtimeStepsClaimedToday()
                    + "/" + NxRewardService.PLAYTIME_MAX_STEPS_PER_DAY
                    + " | pending vote NX " + status.pendingVoteNx() + ".");
        } catch (SQLException e) {
            player.yellowMessage("NX rewards are temporarily unavailable. Please report this to staff.");
        }
    }
}
