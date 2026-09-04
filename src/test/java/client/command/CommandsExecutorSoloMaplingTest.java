package client.command;

import org.junit.jupiter.api.Test;
import soloMapling.ArtificialPlayer.BotQaSoakRunner;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

class CommandsExecutorSoloMaplingTest {
    @Test
    void explicitlyRegistersBothSoloMaplingGm4ControlSurfaces() throws IOException {
        // CommandsExecutor eagerly constructs every registered command. Bootstrapping that global singleton
        // inside the shared Maven test JVM can initialize WZ-backed factories before their isolated tests set
        // a temporary wz-path. This source-level regression guard checks the exact failure mode we care about
        // (forgetting the manual registration) without contaminating unrelated static WZ state.
        String source = Files.readString(Path.of("src/main/java/client/command/CommandsExecutor.java"));

        assertTrue(source.contains("addCommand(\"qabot\", 4, QaBotCommand.class);"),
                "!qabot must be explicitly registered as GM4");
        assertTrue(source.contains("addCommand(\"qabotops\", 4, QaBotOpsCommand.class);"),
                "!qabotops must be explicitly registered as GM4");
    }

    @Test
    void soakRunnerFailsClosedWithoutExplicitArmToken() {
        BotQaSoakRunner.SoakResult result = BotQaSoakRunner.start(1, 1);
        assertFalse(result.success());
        assertEquals("explicit-arm-token-required", result.reason());
    }
}
