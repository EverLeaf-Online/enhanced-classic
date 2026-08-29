using System.Diagnostics;
using System.IO;
using System.IO.Compression;
using System.Net.Http;
using System.Reflection;
using System.Security.Cryptography;

namespace EverLeaf.Launcher;

public sealed class LauncherUpdateService : IDisposable
{
    private readonly HttpClient _http = new() { Timeout = TimeSpan.FromMinutes(5) };
    private readonly string _gameDirectory;

    public LauncherUpdateService(string gameDirectory) => _gameDirectory = Path.GetFullPath(gameDirectory);

    public async Task<bool> TryBeginUpdateAsync(CancellationToken cancellationToken)
    {
        using var patcher = new PatchService(_gameDirectory);
        var manifest = await patcher.GetVerifiedManifestAsync(cancellationToken);
        var release = manifest.Launcher;
        if (release is null || !NeedsUpdate(CurrentVersion(), release.Version))
            return false;

        PatchService.ValidateLauncherRelease(release);
        var updateDirectory = Path.Combine(Path.GetTempPath(), "EverLeafLauncher-update-" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(updateDirectory);
        var archivePath = Path.Combine(updateDirectory, "launcher.zip");
        var executablePath = Path.Combine(updateDirectory, LauncherConfiguration.LauncherExecutable);

        try
        {
            await DownloadVerifiedArchiveAsync(release, archivePath, cancellationToken);
            await ExtractLauncherAsync(archivePath, executablePath, cancellationToken);
            var currentExecutable = Environment.ProcessPath
                                    ?? throw new InvalidOperationException("EverLeaf could not locate the running launcher.");
            using var process = Process.Start(LauncherUpdateApplier.CreateApplyStartInfo(
                executablePath, currentExecutable, Environment.ProcessId, updateDirectory));
            if (process is null)
                throw new InvalidOperationException("EverLeaf could not start the launcher updater.");
            return true;
        }
        catch
        {
            TryDeleteDirectory(updateDirectory);
            throw;
        }
    }

    internal static string CurrentVersion() =>
        Assembly.GetEntryAssembly()?.GetCustomAttribute<AssemblyInformationalVersionAttribute>()?.InformationalVersion
        ?? "unknown";

    internal static bool NeedsUpdate(string currentVersion, string publishedVersion) =>
        !string.Equals(currentVersion, publishedVersion, StringComparison.Ordinal);

    private async Task DownloadVerifiedArchiveAsync(
        LauncherRelease release,
        string destination,
        CancellationToken cancellationToken)
    {
        var uri = new Uri(LauncherConfiguration.ApiBase, release.Url);
        if (uri.Scheme != Uri.UriSchemeHttps
            || !string.Equals(uri.Host, LauncherConfiguration.ApiBase.Host, StringComparison.OrdinalIgnoreCase)
            || uri.Port != LauncherConfiguration.ApiBase.Port)
            throw new InvalidOperationException("Launcher update URL is outside the EverLeaf service.");

        using var response = await _http.GetAsync(uri, HttpCompletionOption.ResponseHeadersRead, cancellationToken);
        response.EnsureSuccessStatusCode();
        if (response.Content.Headers.ContentLength is long remoteSize && remoteSize != release.Size)
            throw new InvalidOperationException("Launcher update size does not match the signed manifest.");

        await using (var source = await response.Content.ReadAsStreamAsync(cancellationToken))
        await using (var target = new FileStream(destination, FileMode.CreateNew, FileAccess.Write, FileShare.None,
                         1024 * 1024, FileOptions.Asynchronous | FileOptions.SequentialScan))
            await source.CopyToAsync(target, cancellationToken);

        if (new FileInfo(destination).Length != release.Size
            || !await PatchService.HashMatchesAsync(destination, release.Sha256, cancellationToken))
            throw new CryptographicException("Launcher update failed signed SHA-256 verification.");
    }

    internal static async Task ExtractLauncherAsync(
        string archivePath,
        string destination,
        CancellationToken cancellationToken)
    {
        using var archive = ZipFile.OpenRead(archivePath);
        var files = archive.Entries.Where(entry => !string.IsNullOrEmpty(entry.Name)).ToArray();
        if (files.Length != 1
            || files[0].FullName != LauncherConfiguration.LauncherExecutable
            || files[0].Length <= 0
            || files[0].Length > 512L * 1024 * 1024)
            throw new InvalidOperationException("Launcher update archive has an invalid layout.");

        await using var source = files[0].Open();
        await using var target = new FileStream(destination, FileMode.CreateNew, FileAccess.Write, FileShare.None,
            1024 * 1024, FileOptions.Asynchronous | FileOptions.SequentialScan);
        await source.CopyToAsync(target, cancellationToken);
    }

    private static void TryDeleteDirectory(string path)
    {
        try { if (Directory.Exists(path)) Directory.Delete(path, true); }
        catch { }
    }

    public void Dispose() => _http.Dispose();
}

public static class LauncherUpdateApplier
{
    private const string ApplyArgument = "--apply-launcher-update";
    private const string CleanupArgument = "--cleanup-launcher-update";

