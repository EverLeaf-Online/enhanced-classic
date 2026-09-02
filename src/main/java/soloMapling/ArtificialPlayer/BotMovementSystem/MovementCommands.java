package soloMapling.ArtificialPlayer.BotMovementSystem;

import client.Character;

import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicBoolean;

/**
 * Minimal EverLeaf compatibility surface for GCMove.
 *
 * The full SoloMapling recorded-path movement subsystem is intentionally not
 * imported yet. GCMove currently needs only the shared per-character movement
 * lock so two movement engines cannot drive the same headless bot at once.
 */
public final class MovementCommands {
    private static final ConcurrentHashMap<Integer, AtomicBoolean> MOVEMENT_LOCKS = new ConcurrentHashMap<>();

    private MovementCommands() {
    }

    public static boolean tryAcquireMovementLock(Character character) {
        if (character == null) {
            return false;
        }
        AtomicBoolean lock = MOVEMENT_LOCKS.computeIfAbsent(character.getId(), ignored -> new AtomicBoolean(false));
        return lock.compareAndSet(false, true);
    }

    public static void releaseMovementLock(Character character) {
        if (character == null) {
            return;
        }
        AtomicBoolean lock = MOVEMENT_LOCKS.get(character.getId());
        if (lock != null) {
            lock.set(false);
        }
    }
}
