using EverLeaf.Launcher;
using Xunit;

namespace EverLeaf.Launcher.Tests;

public sealed class BoundedDownloadTests
{
    [Fact]
    public async Task CopiesExactlyTheSignedSize()
    {
        await using var source = new MemoryStream("everleaf"u8.ToArray());
        await using var destination = new MemoryStream();

        await BoundedDownload.CopyExactAsync(source, destination, 8, CancellationToken.None);

        Assert.Equal("everleaf"u8.ToArray(), destination.ToArray());
    }

    [Fact]
    public async Task RejectsTruncatedResponses()
    {
        await using var source = new MemoryStream("short"u8.ToArray());
        await using var destination = new MemoryStream();

        await Assert.ThrowsAsync<InvalidOperationException>(() =>
            BoundedDownload.CopyExactAsync(source, destination, 10, CancellationToken.None));
    }

    [Fact]
    public async Task RejectsOversizedResponsesWithoutWritingPastSignedSize()
    {
        await using var source = new MemoryStream("trusted-extra"u8.ToArray());
        await using var destination = new MemoryStream();

        await Assert.ThrowsAsync<InvalidOperationException>(() =>
            BoundedDownload.CopyExactAsync(source, destination, 7, CancellationToken.None));

        Assert.Equal("trusted"u8.ToArray(), destination.ToArray());
    }
}