    internal static ProcessStartInfo CreateApplyStartInfo(
        string updaterExecutable,
        string targetExecutable,
        int oldProcessId,
        string updateDirectory)
    {
        var start = new ProcessStartInfo
        {
            FileName = updaterExecutable,
            WorkingDirectory = Path.GetDirectoryName(updaterExecutable)!,
            UseShellExecute = true
        };
        start.ArgumentList.Add(ApplyArgument);
        start.ArgumentList.Add(targetExecutable);
        start.ArgumentList.Add(oldProcessId.ToString());
        start.ArgumentList.Add(updateDirectory);
        return start;
    }

    public static bool TryApply(string[] args)
    {
        if (args.Length == 0 || args[0] != ApplyArgument)
            return false;
        if (args.Length != 4 || !int.TryParse(args[2], out var oldProcessId))
            throw new InvalidOperationException("Launcher update arguments are invalid.");

        var source = Path.GetFullPath(Environment.ProcessPath
                                      ?? throw new InvalidOperationException("Updater executable path is unavailable."));
        var target = Path.GetFullPath(args[1]);
        var updateDirectory = Path.GetFullPath(args[3]);
        ValidateApplyPaths(source, target, updateDirectory);

        try
        {
            using var oldProcess = Process.GetProcessById(oldProcessId);
            if (!oldProcess.WaitForExit(60_000))
                throw new TimeoutException("The previous launcher did not close in time.");
        }
        catch (ArgumentException)
        {
            // The previous process already exited.
        }

        var staged = target + ".everleaf-new";
        File.Copy(source, staged, true);
        File.Move(staged, target, true);

        var restart = new ProcessStartInfo { FileName = target, WorkingDirectory = Path.GetDirectoryName(target)!, UseShellExecute = true };
        restart.ArgumentList.Add(CleanupArgument);
        restart.ArgumentList.Add(updateDirectory);
        restart.ArgumentList.Add(Environment.ProcessId.ToString());
        Process.Start(restart)?.Dispose();
        return true;
    }

    internal static void ValidateApplyPaths(string source, string target, string updateDirectory)
    {
        var expectedUpdateRoot = Path.GetFullPath(Path.GetTempPath())
            .TrimEnd(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar);
        var updateParent = Path.GetDirectoryName(updateDirectory.TrimEnd(
            Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar));
        if (!string.Equals(Path.GetFileName(source), LauncherConfiguration.LauncherExecutable, StringComparison.OrdinalIgnoreCase)
            || !string.Equals(Path.GetFileName(target), LauncherConfiguration.LauncherExecutable, StringComparison.OrdinalIgnoreCase)
            || !source.StartsWith(updateDirectory + Path.DirectorySeparatorChar, StringComparison.OrdinalIgnoreCase)
            || !string.Equals(updateParent, expectedUpdateRoot, StringComparison.OrdinalIgnoreCase)
            || target.StartsWith(updateDirectory + Path.DirectorySeparatorChar, StringComparison.OrdinalIgnoreCase)
            || !Path.GetFileName(updateDirectory).StartsWith("EverLeafLauncher-update-", StringComparison.Ordinal))
            throw new InvalidOperationException("Launcher update paths are invalid.");
    }

    public static void ScheduleCleanup(string[] args)
    {
        if (args.Length != 3 || args[0] != CleanupArgument || !int.TryParse(args[2], out var helperProcessId))
            return;

        var directory = Path.GetFullPath(args[1]);
        var tempRoot = Path.GetFullPath(Path.GetTempPath())
            .TrimEnd(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar);
        if (!string.Equals(Path.GetDirectoryName(directory.TrimEnd(
                Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar)), tempRoot, StringComparison.OrdinalIgnoreCase)
            || !Path.GetFileName(directory).StartsWith("EverLeafLauncher-update-", StringComparison.Ordinal))
            return;

        _ = Task.Run(() =>
        {
            try
            {
                using var helper = Process.GetProcessById(helperProcessId);
                helper.WaitForExit(60_000);
            }
            catch (ArgumentException) { }
            try { if (Directory.Exists(directory)) Directory.Delete(directory, true); }
            catch { }
        });
    }
}
