package soloMapling.ArtificialPlayer;

import client.Character;
import client.inventory.InventoryType;
import client.inventory.Item;

import java.util.Collections;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.TreeSet;

/** Lightweight conservation snapshots used by trade/storage anti-dupe QA scenarios. */
public final class BotQaLedger {
    private static final InventoryType[] PLAYER_TYPES = {
            InventoryType.EQUIPPED, InventoryType.EQUIP, InventoryType.USE,
            InventoryType.SETUP, InventoryType.ETC, InventoryType.CASH
    };

    private BotQaLedger() {}

    public static Snapshot capture(Character... characters) {
        long mesos = 0;
        Map<Integer, Long> items = new LinkedHashMap<>();
        if (characters != null) {
            for (Character chr : characters) {
                if (chr == null) continue;
                mesos += chr.getMeso();
                for (InventoryType type : PLAYER_TYPES) {
                    for (Item item : chr.getInventory(type).list()) {
                        if (item == null || item.getQuantity() <= 0) continue;
                        items.merge(item.getItemId(), (long) item.getQuantity(), Long::sum);
                    }
                }
            }
        }
        return new Snapshot(mesos, Collections.unmodifiableMap(new LinkedHashMap<>(items)));
    }

    public static Conservation compare(Snapshot before, Snapshot after) {
        if (before == null || after == null) return new Conservation(false, false, 0, "missing-snapshot");
        boolean itemsEqual = before.items().equals(after.items());
        long mesoDelta = after.mesos() - before.mesos();
        boolean mesosEqual = mesoDelta == 0;
        String reason = itemsEqual && mesosEqual ? "conserved" : describeDifference(before, after, mesoDelta);
        return new Conservation(itemsEqual, mesosEqual, mesoDelta, reason);
    }

    public static boolean noItemCreation(Snapshot before, Snapshot after) {
        if (before == null || after == null) return false;
        for (Map.Entry<Integer, Long> entry : after.items().entrySet()) {
            if (entry.getValue() > before.items().getOrDefault(entry.getKey(), 0L)) return false;
        }
        return true;
    }

    public static boolean noMesoCreation(Snapshot before, Snapshot after) {
        return before != null && after != null && after.mesos() <= before.mesos();
    }

    public static long quantity(Snapshot snapshot, int itemId) {
        return snapshot == null ? 0L : snapshot.items().getOrDefault(itemId, 0L);
    }

    private static String describeDifference(Snapshot before, Snapshot after, long mesoDelta) {
        TreeSet<Integer> ids = new TreeSet<>();
        ids.addAll(before.items().keySet());
        ids.addAll(after.items().keySet());
        StringBuilder changed = new StringBuilder();
        for (int id : ids) {
            long a = before.items().getOrDefault(id, 0L);
            long b = after.items().getOrDefault(id, 0L);
            if (a == b) continue;
            if (changed.length() > 0) changed.append(',');
            changed.append(id).append(':').append(a).append("->").append(b);
            if (changed.length() > 160) {
                changed.append("...");
                break;
            }
        }
        return "mesoDelta=" + mesoDelta + ";items=" + (changed.length() == 0 ? "same" : changed);
    }

    public record Snapshot(long mesos, Map<Integer, Long> items) {}

    public record Conservation(boolean itemsEqual, boolean mesosEqual, long mesoDelta, String reason) {
        public boolean fullyConserved() {
            return itemsEqual && mesosEqual;
        }
    }
}
