using System.IO;

namespace EverLeaf.Launcher;

internal static class BoundedDownload
{
    internal static async Task CopyExactAsync(
        Stream source,
        Stream destination,
        long expectedBytes,
        CancellationToken cancellationToken)
    {
        if (expectedBytes <= 0)
            throw new ArgumentOutOfRangeException(nameof(expectedBytes));

        var buffer = new byte[1024 * 1024];
        long copied = 0;
        while (copied < expectedBytes)
        {
            var remaining = expectedBytes - copied;
            var read = await source.ReadAsync(
                buffer.AsMemory(0, (int)Math.Min(buffer.Length, remaining)),
                cancellationToken);
            if (read == 0)
                throw new InvalidOperationException("Download ended before the signed size was reached.");

            await destination.WriteAsync(buffer.AsMemory(0, read), cancellationToken);
            copied += read;
        }

        // Probe one extra byte. Responses larger than the signed manifest are
        // rejected before untrusted bytes can be written beyond the trusted size.
        var extra = await source.ReadAsync(buffer.AsMemory(0, 1), cancellationToken);
        if (extra != 0)
            throw new InvalidOperationException("Download exceeds the signed size.");
    }
}
