package net.server.handlers.login;

import java.util.Locale;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

/**
 * Small in-memory guard against password-guessing bursts on the login server.
 * The limiter is deliberately local to a login-server process: it adds a cheap
 * first line of defense without introducing database writes on failed logins.
 */
final class LoginAttemptLimiter {
    private static final long WINDOW_MILLIS = 60_000L;
    private static final long LOCKOUT_MILLIS = 60_000L;
    private static final int MAX_FAILURES_PER_WINDOW = 8;
    private static final int MAX_TRACKED_KEYS = 20_000;

    private static final Map<String, AttemptState> ATTEMPTS = new ConcurrentHashMap<>();

    private LoginAttemptLimiter() {
    }

    static boolean allowAttempt(String remoteHost, String accountName) {
        long now = System.currentTimeMillis();
        String key = key(remoteHost, accountName);
        AttemptState state = ATTEMPTS.get(key);
        if (state == null) {
            return true;
        }
        synchronized (state) {
            if (state.lockedUntil > now) {
                return false;
            }
            if (now - state.windowStarted >= WINDOW_MILLIS) {
                ATTEMPTS.remove(key, state);
            }
            return true;
        }
    }

    static void recordFailure(String remoteHost, String accountName) {
        long now = System.currentTimeMillis();
        if (ATTEMPTS.size() > MAX_TRACKED_KEYS) {
            prune(now);
        }

        String key = key(remoteHost, accountName);
        AttemptState state = ATTEMPTS.computeIfAbsent(key, ignored -> new AttemptState(now));
        synchronized (state) {
            if (now - state.windowStarted >= WINDOW_MILLIS) {
                state.windowStarted = now;
                state.failures = 0;
                state.lockedUntil = 0L;
            }
            state.failures++;
            if (state.failures >= MAX_FAILURES_PER_WINDOW) {
                state.lockedUntil = now + LOCKOUT_MILLIS;
            }
        }
    }

    static void recordSuccess(String remoteHost, String accountName) {
        ATTEMPTS.remove(key(remoteHost, accountName));
    }

    private static void prune(long now) {
        ATTEMPTS.entrySet().removeIf(entry -> {
            AttemptState state = entry.getValue();
            synchronized (state) {
                return state.lockedUntil <= now && now - state.windowStarted >= WINDOW_MILLIS * 2;
            }
        });
    }

    private static String key(String remoteHost, String accountName) {
        String normalizedHost = remoteHost == null ? "unknown" : remoteHost.trim().toLowerCase(Locale.ROOT);
        String normalizedAccount = accountName == null ? "" : accountName.trim().toLowerCase(Locale.ROOT);
        return normalizedHost + '|' + normalizedAccount;
    }

    private static final class AttemptState {
        private long windowStarted;
        private int failures;
        private long lockedUntil;

        private AttemptState(long now) {
            this.windowStarted = now;
        }
    }
}
