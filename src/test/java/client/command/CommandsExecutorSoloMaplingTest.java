package client.command;

import client.command.commands.gm4.QaBotCommand;
import client.command.commands.gm4.QaBotOpsCommand;
import org.junit.jupiter.api.Test;

import java.lang.reflect.Field;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertNotNull;

class CommandsExecutorSoloMaplingTest {
    @Test
    void registersBothSoloMaplingGm4ControlSurfaces() throws Exception {
        CommandsExecutor executor = CommandsExecutor.getInstance();
        Field registeredCommands = CommandsExecutor.class.getDeclaredField("registeredCommands");
        registeredCommands.setAccessible(true);

        @SuppressWarnings("unchecked")
        Map<String, Command> commands = (Map<String, Command>) registeredCommands.get(executor);

        Command qaBot = commands.get("qabot");
        assertNotNull(qaBot, "!qabot must be explicitly registered");
        assertInstanceOf(QaBotCommand.class, qaBot);
        assertEquals(4, qaBot.getRank());

        Command qaBotOps = commands.get("qabotops");
        assertNotNull(qaBotOps, "!qabotops must be explicitly registered");
        assertInstanceOf(QaBotOpsCommand.class, qaBotOps);
        assertEquals(4, qaBotOps.getRank());
    }
}
