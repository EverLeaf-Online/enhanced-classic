using System.Globalization;
using System.IO;

namespace EverLeaf.Launcher;

internal static class LaunchTicket
{
    internal const string FileName = ".everleaf-launch";

    internal static string Create(string gameDirectory)
    {
        var root = Path.GetFullPath(gameDirectory)
            .TrimEnd(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar);
        var path = Path.Combine(root, FileName);
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

    internal static void Delete(string? path)
    {
        if (string.IsNullOrWhiteSpace(path))
            return;

        try
        {
            if (File.Exists(path))
                File.Delete(path);
        }
        catch (IOException)
        {
        }
        catch (UnauthorizedAccessException)
        {
        }
    }
}
