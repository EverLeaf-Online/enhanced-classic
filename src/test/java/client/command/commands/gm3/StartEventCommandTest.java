package client.command.commands.gm3;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

class StartEventCommandTest {
    @Test
    void defaultsToFiftyPlayersWhenNoLimitIsProvided() {
        assertEquals(50, StartEventCommand.parsePlayerLimit(new String[]{}));
    }

    @Test
    void acceptsExactlyOnePositivePlayerLimit() {
        assertEquals(1, StartEventCommand.parsePlayerLimit(new String[]{"1"}));
        assertEquals(25, StartEventCommand.parsePlayerLimit(new String[]{"25"}));
        assertEquals(100, StartEventCommand.parsePlayerLimit(new String[]{"100"}));
    }

    @Test
    void rejectsInvalidPlayerLimits() {
        assertThrows(IllegalArgumentException.class,
                () -> StartEventCommand.parsePlayerLimit(new String[]{"0"}));
        assertThrows(IllegalArgumentException.class,
                () -> StartEventCommand.parsePlayerLimit(new String[]{"-1"}));
        assertThrows(IllegalArgumentException.class,
                () -> StartEventCommand.parsePlayerLimit(new String[]{"abc"}));
        assertThrows(IllegalArgumentException.class,
                () -> StartEventCommand.parsePlayerLimit(new String[]{"25", "extra"}));
    }
}
