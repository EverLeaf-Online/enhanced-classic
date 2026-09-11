package client.command.commands.gm0;

import client.Character;
import client.Client;
import client.command.Command;
import client.inventory.InventoryType;
import client.inventory.Item;
import client.inventory.manipulator.InventoryManipulator;
import everleaf.progression.AccountMilestoneService;
import everleaf.progression.AccountMilestoneSnapshot;
import everleaf.progression.AccountMilestoneTrack;
import everleaf.progression.EverleafProgressionRuntime;
import server.ItemInformationProvider;

import java.util.ArrayList;
import java.util.List;

/** Shows and synchronizes EverLeaf's bounded account milestone ring tracks. */
public class MilestonesCommand extends Command {
    {
        setDescription("Show account milestones or sync unlocked milestone rings.");
    }

    @Override
    public void execute(Client client, String[] params) {
        Character player = client.getPlayer();
        AccountMilestoneSnapshot snapshot;
        try {
            snapshot = EverleafProgressionRuntime.accountMilestoneService().snapshot(player.getAccountID());
        } catch (RuntimeException e) {
            player.yellowMessage("Milestone progress is temporarily unavailable. Please try again later.");
            return;
        }

        if (params.length == 0) {
            showProgress(player, snapshot);
            return;
        }

        String action = params[0];
        if (!"sync".equals(action) && !"claim".equals(action)) {
            player.yellowMessage("Usage: @milestones [sync|claim] [book|quest|legacy|all]");
            return;
        }

        String requested = params.length >= 2 ? params[1] : "all";
        if ("all".equals(requested)) {
            for (AccountMilestoneTrack track : AccountMilestoneTrack.values()) {
                syncTrack(client, snapshot, track);
            }
            return;
        }

        AccountMilestoneTrack track = AccountMilestoneTrack.fromToken(requested);
        if (track == null) {
            player.yellowMessage("Unknown milestone track. Use book, quest, legacy, or all.");
            return;
        }
        syncTrack(client, snapshot, track);
    }

    private static void showProgress(Character player, AccountMilestoneSnapshot snapshot) {
        player.yellowMessage("EverLeaf account milestones:");
        showTrack(player, snapshot, AccountMilestoneTrack.MONSTER_BOOK, "unique cards");
        showTrack(player, snapshot, AccountMilestoneTrack.QUESTS, "unique completed quests");
        showTrack(player, snapshot, AccountMilestoneTrack.LEGACY, "linked-level score");
        player.yellowMessage(
                "Legacy score uses only your top " + AccountMilestoneService.LINKED_CHARACTER_CAP
                        + " characters and caps each at level " + AccountMilestoneService.LINKED_LEVEL_CAP_PER_CHARACTER
                        + " (current contributors: " + snapshot.linkedCharacters() + ")."
        );
        player.yellowMessage("Use @milestones sync all to claim or evolve every unlocked ring on this character.");
    }

    private static void showTrack(Character player, AccountMilestoneSnapshot snapshot,
                                  AccountMilestoneTrack track, String unit) {
        int value = snapshot.value(track);
        int tier = snapshot.tier(track);
        String next;
        if (tier >= track.maxTier()) {
            next = "MAX";
        } else {
            next = String.valueOf(track.thresholdForTier(tier + 1));
        }
        player.yellowMessage(
                track.displayName() + ": " + value + " " + unit
                        + " | ring tier " + tier + "/" + track.maxTier()
                        + " | next: " + next
        );
    }

    private static void syncTrack(Client client, AccountMilestoneSnapshot snapshot,
                                  AccountMilestoneTrack track) {
        Character player = client.getPlayer();
        int unlockedTier = snapshot.tier(track);
        if (unlockedTier <= 0) {
            player.yellowMessage(
                    track.displayName() + ": no ring unlocked yet. First milestone is "
                            + track.thresholdForTier(1) + "."
            );
            return;
        }

        int ownedTier = highestMarkedTier(player, track);
        if (ownedTier >= unlockedTier) {
            player.yellowMessage(
                    track.displayName() + ": " + track.ringName() + " is already synced at tier "
                            + ownedTier + "."
            );
            return;
        }

        if (hasMarkedRingEquipped(player, track)) {
            player.yellowMessage(
                    track.displayName() + ": unequip your EverLeaf milestone ring before evolving it."
            );
            return;
        }

        int targetItemId = track.ringIdForTier(unlockedTier);
        if (!InventoryManipulator.checkSpace(client, targetItemId, 1, track.ownerMarker())) {
            player.yellowMessage(
                    track.displayName() + ": make one free Equip slot and make sure no conflicting copy of the target ring is present."
            );
            return;
        }

        Item target = ItemInformationProvider.getInstance().getEquipById(targetItemId);
        if (target == null) {
            player.yellowMessage(track.displayName() + ": ring data is unavailable; nothing was changed.");
            return;
        }
        target.setOwner(track.ownerMarker());

        if (!InventoryManipulator.addFromDrop(client, target, false)) {
            player.yellowMessage(track.displayName() + ": ring grant failed; nothing was removed. Try again later.");
            return;
        }

        // Add-first/remove-second prevents a failed grant from eating the previous tier.
        removeOlderMarkedRings(client, track, targetItemId);
        player.yellowMessage(
                track.displayName() + ": synced " + track.ringName() + " to tier " + unlockedTier
                        + " (item " + targetItemId + ")."
        );
    }

    private static int highestMarkedTier(Character player, AccountMilestoneTrack track) {
        int highest = 0;
        for (InventoryType type : new InventoryType[]{InventoryType.EQUIP, InventoryType.EQUIPPED}) {
            for (Item item : player.getInventory(type).list()) {
                if (isMarkedTrackItem(item, track)) {
                    highest = Math.max(highest, track.tierForRingId(item.getItemId()));
                }
            }
        }
        return highest;
    }

    private static boolean hasMarkedRingEquipped(Character player, AccountMilestoneTrack track) {
        for (Item item : player.getInventory(InventoryType.EQUIPPED).list()) {
            if (isMarkedTrackItem(item, track)) {
                return true;
            }
        }
        return false;
    }

    private static boolean isMarkedTrackItem(Item item, AccountMilestoneTrack track) {
        return item != null
                && track.containsRingId(item.getItemId())
                && track.ownerMarker().equals(item.getOwner());
    }

    private static void removeOlderMarkedRings(Client client, AccountMilestoneTrack track, int keepItemId) {
        List<Item> snapshot = new ArrayList<>(client.getPlayer().getInventory(InventoryType.EQUIP).list());
        for (Item item : snapshot) {
            if (item.getItemId() == keepItemId || !isMarkedTrackItem(item, track)) {
                continue;
            }
            InventoryManipulator.removeFromSlot(
                    client,
                    InventoryType.EQUIP,
                    item.getPosition(),
                    item.getQuantity(),
                    false,
                    false
            );
        }
    }
}
