package client.command.commands.gm0;

import client.Client;
import client.command.Command;
import everleaf.progression.EverleafProgressionRuntime;
import everleaf.progression.VerdantMarkAccount;
import everleaf.progression.VerdantMarkLedgerEntry;
import everleaf.progression.VerdantMarkService;
import everleaf.progression.VerdantRewardCatalog;
import everleaf.progression.VerdantRewardDefinition;

import java.util.List;

/** Shows account-bound Verdant Marks balance and eligible reward-shop previews. */
public class MarksCommand extends Command {
    {
        setDescription("Show your Verdant Marks balance and reward-shop preview.");
    }

    @Override
    public void execute(Client client, String[] params) {
        int accountId = client.getPlayer().getAccountID();
        int level = client.getPlayer().getLevel();
        VerdantMarkService service = EverleafProgressionRuntime.verdantMarkService();
        VerdantMarkAccount account = service.account(accountId);

        client.getPlayer().yellowMessage(
                "Verdant Marks: " + account.balance()
                        + " | Lifetime earned: " + account.lifetimeEarned()
                        + " | Spent: " + account.lifetimeSpent()
        );

        if (params.length > 0 && "history".equalsIgnoreCase(params[0])) {
            List<VerdantMarkLedgerEntry> history = service.recentLedger(accountId, 5);
            if (history.isEmpty()) {
                client.getPlayer().yellowMessage("No Verdant Marks transactions yet.");
                return;
            }
            client.getPlayer().yellowMessage("Recent Verdant Marks activity:");
            for (VerdantMarkLedgerEntry entry : history) {
                String sign = entry.amount() > 0 ? "+" : "";
                client.getPlayer().yellowMessage(
                        sign + entry.amount() + " -> " + entry.balanceAfter()
                                + " [" + entry.reasonType() + "]"
                );
            }
            return;
        }

        if (level < 200) {
            client.getPlayer().yellowMessage("Verdant Marks endgame rewards unlock at level 200.");
            return;
        }

        List<VerdantRewardDefinition> rewards = VerdantRewardCatalog.eligibleForLevel(level);
        client.getPlayer().yellowMessage("Eligible Verdant reward preview:");
        for (VerdantRewardDefinition reward : rewards) {
            String limit = reward.weeklyAccountLimit() == null
                    ? ""
                    : " | weekly limit " + reward.weeklyAccountLimit();
            client.getPlayer().yellowMessage(
                    "- " + reward.displayName() + " | " + reward.price() + " Marks"
                            + " | " + reward.category().name() + limit
            );
        }
        client.getPlayer().yellowMessage("Use @marks history to view recent account activity.");
    }
}
