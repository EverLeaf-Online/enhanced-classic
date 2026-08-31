using Xunit;

namespace EverLeaf.Launcher.Tests;

public sealed class LauncherFileSwapTests
{
    [Fact]
    public void ReplaceKeepsPreviousLauncherUntilStartupCleanup()
    {
        var directory = CreateTempDirectory();
        try
        {
            var source = Path.Combine(directory, "source.exe");
            var target = Path.Combine(directory, "EverLeafLauncher.exe");
            File.WriteAllText(source, "new-launcher");
            File.WriteAllText(target, "old-launcher");

            LauncherFileSwap.Replace(source, target);

            Assert.Equal("new-launcher", File.ReadAllText(target));
            Assert.Equal("old-launcher", File.ReadAllText(LauncherFileSwap.BackupPath(target)));

            LauncherFileSwap.DeleteBackup(target);
            Assert.False(File.Exists(LauncherFileSwap.BackupPath(target)));
        }
        finally
        {
            Directory.Delete(directory, true);
        }
    }

    [Fact]
    public void RestoreReturnsPreviousLauncherAfterFailedRestart()
    {
        var directory = CreateTempDirectory();
        try
        {
            var source = Path.Combine(directory, "source.exe");
            var target = Path.Combine(directory, "EverLeafLauncher.exe");
            File.WriteAllText(source, "new-launcher");
            File.WriteAllText(target, "old-launcher");

            LauncherFileSwap.Replace(source, target);
            LauncherFileSwap.Restore(target);

            Assert.Equal("old-launcher", File.ReadAllText(target));
            Assert.False(File.Exists(LauncherFileSwap.BackupPath(target)));
            Assert.False(File.Exists(target + LauncherFileSwap.StagedSuffix));
        }
        finally
        {
            Directory.Delete(directory, true);
        }
    }

    private static string CreateTempDirectory()
    {
        var directory = Path.Combine(Path.GetTempPath(), "everleaf-launcher-swap-" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(directory);
        return directory;
    }
}
