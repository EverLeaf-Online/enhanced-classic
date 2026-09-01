using System.Globalization;
using System.IO;

namespace EverLeaf.Launcher;

internal static class LaunchTicket
{
    internal const string FileName = ".everleaf-launch";
    private const int DeleteAttempts = 5;
    private static readonly TimeSpan DeleteRetryDelay = TimeSpan.FromMilliseconds(100);

    internal static string GetPath(string gameDirectory)
    {
        var root = Path.GetFullPath(gameDirectory)
            .TrimEnd(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar);
        return Path.Combine(root, FileName);
    }

    internal static string Create(string gameDirectory)
    {
        var path = GetPath(gameDirectory);

        // A launch ticket is transient state, not an installed game file. A client
        // crash or an older client build may leave it behind, so every new launch
        // replaces any previous ticket rather than inheriting stale state.
        Delete(path, throwOnFailure: true);

        var issuedAt = DateTimeOffset.UtcNow.ToUnixTimeSeconds()
            .ToString(CultureInfo.InvariantCulture);

        File.WriteAllText(path, issuedAt);
        try
        {
            File.SetAttributes(path, File.GetAttributes(path) | FileAttributes.Hidden);
        }
        catch (IOException)
        {
            // The ticket remains valid even if Windows cannot mark it hidden.
        }
        catch (UnauthorizedAccessException)
        {
            // The ticket remains valid even if Windows cannot mark it hidden.
        }

        return path;
    }

    internal static void CleanupStale(string gameDirectory)
        => Delete(GetPath(gameDirectory), throwOnFailure: true);

    internal static void Delete(string? path)
        => Delete(path, throwOnFailure: false);

    private static void Delete(string? path, bool throwOnFailure)
    {
        if (string.IsNullOrWhiteSpace(path))
            return;

        Exception? lastError = null;
        for (var attempt = 0; attempt < DeleteAttempts; attempt++)
        {
            try
            {
                if (!File.Exists(path))
                    return;

                // Hidden is intentional, but ReadOnly/System can be inherited or
                // introduced by extraction/security software. Normalize attributes
                // before deleting so a stale ticket can never make a folder unusable.
                File.SetAttributes(path, FileAttributes.Normal);
                File.Delete(path);
                return;
            }
            catch (FileNotFoundException)
            {
                return;
            }
            catch (DirectoryNotFoundException)
            {
                return;
            }
            catch (IOException ex)
            {
                lastError = ex;
            }
            catch (UnauthorizedAccessException ex)
            {
                lastError = ex;
            }

            if (attempt + 1 < DeleteAttempts)
                Thread.Sleep(DeleteRetryDelay);
        }

        if (throwOnFailure && lastError is not null)
            throw new IOException("EverLeaf could not clear a stale launch ticket. Close EverLeaf.exe and try again.", lastError);
    }
}
