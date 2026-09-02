package soloMapling;

import java.time.LocalTime;
import java.time.format.DateTimeFormatter;

/**
 * Minimal SoloMapling debug helper retained for GCMove compatibility.
 * Debug output is disabled unless explicitly enabled in code and a debugger is attached.
 */
public final class DebugUtilities {
    private static final DateTimeFormatter TIME_FORMATTER = DateTimeFormatter.ofPattern("HH:mm:ss.SSS");

    private DebugUtilities() {
    }

    private static boolean isDebugging() {
        return java.lang.management.ManagementFactory.getRuntimeMXBean()
                .getInputArguments()
                .toString()
                .contains("jdwp");
    }

    public static void debugprint(Object... variables) {
        boolean printDebug = false;
        if (!printDebug || !isDebugging()) {
            return;
        }

        StringBuilder sb = new StringBuilder();
        sb.append('[').append(LocalTime.now().format(TIME_FORMATTER)).append("] DEBUG: ");
        for (int i = 0; i < variables.length; i++) {
            sb.append(variables[i]);
            if (i < variables.length - 1) {
                sb.append(", ");
            }
        }
        System.out.println(sb);
    }

    public static String fmt(String template, Object... args) {
        String result = template;
        for (Object arg : args) {
            result = result.replaceFirst("\\{\\}", String.valueOf(arg));
        }
        return result;
    }
}
