using System.IO;

namespace EverLeaf.Launcher;

internal static class LauncherFileSwap
{
    internal const string BackupSuffix = ".everleaf-old";
    internal const string StagedSuffix = ".everleaf-new";

    internal static string BackupPath(string targetExecutable) =>
        Path.GetFullPath(targetExecutable) + BackupSuffix;

    internal static void Replace(string sourceExecutable, string targetExecutable)
    {
        var source = Path.GetFullPath(sourceExecutable);
        var target = Path.GetFullPath(targetExecutable);
        var staged = target + StagedSuffix;
        var backup = BackupPath(target);

        if (!File.Exists(source))
            throw new FileNotFoundException("The staged launcher update is missing.", source);

        TryDelete(staged);
        TryDelete(backup);
        File.Copy(source, staged, true);

        var hadPreviousLauncher = File.Exists(target);
        if (hadPreviousLauncher)
            File.Move(target, backup, true);

        try
        {
            File.Move(staged, target, true);
        }
        catch
        {
            TryDelete(staged);
            if (hadPreviousLauncher)
                Restore(target);
            throw;
        }
    }

    internal static void Restore(string targetExecutable)
    {
        var target = Path.GetFullPath(targetExecutable);
        var backup = BackupPath(target);
        if (!File.Exists(backup))
            return;

        TryDelete(target);
        File.Move(backup, target, true);
    }

    internal static void DeleteBackup(string? targetExecutable)
    {
        if (string.IsNullOrWhiteSpace(targetExecutable))
            return;
        TryDelete(BackupPath(targetExecutable));
    }

    private static void TryDelete(string path)
    {
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
