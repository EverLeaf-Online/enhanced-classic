using System.Diagnostics;
using System.IO;
using System.Net.Http;
using System.Net.Http.Json;
using System.Security.Cryptography;
using System.Text.Json;

namespace EverLeaf.Launcher;

public sealed record ServerStatus(bool Online, string Message, string Version);
public sealed record PatchEntry(string Path, string Url, string Sha256, long Size);
public sealed record LauncherRelease(string Version, string Url, string Sha256, long Size);
public sealed record PatchManifest(
    string Version,
    IReadOnlyList<PatchEntry> Files,
    LauncherRelease? Launcher = null);
public sealed record SignedManifest(string Payload, string Signature);

public sealed class InsufficientDiskSpaceException(string message) : IOException(message);

public static class LauncherConfiguration
{
    public static readonly Uri ApiBase = new("https://everleafms.online/");
    public static readonly Uri ManifestUri = new(ApiBase, "v1/launcher/manifest");
    public const string GameExecutable = "EverLeaf.exe";
    public const string LegacyGameExecutable = "MapleStory.exe";
    public const string LauncherExecutable = "EverLeafLauncher.exe";
    public static readonly IReadOnlySet<string> RequiredGameFiles = new HashSet<string>(StringComparer.OrdinalIgnoreCase)
    {
        "Base.wz", "Canvas.dll", "Character.wz", "config.ini", "dinput8.dll",
        "Effect.wz", "Etc.wz", "EverLeaf_UI.wz", "Gr2D_DX8.dll", "ijl15.dll",
        "Item.wz", "l3codeca.acm", "List.wz", "Map.wz", "EverLeaf.exe",
        "Mob.wz", "Morph.wz", "mss32.dll", "NameSpace.dll", "nmcogame.dll",
        "nmconew.dll", "Npc.wz", "PCOM.dll", "Quest.wz", "Reactor.wz",
        "ResMan.dll", "Shape2D.dll", "Skill.wz", "Sound.wz", "Sound_DX8.dll",
        "String.wz", "suipre.dll", "TamingMob.wz", "UI.wz", "WzFlashRenderer.dll",
        "ZLZ.dll"
    };

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
    internal static readonly JsonSerializerOptions SerializerOptions = new()
    {
        PropertyNameCaseInsensitive = true
    };

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
        var manifest = await GetVerifiedManifestAsync(cancellationToken);
        progress.Report((0, "Checking files and available disk space…"));
        var repairPlan = await BuildRepairPlanAsync(manifest, cancellationToken);
        EnsureInstallSpace(repairPlan.Sum(file => file.Size));

        long totalBytes = Math.Max(1, manifest.Files.Sum(file => Math.Max(1, file.Size)));
        long completedBytes = 0;
        var totalFiles = manifest.Files.Count;

        for (var index = 0; index < totalFiles; index++)
        {
            var file = manifest.Files[index];
            cancellationToken.ThrowIfCancellationRequested();
            var destination = ResolveSafePath(file.Path);
            var basePercent = completedBytes * 100d / totalBytes;
            progress.Report((basePercent, $"Checking {index + 1} of {totalFiles}: {file.Path}"));

            if (!repairPlan.Contains(file))
            {
                completedBytes += Math.Max(1, file.Size);
                continue;
            }

            await DownloadAndReplaceAsync(file, destination, index + 1, totalFiles, completedBytes, totalBytes, progress, cancellationToken);
            completedBytes += Math.Max(1, file.Size);
        }

