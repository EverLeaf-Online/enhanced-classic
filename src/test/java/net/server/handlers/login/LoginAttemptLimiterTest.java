package net.server.handlers.login;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

class LoginAttemptLimiterTest {

    @Test
    void blocksAfterRepeatedFailuresAndSuccessClearsState() {
        String host = "203.0.113.7:40000";
        String account = "EverLeafRateLimitTest";

        LoginAttemptLimiter.recordSuccess(host, account);
        assertTrue(LoginAttemptLimiter.allowAttempt(host, account));

        for (int i = 0; i < 7; i++) {
            LoginAttemptLimiter.recordFailure(host, account);
            assertTrue(LoginAttemptLimiter.allowAttempt(host, account));
        }

        LoginAttemptLimiter.recordFailure(host, account);
        assertFalse(LoginAttemptLimiter.allowAttempt(host, account));

        LoginAttemptLimiter.recordSuccess(host, account);
        assertTrue(LoginAttemptLimiter.allowAttempt(host, account));
    }

    @Test
    void separatesAccountsAndHosts() {
        String host = "203.0.113.9:40000";
        String account = "EverLeafRateLimitIsolation";
        LoginAttemptLimiter.recordSuccess(host, account);

        for (int i = 0; i < 8; i++) {
            LoginAttemptLimiter.recordFailure(host, account);
        }

        assertFalse(LoginAttemptLimiter.allowAttempt(host, account));
        assertTrue(LoginAttemptLimiter.allowAttempt(host, account + "Other"));
        assertTrue(LoginAttemptLimiter.allowAttempt("203.0.113.10:40000", account));

        LoginAttemptLimiter.recordSuccess(host, account);
    }
}
