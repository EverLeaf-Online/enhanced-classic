using System.Globalization;
using EverLeaf.Launcher;
using Xunit;

namespace EverLeaf.Launcher.Tests;

public sealed class LaunchTicketTests
{
    [Fact]
    public void CreateWritesFreshUnixTimestampAndDeleteRemovesTicket()
    {
        var directory = Path.Combine(Path.GetTempPath(), "everleaf-launch-ticket-" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(directory);
        try
        {
            var before = DateTimeOffset.UtcNow.ToUnixTimeSeconds();
            var path = LaunchTicket.Create(directory);
            var after = DateTimeOffset.UtcNow.ToUnixTimeSeconds();

            Assert.Equal(Path.Combine(Path.GetFullPath(directory), LaunchTicket.FileName), path);
            Assert.True(File.Exists(path));
            Assert.True(long.TryParse(File.ReadAllText(path), NumberStyles.Integer, CultureInfo.InvariantCulture, out var issuedAt));
            Assert.InRange(issuedAt, before, after);

            LaunchTicket.Delete(path);
            Assert.False(File.Exists(path));
        }
        finally
        {
            LaunchTicket.Delete(Path.Combine(directory, LaunchTicket.FileName));
            Directory.Delete(directory, true);
        }
    }
}