        RemoveLegacyGameExecutable();
        progress.Report((100, $"EverLeaf is up to date — {manifest.Version}"));
    }

    internal async Task<PatchManifest> GetVerifiedManifestAsync(CancellationToken cancellationToken)
    {
        var envelopeJson = await _http.GetStringAsync(LauncherConfiguration.ManifestUri, cancellationToken);
        var envelope = JsonSerializer.Deserialize<SignedManifest>(envelopeJson, SerializerOptions)
                       ?? throw new InvalidOperationException("Invalid patch manifest envelope.");

        if (string.IsNullOrWhiteSpace(envelope.Payload) || string.IsNullOrWhiteSpace(envelope.Signature))
            throw new InvalidOperationException("Patch manifest envelope is incomplete.");

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

        VerifySignature(payload, signature, LauncherConfiguration.ManifestPublicKeyPem);
        var manifest = JsonSerializer.Deserialize<PatchManifest>(payload, SerializerOptions)
                       ?? throw new InvalidOperationException("Invalid patch manifest.");
        ValidateManifest(manifest);
        return manifest;
    }

    internal void RemoveLegacyGameExecutable()
    {
        var current = Path.Combine(_gameDirectory, LauncherConfiguration.GameExecutable);
        var legacy = Path.Combine(_gameDirectory, LauncherConfiguration.LegacyGameExecutable);
        if (File.Exists(current) && File.Exists(legacy))
        {
            MakeWritable(legacy);
            File.Delete(legacy);
        }
    }

    internal async Task<IReadOnlySet<PatchEntry>> BuildRepairPlanAsync(
        PatchManifest manifest,
        CancellationToken cancellationToken)
    {
        var repairPlan = new HashSet<PatchEntry>();
        foreach (var file in manifest.Files)
        {
            cancellationToken.ThrowIfCancellationRequested();
            var destination = ResolveSafePath(file.Path);
            if (!File.Exists(destination)
                || new FileInfo(destination).Length != file.Size
                || !await HashMatchesAsync(destination, file.Sha256, cancellationToken))
            {
                repairPlan.Add(file);
            }
        }
        return repairPlan;
    }

    internal async Task<long> CalculateRepairFileBytesAsync(
        PatchManifest manifest,
        CancellationToken cancellationToken)
    {
        var repairPlan = await BuildRepairPlanAsync(manifest, cancellationToken);
        return repairPlan.Aggregate(0L, (total, file) => checked(total + file.Size));
    }

    internal void EnsureInstallSpace(long repairBytes)
    {
        if (repairBytes == 0)
            return;

        var root = Path.GetPathRoot(_gameDirectory)
                   ?? throw new IOException("EverLeaf could not determine the game folder drive.");
        var reserveBytes = 512L * 1024 * 1024;
        var requiredBytes = checked(repairBytes + reserveBytes);
        var availableBytes = new DriveInfo(root).AvailableFreeSpace;
        if (availableBytes < requiredBytes)
        {
            throw new InsufficientDiskSpaceException(
                $"EverLeaf needs about {FormatBytes(requiredBytes)} free in this folder, but only {FormatBytes(availableBytes)} is available.");
        }
    }

    private async Task DownloadAndReplaceAsync(
        PatchEntry file,
        string destination,
        int fileNumber,
        int totalFiles,
        long completedBytes,
        long totalBytes,
        IProgress<(double Percent, string Status)> progress,
        CancellationToken cancellationToken)
    {
        var temporary = destination + ".everleaf-new";
        Directory.CreateDirectory(Path.GetDirectoryName(destination)!);
        RemoveStaleDownload(temporary);

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
                    progress.Report((percent, $"Repairing {fileNumber} of {totalFiles}: {file.Path} — {FormatBytes(downloaded)} / {FormatBytes(file.Size)}"));
                }
            }

            if (new FileInfo(temporary).Length != file.Size)
                throw new InvalidOperationException($"Downloaded file size is invalid: {file.Path}");
            if (!await HashMatchesAsync(temporary, file.Sha256, cancellationToken))
                throw new InvalidOperationException($"Downloaded file failed verification: {file.Path}");

            MakeWritable(destination);
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

    private static Uri ResolveDownloadUri(string value)
    {
        if (Uri.TryCreate(value, UriKind.Absolute, out _))
            throw new InvalidOperationException("Patch manifests cannot redirect downloads to an absolute URL.");
        if (string.IsNullOrWhiteSpace(value) || !value.StartsWith("/patches/", StringComparison.Ordinal)
            || value.Contains('\\') || value.Contains("..", StringComparison.Ordinal))
            throw new InvalidOperationException("Patch manifest contains an unsafe download URL.");
        var resolved = new Uri(LauncherConfiguration.ApiBase, value);
        if (!string.Equals(resolved.Scheme, Uri.UriSchemeHttps, StringComparison.OrdinalIgnoreCase)
            || !string.Equals(resolved.Host, LauncherConfiguration.ApiBase.Host, StringComparison.OrdinalIgnoreCase)
            || resolved.Port != LauncherConfiguration.ApiBase.Port)
            throw new InvalidOperationException("Patch download URL is outside the EverLeaf patch service.");
        return resolved;
    }

    internal void ValidateManifest(PatchManifest manifest)
    {
        if (string.IsNullOrWhiteSpace(manifest.Version))
            throw new InvalidOperationException("Patch manifest has no version.");
        if (manifest.Files is null || manifest.Files.Count == 0)
            throw new InvalidOperationException("Patch manifest has an empty file list.");

        var seen = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
        foreach (var file in manifest.Files)
        {
            if (string.IsNullOrWhiteSpace(file.Path) || string.IsNullOrWhiteSpace(file.Url))
                throw new InvalidOperationException("Patch manifest contains an incomplete file entry.");
            if (file.Size <= 0)
                throw new InvalidOperationException($"Patch manifest contains an invalid size: {file.Path}");
            if (file.Sha256?.Length != 64 || !file.Sha256.All(Uri.IsHexDigit))
                throw new InvalidOperationException($"Patch manifest contains an invalid SHA-256: {file.Path}");

            var resolved = ResolveSafePath(file.Path);
            ResolveDownloadUri(file.Url);
            if (!seen.Add(resolved))
                throw new InvalidOperationException($"Patch manifest contains a duplicate path: {file.Path}");
            if (string.Equals(Path.GetFileName(resolved), LauncherConfiguration.LauncherExecutable, StringComparison.OrdinalIgnoreCase))
                throw new InvalidOperationException("The game manifest cannot replace the running launcher executable.");
        }

        var actual = manifest.Files.Select(file => file.Path).ToHashSet(StringComparer.OrdinalIgnoreCase);
        if (!actual.SetEquals(LauncherConfiguration.RequiredGameFiles))
        {
            var missing = LauncherConfiguration.RequiredGameFiles.Except(actual, StringComparer.OrdinalIgnoreCase);
            var unexpected = actual.Except(LauncherConfiguration.RequiredGameFiles, StringComparer.OrdinalIgnoreCase);
            throw new InvalidOperationException(
                $"Patch manifest does not contain the complete EverLeaf client. Missing: [{string.Join(", ", missing)}]; unexpected: [{string.Join(", ", unexpected)}].");
        }

        if (manifest.Launcher is not null)
            ValidateLauncherRelease(manifest.Launcher);
    }

    internal static void ValidateLauncherRelease(LauncherRelease release)
    {
        if (string.IsNullOrWhiteSpace(release.Version) || release.Version.Length > 128)
            throw new InvalidOperationException("Launcher release has an invalid version.");
        if (release.Url != "/launcher/download")
            throw new InvalidOperationException("Launcher release URL is outside the EverLeaf launcher service.");
        if (release.Size <= 0 || release.Size > 512L * 1024 * 1024)
            throw new InvalidOperationException("Launcher release has an invalid size.");
        if (release.Sha256?.Length != 64 || !release.Sha256.All(Uri.IsHexDigit))
            throw new InvalidOperationException("Launcher release has an invalid SHA-256.");
    }

    private string ResolveSafePath(string relativePath)
    {
        if (Path.IsPathRooted(relativePath) || relativePath.Contains('\\'))
            throw new InvalidOperationException("Manifest contains an absolute path.");

        var parts = relativePath.Split('/');
        if (parts.Any(part => string.IsNullOrWhiteSpace(part) || part is "." or ".."))
            throw new InvalidOperationException("Manifest contains an unsafe path segment.");

        var resolved = Path.GetFullPath(Path.Combine(_gameDirectory, relativePath));
        var root = _gameDirectory + Path.DirectorySeparatorChar;
        if (!resolved.StartsWith(root, StringComparison.OrdinalIgnoreCase))
            throw new InvalidOperationException("Manifest path escapes the game directory.");
        return resolved;
    }

    internal static async Task<bool> HashMatchesAsync(string path, string expected, CancellationToken cancellationToken)
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

    internal static void VerifySignature(byte[] payload, byte[] signature, string publicKeyPem)
    {
        try
        {
            using var rsa = RSA.Create();
            rsa.ImportFromPem(publicKeyPem);
            if (!rsa.VerifyData(payload, signature, HashAlgorithmName.SHA256, RSASignaturePadding.Pss))
                throw new CryptographicException("Manifest signature is invalid.");
        }
        catch (Exception ex) when (ex is ArgumentException or CryptographicException)
        {
            throw new InvalidOperationException("Patch manifest could not be authenticated.", ex);
        }
    }

    private static void MakeWritable(string path)
    {
        if (!File.Exists(path)) return;
        var attributes = File.GetAttributes(path);
        if ((attributes & FileAttributes.ReadOnly) != 0)
            File.SetAttributes(path, attributes & ~FileAttributes.ReadOnly);
    }

    internal static void RemoveStaleDownload(string path)
    {
        if (!File.Exists(path)) return;
        MakeWritable(path);
        File.Delete(path);
    }

    private static void TryDelete(string path)
    {
        try
        {
            RemoveStaleDownload(path);
        }
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
                "EverLeaf.exe was not found. Run Install / Repair Files before launching.", executable);

        var start = CreateStartInfo(executable, gameDirectory);
        using var process = Process.Start(start) ?? throw new InvalidOperationException("Unable to start EverLeaf.exe.");
    }

    internal static ProcessStartInfo CreateStartInfo(string executable, string gameDirectory) => new()
    {
        FileName = executable,
        WorkingDirectory = gameDirectory,
        // The v83 game executable declares requireAdministrator in its embedded manifest.
        // Shell execution lets Windows display the trusted UAC consent prompt.
        UseShellExecute = true
    };
}
