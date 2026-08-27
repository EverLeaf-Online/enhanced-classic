using System.Diagnostics;
using System.Net.Http.Json;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;

namespace EverLeaf.Launcher;

public sealed record LauncherSession(string Username, string AccessToken, DateTimeOffset ExpiresAt);
public sealed record LoginRequest(string Username, string Password);
public sealed record LoginResponse(string AccessToken, DateTimeOffset ExpiresAt);
public sealed record ServerStatus(bool Online, string Message, string Version);
public sealed record PatchEntry(string Path, string Url, string Sha256, long Size);
public sealed record PatchManifest(string Version, IReadOnlyList<PatchEntry> Files);
public sealed record SignedManifest(string Payload, string Signature);

public static class LauncherConfiguration
{
    public static readonly Uri ApiBase = new("https://132-145-141-79.sslip.io/");
    public static readonly Uri ManifestUri = new(ApiBase, "v1/launcher/manifest");
    public const string GameExecutable = "MapleStory.exe";

    // Replace only through a source release when the production signing key is provisioned.
    public const string ManifestPublicKeyPem = """
-----BEGIN PUBLIC KEY-----
MFwwDQYJKoZIhvcNAQEBBQADSwAwSAJBAJ6Z0+EverLeafProductionKeyPending
-----END PUBLIC KEY-----
""";
}

public sealed class LauncherApi : IDisposable
{
    private readonly HttpClient _http = new()
    {
        BaseAddress = LauncherConfiguration.ApiBase,
        Timeout = TimeSpan.FromSeconds(15)
    };

    public async Task<ServerStatus> GetStatusAsync(CancellationToken cancellationToken) =>
        await _http.GetFromJsonAsync<ServerStatus>("v1/launcher/status", cancellationToken)
        ?? new(false, "No status response", "unknown");

    public async Task<LauncherSession> LoginAsync(string username, string password, CancellationToken cancellationToken)
    {
        using var response = await _http.PostAsJsonAsync(
            "v1/launcher/login", new LoginRequest(username, password), cancellationToken);
        if (!response.IsSuccessStatusCode)
        {
            throw new InvalidOperationException(response.StatusCode == System.Net.HttpStatusCode.Unauthorized
                ? "Incorrect username or password."
                : "Login service is unavailable.");
        }

        var login = await response.Content.ReadFromJsonAsync<LoginResponse>(cancellationToken: cancellationToken)
                    ?? throw new InvalidOperationException("Invalid login response.");
        return new(username, login.AccessToken, login.ExpiresAt);
    }

    public void Dispose() => _http.Dispose();
}

public sealed class PatchService
{
    private readonly HttpClient _http = new() { Timeout = TimeSpan.FromMinutes(5) };
    private readonly string _gameDirectory;

    public PatchService(string gameDirectory) => _gameDirectory = Path.GetFullPath(gameDirectory);

    public async Task VerifyAndRepairAsync(IProgress<(double Percent, string Status)> progress,
                                           CancellationToken cancellationToken)
    {
        var envelopeJson = await _http.GetStringAsync(LauncherConfiguration.ManifestUri, cancellationToken);
        var envelope = JsonSerializer.Deserialize<SignedManifest>(envelopeJson)
                       ?? throw new InvalidOperationException("Invalid patch manifest envelope.");
        var payload = Convert.FromBase64String(envelope.Payload);
        var signature = Convert.FromBase64String(envelope.Signature);
        VerifySignature(payload, signature);

        var manifest = JsonSerializer.Deserialize<PatchManifest>(payload)
                       ?? throw new InvalidOperationException("Invalid patch manifest.");
        var total = Math.Max(1, manifest.Files.Count);
        for (var index = 0; index < manifest.Files.Count; index++)
        {
            var file = manifest.Files[index];
            var destination = ResolveSafePath(file.Path);
            progress.Report((index * 100d / total, $"Checking {file.Path}"));

            if (File.Exists(destination) && await HashMatchesAsync(destination, file.Sha256, cancellationToken))
                continue;

            var temporary = destination + ".everleaf-new";
            Directory.CreateDirectory(Path.GetDirectoryName(destination)!);
            using (var response = await _http.GetAsync(file.Url, HttpCompletionOption.ResponseHeadersRead, cancellationToken))
            {
                response.EnsureSuccessStatusCode();
                await using var source = await response.Content.ReadAsStreamAsync(cancellationToken);
                await using var target = new FileStream(temporary, FileMode.Create, FileAccess.Write, FileShare.None);
                await source.CopyToAsync(target, cancellationToken);
            }

            if (!await HashMatchesAsync(temporary, file.Sha256, cancellationToken))
            {
                File.Delete(temporary);
                throw new InvalidOperationException($"Downloaded file failed verification: {file.Path}");
            }

            File.Move(temporary, destination, true);
        }

        progress.Report((100, $"Client ready — {manifest.Version}"));
    }

