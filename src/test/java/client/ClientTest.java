package client;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;

class ClientTest {
    @Test
    void sessionCleanupIsSafeBeforeNettyChannelActivation() {
        Client client = Client.createMock();

        assertDoesNotThrow(client::closeSession);
        assertDoesNotThrow(client::disconnectSession);
    }
}
