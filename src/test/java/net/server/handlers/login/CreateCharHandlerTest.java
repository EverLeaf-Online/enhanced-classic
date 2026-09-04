package net.server.handlers.login;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

class CreateCharHandlerTest {

    @Test
    void allowsOnlyCurrentlySupportedCharacterFamilies() {
        assertTrue(CreateCharHandler.isSupportedCharacterType(CreateCharHandler.TYPE_CYGNUS));
        assertTrue(CreateCharHandler.isSupportedCharacterType(CreateCharHandler.TYPE_EXPLORER));
        assertTrue(CreateCharHandler.isSupportedCharacterType(CreateCharHandler.TYPE_ARAN));
        assertTrue(CreateCharHandler.isSupportedCharacterType(CreateCharHandler.TYPE_EVAN));
    }

    @Test
    void rejectsFutureAndMalformedCharacterFamilies() {
        assertFalse(CreateCharHandler.isSupportedCharacterType(-1));
        assertFalse(CreateCharHandler.isSupportedCharacterType(4));
        assertFalse(CreateCharHandler.isSupportedCharacterType(5));
        assertFalse(CreateCharHandler.isSupportedCharacterType(100));
        assertFalse(CreateCharHandler.isSupportedCharacterType(Integer.MAX_VALUE));
    }
}
