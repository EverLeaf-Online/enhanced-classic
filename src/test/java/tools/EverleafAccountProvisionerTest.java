package tools;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertThrows;

class EverleafAccountProvisionerTest {
    @Test
    void acceptsClosedAlphaCredentials() {
        assertDoesNotThrow(() -> EverleafAccountProvisioner.validateUsername("Alpha01"));
        assertDoesNotThrow(() -> EverleafAccountProvisioner.validatePassword("mapleAlpha2026".toCharArray()));
    }

    @Test
    void rejectsUnsafeUsernames() {
        assertThrows(IllegalArgumentException.class,
                () -> EverleafAccountProvisioner.validateUsername("abc"));
        assertThrows(IllegalArgumentException.class,
                () -> EverleafAccountProvisioner.validateUsername("alpha user"));
    }

    @Test
    void rejectsWeakOrOversizedPasswords() {
        assertThrows(IllegalArgumentException.class,
                () -> EverleafAccountProvisioner.validatePassword("onlyletters".toCharArray()));
        assertThrows(IllegalArgumentException.class,
                () -> EverleafAccountProvisioner.validatePassword("1234567890".toCharArray()));
        assertThrows(IllegalArgumentException.class,
                () -> EverleafAccountProvisioner.validatePassword(("A1" + "x".repeat(71)).toCharArray()));
    }
}
