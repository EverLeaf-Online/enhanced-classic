using EverLeaf.Launcher;
using Xunit;

namespace EverLeaf.Launcher.Tests;

public sealed class PatchRecoveryTests
{
    [Fact]
    public void InterruptedDownloadStagingFileIsRemovedBeforeRetry()
    {
        var directory = Path.Combine(Path.GetTempPath(), "everleaf-interrupted-" + Guid.NewGuid());
        Directory.CreateDirectory(directory);
        try
        {
            var staged = Path.Combine(directory, "Map.wz.everleaf-new");
            File.WriteAllText(staged, "partial interrupted payload");
            File.SetAttributes(staged, FileAttributes.ReadOnly);

            PatchService.RemoveStaleDownload(staged);

            Assert.False(File.Exists(staged));
        }
        finally
        {
            if (Directory.Exists(directory)) Directory.Delete(directory, true);
        }
    }
}
