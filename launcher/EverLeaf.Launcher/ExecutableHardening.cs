using System.Buffers.Binary;
using System.Security.Cryptography;

namespace EverLeaf.Launcher;

internal static class ExecutableHardening
{
    private const int DosPePointerOffset = 0x3C;
    private const int PeSignatureSize = 4;
    private const int CoffMachineOffset = 0;
    private const int CoffCharacteristicsOffset = 18;
    private const ushort ImageFileMachineI386 = 0x014C;
    private const ushort ImageFileLargeAddressAware = 0x0020;
    private const int MaxNormalizedExecutableBytes = 64 * 1024 * 1024;

    internal static void EnsureLargeAddressAware(string executable)
    {
        using var stream = new FileStream(executable, FileMode.Open, FileAccess.ReadWrite, FileShare.None);
        if (stream.Length <= 0 || stream.Length > MaxNormalizedExecutableBytes)
            throw new InvalidDataException("EverLeaf.exe has an unexpected size and cannot be PE-hardened safely.");

        var bytes = new byte[checked((int)stream.Length)];
        ReadExactly(stream, bytes);
        if (!TryGetCharacteristicsOffset(bytes, out var characteristicsOffset))
            throw new InvalidDataException("EverLeaf.exe is not the expected Win32 PE executable.");

        var characteristics = BinaryPrimitives.ReadUInt16LittleEndian(bytes.AsSpan(characteristicsOffset, 2));
        if ((characteristics & ImageFileLargeAddressAware) != 0)
            return;

        characteristics |= ImageFileLargeAddressAware;
        stream.Position = characteristicsOffset;
        Span<byte> updated = stackalloc byte[2];
        BinaryPrimitives.WriteUInt16LittleEndian(updated, characteristics);
        stream.Write(updated);
        stream.Flush(flushToDisk: true);
    }

    internal static bool IsLargeAddressAware(string executable)
    {
        try
        {
            var bytes = File.ReadAllBytes(executable);
            if (!TryGetCharacteristicsOffset(bytes, out var characteristicsOffset))
                return false;
            var characteristics = BinaryPrimitives.ReadUInt16LittleEndian(bytes.AsSpan(characteristicsOffset, 2));
            return (characteristics & ImageFileLargeAddressAware) != 0;
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

    internal static async Task<bool> HashMatchesCanonicalOrLargeAddressAwareAsync(
        string executable,
        string expectedSha256,
        CancellationToken cancellationToken)
    {
        if (await PatchService.HashMatchesAsync(executable, expectedSha256, cancellationToken))
            return true;

        try
        {
            var info = new FileInfo(executable);
            if (!info.Exists || info.Length <= 0 || info.Length > MaxNormalizedExecutableBytes)
                return false;

            var bytes = await File.ReadAllBytesAsync(executable, cancellationToken);
            if (!TryGetCharacteristicsOffset(bytes, out var characteristicsOffset))
                return false;

            var characteristics = BinaryPrimitives.ReadUInt16LittleEndian(bytes.AsSpan(characteristicsOffset, 2));
            if ((characteristics & ImageFileLargeAddressAware) == 0)
                return false;

            // The signed patch manifest describes the canonical server byte stream.
            // Normalize only the launcher-owned LAA bit before comparing. Any other
            // local difference remains in the hash and therefore forces repair.
            characteristics = (ushort)(characteristics & ~ImageFileLargeAddressAware);
            BinaryPrimitives.WriteUInt16LittleEndian(bytes.AsSpan(characteristicsOffset, 2), characteristics);

            byte[] expected;
            try
            {
                expected = Convert.FromHexString(expectedSha256);
            }
            catch (FormatException)
            {
                return false;
            }

            var normalizedHash = SHA256.HashData(bytes);
            return CryptographicOperations.FixedTimeEquals(normalizedHash, expected);
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

    private static bool TryGetCharacteristicsOffset(ReadOnlySpan<byte> bytes, out int characteristicsOffset)
    {
        characteristicsOffset = 0;
        if (bytes.Length < 0x40 || bytes[0] != (byte)'M' || bytes[1] != (byte)'Z')
            return false;

        var peOffset = BinaryPrimitives.ReadInt32LittleEndian(bytes.Slice(DosPePointerOffset, 4));
        if (peOffset < 0 || peOffset > bytes.Length - (PeSignatureSize + 20))
            return false;

        if (BinaryPrimitives.ReadUInt32LittleEndian(bytes.Slice(peOffset, PeSignatureSize)) != 0x00004550)
            return false;

        var coffOffset = peOffset + PeSignatureSize;
        var machine = BinaryPrimitives.ReadUInt16LittleEndian(bytes.Slice(coffOffset + CoffMachineOffset, 2));
        if (machine != ImageFileMachineI386)
            return false;

        characteristicsOffset = coffOffset + CoffCharacteristicsOffset;
        return characteristicsOffset >= 0 && characteristicsOffset <= bytes.Length - 2;
    }

    private static void ReadExactly(Stream stream, Span<byte> destination)
    {
        var total = 0;
        while (total < destination.Length)
        {
            var read = stream.Read(destination[total..]);
            if (read == 0)
                throw new EndOfStreamException("EverLeaf.exe ended while reading its PE headers.");
            total += read;
        }
    }
}
