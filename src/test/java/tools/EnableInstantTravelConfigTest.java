package tools;

import org.junit.jupiter.api.Test;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;

import static org.junit.jupiter.api.Assertions.assertTrue;

class EnableInstantTravelConfigTest {
    @Test
    void productionConfigDeclaresInstantTravel() throws IOException {
        String config = Files.readString(Path.of("config.yaml"));
        assertTrue(config.contains("instant_travel: true"));
    }
}
