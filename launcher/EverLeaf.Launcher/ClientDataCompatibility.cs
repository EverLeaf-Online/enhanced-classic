using System.Security.Cryptography;

namespace EverLeaf.Launcher;

public static class ClientDataCompatibility
{
    // EverLeaf's server-side WZ XML is pinned to the same Map/Npc data set as
    // the Cosmic v83 client. These hashes are file identities only; the launcher
    // does not redistribute the proprietary game assets.
    private sealed record RequiredFile(string Name, long Size, string Sha256);

    private static readonly RequiredFile[] RequiredFiles =
    [
        new(
            "Map.wz",
            638428788,
            "a39da5ac66cb3cb1803b1a8f70f19cdf67ca191016e16c853f521b3c8156aca4"),
        new(
            "Npc.wz",
            53498512,
            "2992910ac5f65fa3d1ca4b2469fa4105f948f6ceb4a6c47ee6953be9d04dee17")
    ];

    public static async Task VerifyAsync(
        string gameDirectory,
        IProgress<(double Percent, string Status)>? progress,
        CancellationToken cancellationToken)
    {
        for (var index = 0; index < RequiredFiles.Length; index++)
        {
            cancellationToken.ThrowIfCancellationRequested();
            var required = RequiredFiles[index];
            var path = Path.Combine(gameDirectory, required.Name);
            progress?.Report((index * 5d, $"Checking compatible {required.Name}…"));

            if (!File.Exists(path))
                throw BuildCompatibilityError(required.Name, "is missing");

            var info = new FileInfo(path);
            if (info.Length != required.Size)
                throw BuildCompatibilityError(required.Name, "is from a different v83 data set");

            await using var stream = new FileStream(
                path, FileMode.Open, FileAccess.Read, FileShare.Read,
                bufferSize: 1024 * 1024,
                options: FileOptions.Asynchronous | FileOptions.SequentialScan);
            var hash = await SHA256.HashDataAsync(stream, cancellationToken);
            var actual = Convert.ToHexString(hash).ToLowerInvariant();
            if (!CryptographicOperations.FixedTimeEquals(
                    Convert.FromHexString(actual), Convert.FromHexString(required.Sha256)))
            {
                throw BuildCompatibilityError(required.Name, "does not match EverLeaf's server data");
            }
        }

        progress?.Report((10, "EverLeaf map and NPC data verified."));
    }

    private static InvalidOperationException BuildCompatibilityError(string file, string reason) =>
        new(
            $"{file} {reason}. EverLeaf requires the matching EverLeaf/Cosmic v83 WZ data set. " +
            "Using a generic clean-v83 Map.wz/Npc.wz can cause missing or misplaced NPCs. " +
            "Use Repair after installing the supported EverLeaf client data.");
}
