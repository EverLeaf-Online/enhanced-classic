package client;

import io.netty.handler.timeout.IdleStateEvent;
import net.packet.Packet;

/**
 * Shared headless Client implementation used by SoloMapling artificial players.
 *
 * <p>Bots have no Netty socket or account/session row. World and channel routing
 * remain active while network/session side effects are intentionally disabled.</p>
 */
public class BotClient extends Client {

    public BotClient(int world, int channel) {
        super(null, -1, "bot", null, world, channel);
    }

    @Override
    public void sendPacket(Packet packet) {
        // Headless bots have no socket. Outbound packets intentionally fizzle out.
    }

    @Override
    public boolean isLoggedIn() {
        return true;
    }

    @Override
    public void updateLoginState(int newState) {
        // Headless bots have no account row or online-session registration.
    }

    @Override
    public void disconnectSession() {
        // Headless bots have no Netty session to disconnect.
    }

    @Override
    public void closeSession() {
        // Headless bots have no Netty session to close.
    }

    @Override
    public void checkIfIdle(final IdleStateEvent event) {
        // Headless bots are not part of the Netty idle pipeline.
    }

    @Override
    public long getLastPacket() {
        return System.currentTimeMillis();
    }
}
