package client.command.commands.gm0;

import client.Character;
import client.Client;
import client.command.Command;
import service.NxRewardService;

import java.sql.SQLException;

public class DailyNxCommand extends Command {
    {
        setDescription("Claim the account-wide daily NX reward.");
    }

    @Override
    public void execute(Client client, String[] params) {
        Character player = client.getPlayer();
        try {
            int nx = NxRewardService.getInstance().claimDaily(player);
            if (nx > 0) {
                player.yellowMessage("Daily reward claimed: +" + nx + " NX Credit. Come back tomorrow to build your streak.");
            } else {
                NxRewardService.RewardStatus status = NxRewardService.getInstance().getStatus(player.getAccountID());
                player.yellowMessage("Daily NX already claimed today. Current streak: " + status.dailyStreak() + " day(s).");
            }
        } catch (SQLException e) {
            player.yellowMessage("Daily NX is temporarily unavailable. Please report this to staff.");
        }
    }
}
