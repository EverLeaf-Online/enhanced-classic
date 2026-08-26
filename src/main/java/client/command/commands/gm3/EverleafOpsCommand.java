package client.command.commands.gm3;

import client.Character;
import client.Client;
import client.command.Command;
import everleaf.progression.EncounterAttempt;
import everleaf.progression.EnhancedBossRewardMode;
import everleaf.progression.EverleafProgressionRuntime;
import everleaf.progression.RootedForgeOrder;

import java.time.Instant;
import java.util.List;

/** Read-only Everleaf diagnostics plus explicit retry for durable forge orders. */
public class EverleafOpsCommand extends Command {
    private static final int DEFAULT_LIMIT = 10;

    {
        setDescription("Inspect Everleaf encounters and retry pending Rooted forge orders.");
    }

    @Override
    public void execute(Client client, String[] params) {
        Character gm = client.getPlayer();
        if (params.length == 0) {
            usage(gm);
            return;
        }

        try {
            switch (params[0].toLowerCase()) {
                case "forge" -> showPendingForge(gm, params);
                case "retry" -> retryForge(client, params);
                case "reward" -> retryEncounterReward(gm, params);
                case "encounters" -> showEncounters(gm, params);
                default -> usage(gm);
            }
        } catch (IllegalArgumentException e) {
            gm.yellowMessage("Everleaf Ops: " + e.getMessage());
            usage(gm);
        } catch (RuntimeException e) {
            gm.yellowMessage("Everleaf Ops failed: " + e.getMessage());
        }
    }

    private static void showPendingForge(Character gm, String[] params) {
        int limit = parseLimit(params, 1);
        List<RootedForgeOrder> orders = EverleafProgressionRuntime.rootedForgeRepository().pendingOrders(limit);
        gm.yellowMessage("Everleaf pending forge orders: " + orders.size());
        for (RootedForgeOrder order : orders) {
            gm.yellowMessage("#" + order.id() + " char=" + order.characterId()
                    + " account=" + order.accountId() + " recipe=" + order.recipe().name()
                    + " item=" + order.target().itemId() + " slot=" + order.target().slot()
                    + " since=" + order.createdAt());
        }
    }

    private static void retryForge(Client client, String[] params) {
        if (params.length < 2) throw new IllegalArgumentException("missing forge order id");
        long orderId = Long.parseLong(params[1]);
        RootedForgeOrder order = EverleafProgressionRuntime.rootedForgeRepository().findById(orderId)
                .orElseThrow(() -> new IllegalArgumentException("forge order not found"));
        Character owner = client.getWorldServer().getPlayerStorage().getCharacterById(order.characterId());
        if (owner == null) {
            client.getPlayer().yellowMessage("Order #" + orderId + " belongs to an offline character. "
                    + "Retry after character " + order.characterId() + " logs in.");
            return;
        }
        var result = EverleafProgressionRuntime.rootedForgeFulfillmentService().fulfill(owner, orderId);
        client.getPlayer().yellowMessage("Forge order #" + orderId + ": "
                + (result.fulfilled() ? "FULFILLED" : "PENDING") + " (" + result.reason() + ")");
        if (result.fulfilled()) owner.yellowMessage("A GM recovered your pending Rooted forge delivery.");
    }

    private static void showEncounters(Character gm, String[] params) {
        if (params.length < 2) throw new IllegalArgumentException("missing character id");
        int characterId = Integer.parseInt(params[1]);
        int limit = parseLimit(params, 2);
        List<EncounterAttempt> attempts = EverleafProgressionRuntime.encounterRepository()
                .recentAttempts(characterId, limit);
        gm.yellowMessage("Everleaf attempts for character " + characterId + ": " + attempts.size());
        for (EncounterAttempt attempt : attempts) {
            gm.yellowMessage("#" + attempt.id() + " " + attempt.encounterId()
                    + " result=" + attempt.result().name()
                    + " weekly=" + (attempt.weeklyRewardClaimed() ? "CLAIMED" : "NO")
                    + " started=" + attempt.startedAt());
        }
    }

    private static void retryEncounterReward(Character gm, String[] params) {
        if (params.length < 2) throw new IllegalArgumentException("missing encounter attempt id");
        long attemptId = Long.parseLong(params[1]);
        EncounterAttempt attempt = EverleafProgressionRuntime.encounterRepository().findAttempt(attemptId)
                .orElseThrow(() -> new IllegalArgumentException("encounter attempt not found"));
        if (!attempt.cleared() || !attempt.weeklyRewardClaimed()) {
            gm.yellowMessage("Attempt #" + attemptId
                    + " is not an already-claimed weekly clear; reward retry refused.");
            return;
        }
        var result = EverleafProgressionRuntime.rootedZakumLifecycleService().complete(
                attemptId, EnhancedBossRewardMode.WEEKLY_REWARD, Instant.now());
        gm.yellowMessage("Encounter reward #" + attemptId + ": "
                + (result.completed() ? "DELIVERED" : "PENDING") + " (" + result.reason() + ")");
    }

    private static int parseLimit(String[] params, int index) {
        int limit = params.length > index ? Integer.parseInt(params[index]) : DEFAULT_LIMIT;
        if (limit < 1 || limit > 100) throw new IllegalArgumentException("limit must be 1-100");
        return limit;
    }

    private static void usage(Character gm) {
        gm.yellowMessage("!everleafops forge [limit]");
        gm.yellowMessage("!everleafops retry <forgeOrderId>");
        gm.yellowMessage("!everleafops reward <encounterAttemptId>");
        gm.yellowMessage("!everleafops encounters <characterId> [limit]");
    }
}