    private string ResolveSafePath(string relativePath)
    {
        if (Path.IsPathRooted(relativePath))
            throw new InvalidOperationException("Manifest contains an absolute path.");

        var resolved = Path.GetFullPath(Path.Combine(_gameDirectory, relativePath));
        var root = _gameDirectory.TrimEnd(Path.DirectorySeparatorChar) + Path.DirectorySeparatorChar;
        if (!resolved.StartsWith(root, StringComparison.OrdinalIgnoreCase))
            throw new InvalidOperationException("Manifest path escapes the game directory.");
        return resolved;
    }

    private static async Task<bool> HashMatchesAsync(string path, string expected, CancellationToken cancellationToken)
    {
        await using var stream = new FileStream(path, FileMode.Open, FileAccess.Read, FileShare.Read);
        var hash = await SHA256.HashDataAsync(stream, cancellationToken);
        return CryptographicOperations.FixedTimeEquals(
            hash, Convert.FromHexString(expected));
    }

    private static void VerifySignature(byte[] payload, byte[] signature)
    {
        try
        {
            using var rsa = RSA.Create();
            rsa.ImportFromPem(LauncherConfiguration.ManifestPublicKeyPem);
            if (!rsa.VerifyData(payload, signature, HashAlgorithmName.SHA256, RSASignaturePadding.Pss))
                throw new CryptographicException("Manifest signature is invalid.");
        }
        catch (Exception ex) when (ex is ArgumentException or CryptographicException)
        {
            throw new InvalidOperationException("Patch manifest could not be authenticated.", ex);
        }
    }
}

public static class GameLauncher
{
    public static void Start(string gameDirectory, LauncherSession session)
    {
        var executable = Path.Combine(gameDirectory, LauncherConfiguration.GameExecutable);
        if (!File.Exists(executable))
            throw new FileNotFoundException("MapleStory.exe was not found beside the launcher.", executable);

        var start = new ProcessStartInfo
        {
            FileName = executable,
            WorkingDirectory = gameDirectory,
            UseShellExecute = false
        };
        start.Environment["EVERLEAF_LAUNCH_USERNAME"] = session.Username;
        start.Environment["EVERLEAF_LAUNCH_TOKEN"] = session.AccessToken;
        using var process = Process.Start(start) ?? throw new InvalidOperationException("Unable to start the game.");
    }
}

public static class UserPreferences
{
    private static readonly string SettingsDirectory =
        Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "EverLeaf");
    private static readonly string SettingsPath = Path.Combine(SettingsDirectory, "launcher.json");

    public static string LoadRememberedUsername()
    {
        try
        {
            if (!File.Exists(SettingsPath)) return string.Empty;
            using var document = JsonDocument.Parse(File.ReadAllText(SettingsPath));
            return document.RootElement.TryGetProperty("rememberedUsername", out var value)
                ? value.GetString() ?? string.Empty
                : string.Empty;
        }
        catch
        {
            return string.Empty;
        }
    }

    public static void SaveRememberedUsername(string username)
    {
        Directory.CreateDirectory(SettingsDirectory);
        var temporary = SettingsPath + ".new";
        File.WriteAllText(temporary, JsonSerializer.Serialize(new { rememberedUsername = username }));
        File.Move(temporary, SettingsPath, true);
    }
}
