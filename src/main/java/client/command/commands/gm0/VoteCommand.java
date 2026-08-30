package client.command.commands.gm0;

import client.Client;
import client.command.Command;
import java.net.URLEncoder;
import java.nio.charset.Charset;

public class VoteCommand extends Command {
    {
        setDescription("Show your personalized EverLeaf GTop100 voting link.");
    }

    @Override
    public void execute(Client client, String[] params) {
        String accountName = client.getAccountName();
        if (accountName == null || !accountName.matches("[A-Za-z0-9]+")) {
            client.getPlayer().yellowMessage("Your account name is not compatible with GTop voting. Please contact staff.");
            return;
        }
        String encoded = URLEncoder.encode(accountName, Charset.forName("UTF-8"));
        String url = "https:" + "//gtop100.com/MapleStory/server-106444?vote=1&pingUsername=" + encoded;
        client.getPlayer().yellowMessage("Vote for EverLeaf to earn 1,500 NX:");
        client.getPlayer().yellowMessage(url);
        client.getPlayer().yellowMessage("After GTop verifies the vote, use @points nx to claim your reward.");
    }
}
