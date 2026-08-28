import net.encryption.InitializationVector;
import net.encryption.MapleAESOFB;
import net.encryption.MapleCustomEncryption;

import java.io.ByteArrayOutputStream;
import java.io.DataInputStream;
import java.io.OutputStream;
import java.lang.reflect.Constructor;
import java.net.InetSocketAddress;
import java.net.Socket;
import java.nio.charset.StandardCharsets;

public final class EverLeafGameLoginProbe {
    private static void writeLeShort(ByteArrayOutputStream out, int value) {
        out.write(value & 0xff);
        out.write((value >>> 8) & 0xff);
    }

    private static void writeString(ByteArrayOutputStream out, String value) {
        byte[] bytes = value.getBytes(StandardCharsets.US_ASCII);
        writeLeShort(out, bytes.length);
        out.writeBytes(bytes);
    }

    private static InitializationVector iv(byte[] bytes) throws Exception {
        Constructor<InitializationVector> constructor = InitializationVector.class.getDeclaredConstructor(byte[].class);
        constructor.setAccessible(true);
        return constructor.newInstance((Object) bytes);
    }

    private static int packetLength(byte[] header) {
        return (((header[1] ^ header[3]) & 0xff) << 8) | ((header[0] ^ header[2]) & 0xff);
    }

    public static void main(String[] args) throws Exception {
        if (args.length != 3 && args.length != 4) {
            throw new IllegalArgumentException("Usage: host port username [password]");
        }
        String host = args[0];
        int port = Integer.parseInt(args[1]);
        String username = args[2];
        String password = args.length == 4 ? args[3] : System.getenv("EVERLEAF_TEST_PASSWORD");
        if (password == null || password.isEmpty()) {
            throw new IllegalArgumentException("Provide the password argument or EVERLEAF_TEST_PASSWORD.");
        }

        try (Socket socket = new Socket()) {
            socket.connect(new InetSocketAddress(host, port), 5000);
            socket.setSoTimeout(8000);
            DataInputStream in = new DataInputStream(socket.getInputStream());
            OutputStream out = socket.getOutputStream();

            int helloLength = Short.toUnsignedInt(Short.reverseBytes(in.readShort()));
            byte[] hello = in.readNBytes(helloLength);
            if (hello.length != helloLength || helloLength < 13) throw new IllegalStateException("Invalid v83 hello packet");
            int version = (hello[0] & 0xff) | ((hello[1] & 0xff) << 8);
            byte[] serverReceiveIv = new byte[] { hello[5], hello[6], hello[7], hello[8] };
            byte[] serverSendIv = new byte[] { hello[9], hello[10], hello[11], hello[12] };

            MapleAESOFB clientSend = new MapleAESOFB(iv(serverReceiveIv), (short) version);
            MapleAESOFB clientReceive = new MapleAESOFB(iv(serverSendIv), (short) (0xffff - version));

            ByteArrayOutputStream plain = new ByteArrayOutputStream();
            writeLeShort(plain, 0x01);
            writeString(plain, username);
            writeString(plain, password);
            plain.writeBytes(new byte[6]);
            plain.writeBytes(new byte[] { 0x45, 0x32, 0x45, 0x31 });
            byte[] encrypted = plain.toByteArray();
            byte[] requestHeader = clientSend.getPacketHeader(encrypted.length);
            MapleCustomEncryption.encryptData(encrypted);
            clientSend.crypt(encrypted);
            out.write(requestHeader);
            out.write(encrypted);
            out.flush();

            byte[] header = in.readNBytes(4);
            if (header.length != 4) throw new IllegalStateException("No login response packet");
            byte[] response = in.readNBytes(packetLength(header));
            clientReceive.crypt(response);
            MapleCustomEncryption.decryptData(response);
            int opcode = (response[0] & 0xff) | ((response[1] & 0xff) << 8);
            boolean authenticated = response.length >= 6 && response[2] == 0 && response[3] == 0 && response[4] == 0 && response[5] == 0;
            System.out.printf("GAME_PROTOCOL_VERSION=%d%n", version);
            System.out.printf("LOGIN_RESPONSE_OPCODE=%d%n", opcode);
            System.out.printf("GAME_LOGIN_AUTHENTICATED=%s%n", authenticated);
            if (!authenticated) System.exit(2);
        }
    }
}
