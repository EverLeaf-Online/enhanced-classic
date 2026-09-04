package net.server.handlers.login;

import client.Client;
import net.AbstractPacketHandler;
import net.packet.InPacket;
import net.server.Server;
import net.server.coordinator.session.Hwid;
import net.server.coordinator.session.SessionCoordinator;
import net.server.coordinator.session.SessionCoordinator.AntiMulticlientResult;
import net.server.world.World;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import tools.PacketCreator;
import tools.Randomizer;

import java.net.InetAddress;
import java.net.UnknownHostException;

public final class ViewAllCharRegisterPicHandler extends AbstractPacketHandler {
    private static final Logger log = LoggerFactory.getLogger(ViewAllCharRegisterPicHandler.class);

    private static int parseAntiMulticlientError(AntiMulticlientResult res) {
        return switch (res) {
            case REMOTE_PROCESSING -> 10;
            case REMOTE_LOGGEDIN -> 7;
            case REMOTE_NO_MATCH -> 17;
            case COORDINATOR_ERROR -> 8;
            default -> 9;
        };
    }

    @Override
    public final void handlePacket(InPacket p, Client c) {
        p.readByte();
        int charId = p.readInt();
        p.readInt(); // please don't let the client choose which world they should login

        String mac = p.readString();
        String hostString = p.readString();

        final Hwid hwid;
        try {
            hwid = Hwid.fromHostString(hostString);
        } catch (IllegalArgumentException e) {
            log.warn("Invalid host string: {}", hostString, e);
            c.sendPacket(PacketCreator.getAfterLoginError(17));
            return;
        }

        c.updateMacs(mac);
        c.updateHwid(hwid);

        if (c.hasBannedMac() || c.hasBannedHWID()) {
            SessionCoordinator.getInstance().closeSession(c, true);
            return;
        }

        Server server = Server.getInstance();
        if (!server.haveCharacterEntry(c.getAccID(), charId)) {
            SessionCoordinator.getInstance().closeSession(c, true);
            return;
        }

        c.setWorld(server.getCharacterWorld(charId));
        World wserv = c.getWorldServer();
        if (wserv == null || wserv.isWorldCapacityFull() || wserv.getChannelsSize() <= 0) {
            c.sendPacket(PacketCreator.getAfterLoginError(10));
            return;
        }

        final int channel;
        try {
            channel = Randomizer.rand(1, wserv.getChannelsSize());
            c.setChannel(channel);
        } catch (RuntimeException e) {
            log.error("Unable to choose a PIC-registration view-all channel for world={} charId={}", c.getWorld(), charId, e);
            c.sendPacket(PacketCreator.getAfterLoginError(10));
            return;
        }

        final InetAddress channelAddress;
        final int channelPort;
        try {
            String[] socket = server.getInetSocket(c, c.getWorld(), channel);
            if (socket == null || socket.length < 2 || socket[0] == null || socket[0].isBlank()) {
                throw new IllegalStateException("Channel endpoint is unavailable");
            }
            channelAddress = InetAddress.getByName(socket[0]);
            channelPort = Integer.parseInt(socket[1]);
            if (channelPort < 1 || channelPort > 65535) {
                throw new IllegalArgumentException("Channel port is outside the valid TCP range");
            }
        } catch (UnknownHostException | RuntimeException e) {
            log.error("Unable to prepare view-all PIC-registration handoff for world={} channel={} charId={}",
                    c.getWorld(), c.getChannel(), charId, e);
            c.sendPacket(PacketCreator.getAfterLoginError(10));
            return;
        }

        AntiMulticlientResult res = SessionCoordinator.getInstance().attemptGameSession(c, c.getAccID(), hwid);
        if (res != AntiMulticlientResult.SUCCESS) {
            c.sendPacket(PacketCreator.getAfterLoginError(parseAntiMulticlientError(res)));
            return;
        }

        String pic = p.readString();
        c.setPic(pic);
        server.unregisterLoginState(c);
        c.setCharacterOnSessionTransitionState(charId);
        c.sendPacket(PacketCreator.getServerIP(channelAddress, channelPort, charId));
    }
}
