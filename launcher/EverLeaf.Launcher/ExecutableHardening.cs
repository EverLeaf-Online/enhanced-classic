using System.Buffers.Binary;

namespace EverLeaf.Launcher;

internal static class ExecutableHardening
{
    private const int DosPePointerOffset = 0x3C;
    private const int PeSignatureSize = 4;
    private const int CoffMachineOffset = 0;
    private const int CoffCharacteristicsOffset = 18;
    private const ushort ImageFileMachineI386 = 0x014C;
    private const ushort ImageFileLargeAddressAware = 0x0020;
    private const int MaxExecutableBytes = 64 * 1024 * 1024;

    // Before signed patch verification, put the launcher-owned PE flag back into
    // canonical form. Invalid/corrupt executables are deliberately left alone so
    // PatchService can detect their hash mismatch and repair them normally.
    internal static void NormalizeForSignedRepair(string executable)
    {
        if (!File.Exists(executable))
            return;

        try
        {
            SetLargeAddressAware(executable, enabled: false, requireValidPe: false);
        }
        catch (IOException)
        {
            // PatchService already owns the user-facing repair/in-use error path.
        }
        catch (UnauthorizedAccessException)
        {
            // PatchService already owns the user-facing repair/permission error path.
        }
    }

    // Called only after the signed repair has completed successfully. At this
    // point EverLeaf.exe must be the validated Win32 baseline, so fail closed if
    // its PE header cannot be hardened exactly as expected.
    internal static void EnsureLargeAddressAware(string executable)
    {
        if (!File.Exists(executable))
            throw new FileNotFoundException("EverLeaf.exe was not found after signed repair.", executable);

        if (!SetLargeAddressAware(executable, enabled: true, requireValidPe: true))
            throw new InvalidDataException("EverLeaf.exe is not the expected Win32 PE executable.");
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

    private static bool SetLargeAddressAware(string executable, bool enabled, bool requireValidPe)
    {
        using var stream = new FileStream(executable, FileMode.Open, FileAccess.ReadWrite, FileShare.None);
        if (stream.Length <= 0 || stream.Length > MaxExecutableBytes)
        {
            if (requireValidPe)
                throw new InvalidDataException("EverLeaf.exe has an unexpected size and cannot be PE-hardened safely.");
            return false;
        }

        var bytes = new byte[checked((int)stream.Length)];
        ReadExactly(stream, bytes);
        if (!TryGetCharacteristicsOffset(bytes, out var characteristicsOffset))
        {
            if (requireValidPe)
                throw new InvalidDataException("EverLeaf.exe is not the expected Win32 PE executable.");
            return false;
        }

        var characteristics = BinaryPrimitives.ReadUInt16LittleEndian(bytes.AsSpan(characteristicsOffset, 2));
        var updatedCharacteristics = enabled
            ? (ushort)(characteristics | ImageFileLargeAddressAware)
            : (ushort)(characteristics & ~ImageFileLargeAddressAware);

        if (updatedCharacteristics == characteristics)
            return true;

        stream.Position = characteristicsOffset;
        Span<byte> updated = stackalloc byte[2];
        BinaryPrimitives.WriteUInt16LittleEndian(updated, updatedCharacteristics);
        stream.Write(updated);
        stream.Flush(flushToDisk: true);
        return true;
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
