package client.command.commands.gm0;

import client.Client;
import client.command.Command;

import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;

/** Shows the personalized GTop100 link used by EverLeaf's verified Vote Point flow. */
public class VoteCommand extends Command {
    private static final String GTOP100_VOTE_URL =
            "https://gtop100.com/MapleStory/server-106444?vote=1&pingUsername=";

    {
        setDescription("Show your personalized EverLeaf voting link.");
    }

    @Override
    public void execute(Client client, String[] params) {
        String accountName = client.getAccountName();
        if (accountName == null || !accountName.matches("[A-Za-z0-9_]{4,13}")) {
            client.getPlayer().yellowMessage("Your account name cannot be used for verified voting. Please contact staff.");
            return;
        }

        String encoded = URLEncoder.encode(accountName, StandardCharsets.UTF_8);
        client.getPlayer().yellowMessage("Vote for EverLeaf to earn Vote Points:");
        client.getPlayer().yellowMessage(GTOP100_VOTE_URL + encoded);
        client.getPlayer().yellowMessage("Verified votes reward Vote Points only. Use @points vp to check your balance and @voteshop to spend them.");
    }
}
