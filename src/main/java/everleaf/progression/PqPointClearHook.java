package everleaf.progression;

import client.Character;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.Collection;
import java.util.OptionalInt;

/**
 * Server-authoritative bridge from the legacy event system into PQ Points.
 * Only explicitly whitelisted PQ EventManager names can award currency.
 */
public final class PqPointClearHook {
    private static final Logger log = LoggerFactory.getLogger(PqPointClearHook.class);

    private PqPointClearHook() {
    }

    public static void onEventCleared(String eventName, String instanceName, Collection<Character> players) {
        if (eventName == null || instanceName == null || players == null || players.isEmpty()) {
            return;
        }

        PqPointService service = EverleafProgressionRuntime.pqPointService();
        OptionalInt configuredAward = service.clearAward(eventName);
        if (configuredAward.isEmpty()) {
            return;
        }

        int award = configuredAward.getAsInt();
        for (Character chr : players) {
            if (chr == null || chr.getClient() == null || chr.getClient().getAccID() <= 0) {
                continue;
            }

            try {
                PqPointRepository.MutationResult result = service.awardClear(
                        chr.getClient().getAccID(),
                        chr.getId(),
                        eventName,
                        instanceName
                );
                if (result.success()) {
                    chr.dropMessage(5, "PQ Clear: +" + award + " PQ Point" + (award == 1 ? "" : "s") +
                            " (Balance: " + result.balanceAfter() + ")");
                } else if (!"duplicate_reason".equals(result.reason())) {
                    log.warn("PQ Point clear award rejected: event={}, instance={}, account={}, reason={}",
                            eventName, instanceName, chr.getClient().getAccID(), result.reason());
                }
            } catch (RuntimeException e) {
                // A reward subsystem failure must never trap players inside a PQ
                // or prevent the underlying legacy clear/dispose path.
                log.error("Failed to award PQ Points for event {} instance {} character {}",
                        eventName, instanceName, chr.getId(), e);
            }
        }
    }
}
