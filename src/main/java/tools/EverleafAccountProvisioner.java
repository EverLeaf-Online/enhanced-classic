package tools;

import java.io.Console;
import java.nio.charset.StandardCharsets;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.SQLException;
import java.util.Arrays;
import java.util.regex.Pattern;

/** Interactive, closed-alpha account provisioning without command-line secrets. */
public final class EverleafAccountProvisioner {
    private static final Pattern USERNAME = Pattern.compile("[A-Za-z0-9]{4,13}");
    private static final int MIN_PASSWORD_LENGTH = 10;
    private static final int MAX_PASSWORD_BYTES = 72;

    private EverleafAccountProvisioner() {}

    public static void main(String[] args) {
        Console console = System.console();
        if (console == null) {
            System.err.println("An interactive terminal is required. Reconnect with SSH terminal allocation enabled.");
            System.exit(2);
        }

        String usernameInput = console.readLine("Closed-alpha username: ");
        if (usernameInput == null) {
            System.err.println("Account was not created: input ended before a username was entered");
            System.exit(2);
        }
        String username = usernameInput.trim();
        char[] password = console.readPassword("Password: ");
        char[] confirmation = console.readPassword("Confirm password: ");
        try {
            validateUsername(username);
            validatePassword(password);
            if (!Arrays.equals(password, confirmation)) {
                throw new IllegalArgumentException("passwords do not match");
            }

            String passwordHash = BCrypt.hashpw(new String(password), BCrypt.gensalt(12));
            createAccount(username, passwordHash, System.getenv());
            console.printf("Created closed-alpha account '%s'.%n", username);
        } catch (IllegalArgumentException | SQLException exception) {
            System.err.println("Account was not created: " + safeMessage(exception));
            System.exit(1);
        } finally {
            clear(password);
            clear(confirmation);
        }
    }

    static void validateUsername(String username) {
        if (username == null || !USERNAME.matcher(username).matches()) {
            throw new IllegalArgumentException("username must be 4-13 ASCII letters or digits");
        }
    }

    static void validatePassword(char[] password) {
        if (password == null || password.length < MIN_PASSWORD_LENGTH) {
            throw new IllegalArgumentException("password must contain at least 10 characters");
        }
        String value = new String(password);
        if (value.getBytes(StandardCharsets.UTF_8).length > MAX_PASSWORD_BYTES) {
            throw new IllegalArgumentException("password must be at most 72 UTF-8 bytes");
        }
        boolean hasLetter = value.chars().anyMatch(Character::isLetter);
        boolean hasDigit = value.chars().anyMatch(Character::isDigit);
        if (!hasLetter || !hasDigit) {
            throw new IllegalArgumentException("password must include at least one letter and one digit");
        }
    }

    private static void createAccount(String username, String passwordHash,
                                      java.util.Map<String, String> environment) throws SQLException {
        String host = requiredEnvironment(environment, "EVERLEAF_DB_HOST");
        String user = requiredEnvironment(environment, "EVERLEAF_DB_USER");
        String password = requiredEnvironment(environment, "EVERLEAF_DB_PASS");
        String urlFormat = environment.getOrDefault(
                "EVERLEAF_DB_URL_FORMAT", "jdbc:mysql://%s:3306/cosmic");
        String url = String.format(urlFormat, host);

        try (Connection connection = DriverManager.getConnection(url, user, password);
             PreparedStatement statement = connection.prepareStatement(
                     "INSERT INTO accounts (name, password) VALUES (?, ?)")) {
            statement.setString(1, username);
            statement.setString(2, passwordHash);
            statement.executeUpdate();
        } catch (SQLException exception) {
            if ("23000".equals(exception.getSQLState())) {
                throw new IllegalArgumentException("that username already exists");
            }
            throw exception;
        }
    }

    private static String requiredEnvironment(java.util.Map<String, String> environment, String key) {
        String value = environment.get(key);
        if (value == null || value.isBlank()) {
            throw new IllegalArgumentException(key + " is not configured");
        }
        return value;
    }

    private static String safeMessage(Exception exception) {
        if (exception instanceof SQLException) {
            return "database operation failed; check the server log for details";
        }
        return exception.getMessage();
    }

    private static void clear(char[] value) {
        if (value != null) Arrays.fill(value, '\0');
    }
}
