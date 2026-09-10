package client.command;

import org.junit.jupiter.api.Test;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

class CommandsExecutorGm2PermissionTest {
    @Test
    void restrictsGachaListLootAndMobSkillToGm2() throws IOException {
        // Keep this source-level like the existing SoloMapling command registration guard.
        // Constructing CommandsExecutor eagerly instantiates command classes and can initialize
        // WZ-backed state in the shared Maven test JVM.
        String source = Files.readString(Path.of("src/main/java/client/command/CommandsExecutor.java"));

        assertTrue(source.contains("addCommand(\"gachalist\", 2, GachaListCommand.class);"),
                "gachalist must require GM rank 2");
        assertTrue(source.contains("addCommand(\"loot\", 2, LootCommand.class);"),
                "loot must require GM rank 2");
        assertTrue(source.contains("addCommand(\"mobskill\", 2, MobSkillCommand.class);"),
                "mobskill must require GM rank 2");

        assertFalse(source.contains("addCommand(\"gachalist\", GachaListCommand.class);"),
                "gachalist must not use the rank-0 registration overload");
        assertFalse(source.contains("addCommand(\"loot\", LootCommand.class);"),
                "loot must not use the rank-0 registration overload");
        assertFalse(source.contains("addCommand(\"mobskill\", MobSkillCommand.class);"),
                "mobskill must not use the rank-0 registration overload");
    }
}
