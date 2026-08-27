package config;

import org.junit.jupiter.api.Test;
import org.w3c.dom.Document;
import org.w3c.dom.Element;
import org.w3c.dom.NodeList;

import javax.xml.parsers.DocumentBuilderFactory;
import java.io.InputStream;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertTrue;

class LogRotationConfigurationTest {
    @Test
    void everyFileAppenderRotatesToCompressedArchives() throws Exception {
        DocumentBuilderFactory factory = DocumentBuilderFactory.newInstance();
        factory.setFeature("http://apache.org/xml/features/disallow-doctype-decl", true);
        factory.setExpandEntityReferences(false);

        try (InputStream input = getClass().getResourceAsStream("/log4j2.xml")) {
            assertNotNull(input);
            Document document = factory.newDocumentBuilder().parse(input);
            assertEquals(0, document.getElementsByTagName("File").getLength());

            NodeList rollingFiles = document.getElementsByTagName("RollingFile");
            assertEquals(7, rollingFiles.getLength());
            for (int index = 0; index < rollingFiles.getLength(); index++) {
                Element appender = (Element) rollingFiles.item(index);
                assertTrue(appender.getAttribute("filePattern").endsWith(".gz"));
                assertTrue(appender.getElementsByTagName("TimeBasedTriggeringPolicy").getLength() > 0);
                assertTrue(appender.getElementsByTagName("SizeBasedTriggeringPolicy").getLength() > 0);
            }
        }
    }
}
