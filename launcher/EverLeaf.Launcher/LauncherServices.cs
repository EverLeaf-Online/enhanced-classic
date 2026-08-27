using System.Diagnostics;
using System.IO;
using System.Net.Http;
using System.Net.Http.Json;
using System.Security.Cryptography;
using System.Text.Json;

namespace EverLeaf.Launcher;

public sealed record ServerStatus(bool Online, string Message, string Version);
public sealed record PatchEntry(string Path, string Url, string Sha256, long Size);
public sealed record PatchManifest(string Version, IReadOnlyList<PatchEntry> Files);
public sealed record SignedManifest(string Payload, string Signature);

public static class LauncherConfiguration
{
    public static readonly Uri ApiBase = new("https://132-145-141-79.sslip.io/");
    public static readonly Uri ManifestUri = new(ApiBase, "v1/launcher/manifest");
    public const string GameExecutable = "MapleStory.exe";
    public const string LauncherExecutable = "EverLeafLauncher.exe";

    // Public half of EverLeaf's launcher-manifest signing key. The corresponding
    // private key belongs only on the production patch server and is never shipped
    // to players or committed to this repository.
    public const string ManifestPublicKeyPem = """
-----BEGIN PUBLIC KEY-----
MIIBojANBgkqhkiG9w0BAQEFAAOCAY8AMIIBigKCAYEAykfGK6UUcyVsoDohTTAd
i7ncN1SN1ToBKFckN5NZ5iJIhaaLdlIgW4+vP+UmMkaJh3VI0BD3M+jaz2MGYB27
lySLibm0ChW3764xxl0NIlMUpOfSHUa0PhlEWX8fMhFJk8tnz3T3IEErytCY9eNb
1wPZmbQh3fRGHRZ/qZfCf8K7v05IJifu7vXGTxl+c1R1x+U1n4uZoL5GanqLnZ2i
z0Gx0o9P3leJ4OX7RmU8Gn8dsBGQhswm9VEg1vNLCBHRAfaFUP2DGKwC17uJ1Ted
Muf5VkhJrNOCwOKV7rm19NUmuHjb76H7R/C7h8X0i3kRy3Huc8xCV2oxhA0RqJbS
s23RKssZKn0mhRVORAO0HydfGWtgPheTO1GYCbfW9MRm+qxnVMQkr/Axh8Ot34RY
hOebJ4rwJ9o/zGXc6ONSxwKwNW/o4jGqNmaDBDfHIqSc8bI+R0lOgw9qecLY+FuD
tgfoiGul1un/65fJs5aRwaEvGTtxp4K+yXD/DTxGVC8bAgMBAAE=
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

    public void Dispose() => _http.Dispose();
}

public sealed class PatchService : IDisposable
{
    private readonly HttpClient _http = new() { Timeout = TimeSpan.FromMinutes(20) };
    private readonly string _gameDirectory;

    public PatchService(string gameDirectory)
    {
        _gameDirectory = Path.GetFullPath(gameDirectory)
            .TrimEnd(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar);
    }

    public async Task VerifyAndRepairAsync(
        IProgress<(double Percent, string Status)> progress,
        CancellationToken cancellationToken)
    {
        progress.Report((0, "Getting EverLeaf update manifest…"));
        var envelopeJson = await _http.GetStringAsync(LauncherConfiguration.ManifestUri, cancellationToken);
        var envelope = JsonSerializer.Deserialize<SignedManifest>(envelopeJson)
                       ?? throw new InvalidOperationException("Invalid patch manifest envelope.");

        byte[] payload;
        byte[] signature;
        try
        {
            payload = Convert.FromBase64String(envelope.Payload);
            signature = Convert.FromBase64String(envelope.Signature);
        }
        catch (FormatException ex)
        {
            throw new InvalidOperationException("Patch manifest encoding is invalid.", ex);
        }

        VerifySignature(payload, signature);
        var manifest = JsonSerializer.Deserialize<PatchManifest>(payload)
                       ?? throw new InvalidOperationException("Invalid patch manifest.");
        ValidateManifest(manifest);

        long totalBytes = Math.Max(1, manifest.Files.Sum(file => Math.Max(1, file.Size)));
        long completedBytes = 0;

        foreach (var file in manifest.Files)
        {
            cancellationToken.ThrowIfCancellationRequested();
            var destination = ResolveSafePath(file.Path);
            var basePercent = completedBytes * 100d / totalBytes;
            progress.Report((basePercent, $"Checking {file.Path}"));

            if (File.Exists(destination)
                && new FileInfo(destination).Length == file.Size
                && await HashMatchesAsync(destination, file.Sha256, cancellationToken))
            {
                completedBytes += Math.Max(1, file.Size);
                continue;
            }

            await DownloadAndReplaceAsync(file, destination, completedBytes, totalBytes, progress, cancellationToken);
            completedBytes += Math.Max(1, file.Size);
        }

        progress.Report((100, $"EverLeaf is up to date — {manifest.Version}"));
    }

    private async Task DownloadAndReplaceAsync(
        PatchEntry file,
        string destination,
        long completedBytes,
        long totalBytes,
        IProgress<(double Percent, string Status)> progress,
        CancellationToken cancellationToken)
    {
        var temporary = destination + ".everleaf-new";
        Directory.CreateDirectory(Path.GetDirectoryName(destination)!);
        TryDelete(temporary);

        try
        {
            var uri = ResolveDownloadUri(file.Url);
            using var response = await _http.GetAsync(uri, HttpCompletionOption.ResponseHeadersRead, cancellationToken);
            response.EnsureSuccessStatusCode();

            if (response.Content.Headers.ContentLength is long remoteSize && remoteSize != file.Size)
                throw new InvalidOperationException($"Server size mismatch for {file.Path}.");

            await using var source = await response.Content.ReadAsStreamAsync(cancellationToken);
            await using (var target = new FileStream(
                             temporary, FileMode.CreateNew, FileAccess.Write, FileShare.None,
                             1024 * 1024, FileOptions.Asynchronous | FileOptions.SequentialScan))
            {
                var buffer = new byte[1024 * 1024];
                long downloaded = 0;
                while (true)
                {
                    var read = await source.ReadAsync(buffer, cancellationToken);
                    if (read == 0) break;
                    await target.WriteAsync(buffer.AsMemory(0, read), cancellationToken);
                    downloaded += read;
                    var percent = Math.Min(99.5, (completedBytes + downloaded) * 100d / totalBytes);
                    progress.Report((percent, $"Updating {file.Path} — {FormatBytes(downloaded)} / {FormatBytes(file.Size)}"));
                }
            }

            if (new FileInfo(temporary).Length != file.Size)
                throw new InvalidOperationException($"Downloaded file size is invalid: {file.Path}");
            if (!await HashMatchesAsync(temporary, file.Sha256, cancellationToken))
                throw new InvalidOperationException($"Downloaded file failed verification: {file.Path}");

            File.Move(temporary, destination, true);
        }
        finally
        {
            TryDelete(temporary);
        }
    }

    private static string FormatBytes(long bytes)
    {
        if (bytes >= 1024L * 1024L * 1024L) return $"{bytes / (1024d * 1024d * 1024d):0.00} GB";
        if (bytes >= 1024L * 1024L) return $"{bytes / (1024d * 1024d):0.0} MB";
        if (bytes >= 1024L) return $"{bytes / 1024d:0.0} KB";
        return $"{bytes} B";
    }

    private Uri ResolveDownloadUri(string value)
    {
        if (Uri.TryCreate(value, UriKind.Absolute, out var absolute))
        {
            if (!string.Equals(absolute.Scheme, Uri.UriSchemeHttps, StringComparison.OrdinalIgnoreCase))
                throw new InvalidOperationException("Patch downloads must use HTTPS.");
            return absolute;
        }

        return new Uri(LauncherConfiguration.ApiBase, value.TrimStart('/'));
    }

    private void ValidateManifest(PatchManifest manifest)
    {
        if (string.IsNullOrWhiteSpace(manifest.Version))
            throw new InvalidOperationException("Patch manifest has no version.");
        if (manifest.Files is null)
            throw new InvalidOperationException("Patch manifest has no file list.");

        var seen = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
        foreach (var file in manifest.Files)
        {
            if (string.IsNullOrWhiteSpace(file.Path) || string.IsNullOrWhiteSpace(file.Url))
                throw new InvalidOperationException("Patch manifest contains an incomplete file entry.");
            if (file.Size < 0)
                throw new InvalidOperationException($"Patch manifest contains an invalid size: {file.Path}");
            if (file.Sha256?.Length != 64 || !file.Sha256.All(Uri.IsHexDigit))
                throw new InvalidOperationException($"Patch manifest contains an invalid SHA-256: {file.Path}");

            var resolved = ResolveSafePath(file.Path);
            if (!seen.Add(resolved))
                throw new InvalidOperationException($"Patch manifest contains a duplicate path: {file.Path}");
            if (string.Equals(Path.GetFileName(resolved), LauncherConfiguration.LauncherExecutable, StringComparison.OrdinalIgnoreCase))
                throw new InvalidOperationException("The game manifest cannot replace the running launcher executable.");
        }
    }

    private string ResolveSafePath(string relativePath)
    {
        if (Path.IsPathRooted(relativePath))
            throw new InvalidOperationException("Manifest contains an absolute path.");

        var resolved = Path.GetFullPath(Path.Combine(_gameDirectory, relativePath));
        var root = _gameDirectory + Path.DirectorySeparatorChar;
        if (!resolved.StartsWith(root, StringComparison.OrdinalIgnoreCase))
            throw new InvalidOperationException("Manifest path escapes the game directory.");
        return resolved;
    }

    private static async Task<bool> HashMatchesAsync(string path, string expected, CancellationToken cancellationToken)
    {
        try
        {
            await using var stream = new FileStream(
                path, FileMode.Open, FileAccess.Read, FileShare.Read,
                1024 * 1024, FileOptions.Asynchronous | FileOptions.SequentialScan);
            var hash = await SHA256.HashDataAsync(stream, cancellationToken);
            return CryptographicOperations.FixedTimeEquals(hash, Convert.FromHexString(expected));
        }
        catch (IOException)
        {
            return false;
        }
        catch (UnauthorizedAccessException)
        {
            return false;
        }
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

    private static void TryDelete(string path)
    {
        try { if (File.Exists(path)) File.Delete(path); }
        catch { }
    }

    public void Dispose() => _http.Dispose();
}

public static class GameLauncher
{
    public static void Start(string gameDirectory)
    {
        var executable = Path.Combine(gameDirectory, LauncherConfiguration.GameExecutable);
        if (!File.Exists(executable))
            throw new FileNotFoundException(
                "MapleStory.exe was not found. Place the EverLeaf launcher in your supported v83 game folder.", executable);

        var start = new ProcessStartInfo
        {
            FileName = executable,
            WorkingDirectory = gameDirectory,
            UseShellExecute = false
        };
        using var process = Process.Start(start) ?? throw new InvalidOperationException("Unable to start MapleStory.exe.");
    }
}
