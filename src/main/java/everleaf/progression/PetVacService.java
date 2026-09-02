package everleaf.progression;

import client.Character;
import client.inventory.Pet;
import server.maps.MapItem;
import server.maps.MapObject;
import server.maps.MapObjectType;

import java.util.Arrays;
import java.util.List;
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;

/**
 * Conservative server-authoritative Pet Vac implementation.
 *
 * Pet Vac augments normal pet looting; it does not bypass pet pouch/magnet,
 * item-ignore, ownership, quest pickup, or inventory checks. Active event/PQ/
 * boss instances are excluded so vacuuming cannot skip encounter mechanics.
 */
public final class PetVacService {
    public static final double VACUUM_RANGE = 260.0;
    public static final int MAX_ITEMS_PER_TRIGGER = 5;
    public static final long TRIGGER_COOLDOWN_MS = 300L;
    private static final long ENTITLEMENT_CACHE_MS = 30_000L;

    private static final PetVacService INSTANCE = new PetVacService();

    private final ConcurrentHashMap<Integer, Long> lastTriggerByCharacter = new ConcurrentHashMap<>();
    private final ConcurrentHashMap<Integer, EntitlementCacheEntry> entitlementCache = new ConcurrentHashMap<>();

    private PetVacService() {
    }

    public static PetVacService getInstance() {
        return INSTANCE;
    }

    public void invalidateEntitlementCache(int accountId) {
        entitlementCache.remove(accountId);
    }

    public boolean isActive(Character chr) {
        if (chr == null || chr.getClient() == null || chr.getClient().getAccID() <= 0) return false;
        int accountId = chr.getClient().getAccID();
        long now = System.currentTimeMillis();
        EntitlementCacheEntry cached = entitlementCache.get(accountId);
        if (cached != null && now - cached.checkedAtMs() < ENTITLEMENT_CACHE_MS) {
            return cached.active();
        }

        boolean active;
        try {
            active = EverleafProgressionRuntime.accountEntitlementService()
                    .isActive(accountId, AccountEntitlementService.PET_VAC);
        } catch (RuntimeException e) {
            // Fail closed. Missing/unavailable entitlement storage should never
            // turn into free vacuum access or disrupt ordinary pet movement.
            active = false;
        }
        entitlementCache.put(accountId, new EntitlementCacheEntry(active, now));
        return active;
    }

    public void onPetMoved(Character chr, Pet pet, int petIndex) {
        if (chr == null || pet == null || !pet.isSummoned()) return;
        if (chr.getMap() == null || chr.getEventInstance() != null) return;
        if (!isActive(chr)) return;

        long now = System.currentTimeMillis();
        Long previous = lastTriggerByCharacter.put(chr.getId(), now);
        if (previous != null && now - previous < TRIGGER_COOLDOWN_MS) return;

        List<MapObject> nearby = chr.getMap().getMapObjectsInRange(
                pet.getPos(),
                VACUUM_RANGE * VACUUM_RANGE,
                Arrays.asList(MapObjectType.ITEM)
        );

        int attempted = 0;
        for (MapObject object : nearby) {
            if (attempted >= MAX_ITEMS_PER_TRIGGER) break;
            if (!(object instanceof MapItem mapItem)) continue;
            if (!canPetLoot(chr, mapItem)) continue;

            try {
                // Character.pickupItem remains the final authority for map-drop
                // ownership, quest requirements, inventory space, NX cards, etc.
                chr.pickupItem(object, petIndex);
                attempted++;
            } catch (RuntimeException ignored) {
                // Drops can disappear concurrently (other party member pickup,
                // expiry, map cleanup). Continue with the remaining candidates.
            }
        }
    }

    private boolean canPetLoot(Character chr, MapItem mapItem) {
        if (mapItem.getMeso() > 0) {
            if (!chr.isEquippedMesoMagnet()) return false;
            if (chr.isEquippedPetItemIgnore()) {
                Set<Integer> ignored = chr.getExcludedItems();
                return ignored.isEmpty() || !ignored.contains(Integer.MAX_VALUE);
            }
            return true;
        }

        if (!chr.isEquippedItemPouch() || mapItem.getItem() == null) return false;
        if (chr.isEquippedPetItemIgnore()) {
            Set<Integer> ignored = chr.getExcludedItems();
            return ignored.isEmpty() || !ignored.contains(mapItem.getItem().getItemId());
        }
        return true;
    }

    private record EntitlementCacheEntry(boolean active, long checkedAtMs) {
    }
}
