using System.Security.Cryptography;
using System.Text.Json;
using System.IO.Compression;
using EverLeaf.Launcher;
using Xunit;

namespace EverLeaf.Launcher.Tests;

public sealed class PatchServiceTests
{
    [Fact]
    public void ReadsTheLowercaseProductionJsonShape()
    {
        var envelope = JsonSerializer.Deserialize<SignedManifest>(
            """{"payload":"cGF5bG9hZA==","signature":"c2lnbmF0dXJl"}""",
            PatchService.SerializerOptions);
        var manifest = JsonSerializer.Deserialize<PatchManifest>(
            """{"version":"production","files":[{"path":"Base.wz","url":"/patches/Base.wz","sha256":"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa","size":6540}],"launcher":{"version":"abc123","url":"/launcher/download","sha256":"bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb","size":1234}}""",
            PatchService.SerializerOptions);

        Assert.Equal("cGF5bG9hZA==", envelope?.Payload);
        Assert.Equal("production", manifest?.Version);
        Assert.Equal("Base.wz", Assert.Single(manifest!.Files).Path);
        Assert.Equal("abc123", manifest.Launcher?.Version);
    }

    [Fact]
    public void LaunchesTheElevationAwareGameThroughWindowsShell()
    {
        var gameDirectory = System.IO.Path.Combine("C:\\", "EverLeaf Test");
        var executable = System.IO.Path.Combine(gameDirectory, LauncherConfiguration.GameExecutable);
        var start = GameLauncher.CreateStartInfo(executable, gameDirectory);

        Assert.Equal(executable, start.FileName);
        Assert.Equal(gameDirectory, start.WorkingDirectory);
        Assert.True(start.UseShellExecute);
        Assert.Empty(start.ArgumentList);
    }

    [Fact]
    public void RemovesOnlyTheLegacyExecutableAfterEverLeafExists()
    {
        using var temp = new TemporaryDirectory();
        var current = System.IO.Path.Combine(temp.Path, LauncherConfiguration.GameExecutable);
        var legacy = System.IO.Path.Combine(temp.Path, LauncherConfiguration.LegacyGameExecutable);
        File.WriteAllText(legacy, "legacy");
        using var service = new PatchService(temp.Path);

        service.RemoveLegacyGameExecutable();
        Assert.True(File.Exists(legacy));

        File.WriteAllText(current, "verified current client");
        service.RemoveLegacyGameExecutable();
        Assert.True(File.Exists(current));
        Assert.False(File.Exists(legacy));
    }

    [Fact]
    public void VerifiesRsaPssSignatureAndRejectsTampering()
    {
        using var rsa = RSA.Create(3072);
        var payload = "signed managed baseline"u8.ToArray();
        var signature = rsa.SignData(payload, HashAlgorithmName.SHA256, RSASignaturePadding.Pss);
        PatchService.VerifySignature(payload, signature, rsa.ExportSubjectPublicKeyInfoPem());
        payload[0] ^= 1;
        Assert.Throws<InvalidOperationException>(() =>
            PatchService.VerifySignature(payload, signature, rsa.ExportSubjectPublicKeyInfoPem()));
    }

    [Theory]
    [InlineData("../escape.dll", "/patches/escape.dll")]
    [InlineData("Data/File.wz", "https://evil.example/File.wz")]
    [InlineData("Data/File.wz", "http://132-145-141-79.sslip.io/patches/File.wz")]
    public void RejectsUnsafeManifestEntries(string path, string url)
    {
        using var temp = new TemporaryDirectory();
        using var service = new PatchService(temp.Path);
        var manifest = new PatchManifest("test", [new PatchEntry(path, url, new string('a', 64), 1)]);
        Assert.Throws<InvalidOperationException>(() => service.ValidateManifest(manifest));
    }

    [Fact]
    public void RejectsEmptyAndCaseInsensitiveDuplicateManifests()
    {
        using var temp = new TemporaryDirectory();
        using var service = new PatchService(temp.Path);
        Assert.Throws<InvalidOperationException>(() => service.ValidateManifest(new PatchManifest("test", [])));
        var files = new[] {
            new PatchEntry("Data/File.wz", "/patches/Data/File.wz", new string('a', 64), 1),
            new PatchEntry("data/file.wz", "/patches/data/file.wz", new string('b', 64), 1)
        };
        Assert.Throws<InvalidOperationException>(() => service.ValidateManifest(new PatchManifest("test", files)));
    }

    [Fact]
    public void RequiresTheCompleteThirtySixFileClient()
    {
        using var temp = new TemporaryDirectory();
        using var service = new PatchService(temp.Path);
        var complete = LauncherConfiguration.RequiredGameFiles
            .Select(path => new PatchEntry(path, "/patches/" + path, new string('a', 64), 1))
            .ToArray();

        service.ValidateManifest(new PatchManifest("complete", complete));
        Assert.Equal(36, complete.Length);
        Assert.Throws<InvalidOperationException>(() =>
            service.ValidateManifest(new PatchManifest("missing-one", complete.Skip(1).ToArray())));
    }

    [Fact]
    public async Task RepairPlanCountsMissingAndCorruptManagedFiles()
    {
        using var temp = new TemporaryDirectory();
        using var service = new PatchService(temp.Path);
        var files = LauncherConfiguration.RequiredGameFiles
            .Select((path, index) =>
            {
                var bytes = Enumerable.Repeat((byte)(index + 1), index + 1).ToArray();
                var hash = Convert.ToHexString(SHA256.HashData(bytes)).ToLowerInvariant();
                return new PatchEntry(path, "/patches/" + path, hash, bytes.LongLength);
            })
            .ToArray();
        var manifest = new PatchManifest("bootstrap", files);

        Assert.Equal(
            files.Sum(file => file.Size),
            await service.CalculateRepairFileBytesAsync(manifest, CancellationToken.None));

        var valid = files[0];
        await File.WriteAllBytesAsync(
            System.IO.Path.Combine(temp.Path, valid.Path),
            Enumerable.Repeat((byte)1, checked((int)valid.Size)).ToArray());

        var sameSizeCorrupt = files[1];
        await File.WriteAllBytesAsync(
            System.IO.Path.Combine(temp.Path, sameSizeCorrupt.Path),
            Enumerable.Repeat((byte)255, checked((int)sameSizeCorrupt.Size)).ToArray());

        var wrongSize = files[2];
        await File.WriteAllBytesAsync(
            System.IO.Path.Combine(temp.Path, wrongSize.Path),
            new byte[checked((int)wrongSize.Size + 1)]);

        Assert.Equal(
            files.Skip(1).Sum(file => file.Size),
            await service.CalculateRepairFileBytesAsync(manifest, CancellationToken.None));
    }

    [Fact]
    public async Task DetectsAndRepairsDeliberatelyCorruptedFile()
    {
        using var temp = new TemporaryDirectory();
        var destination = System.IO.Path.Combine(temp.Path, "managed.bin");
        var canonical = "canonical EverLeaf runtime"u8.ToArray();
        var expected = Convert.ToHexString(SHA256.HashData(canonical)).ToLowerInvariant();
        await File.WriteAllTextAsync(destination, "corrupted");
        Assert.False(await PatchService.HashMatchesAsync(destination, expected, CancellationToken.None));
        var staged = destination + ".everleaf-new";
        await File.WriteAllBytesAsync(staged, canonical);
        Assert.True(await PatchService.HashMatchesAsync(staged, expected, CancellationToken.None));
        File.Move(staged, destination, true);
        Assert.True(await PatchService.HashMatchesAsync(destination, expected, CancellationToken.None));
    }

    [Theory]
    [InlineData("same", "same", false)]
    [InlineData("old", "new", true)]
    [InlineData("unknown", "release", true)]
    public void LauncherVersionComparisonIsExact(string current, string published, bool expected)
    {
        Assert.Equal(expected, LauncherUpdateService.NeedsUpdate(current, published));
    }

    [Theory]
    [InlineData("https://evil.example/launcher.zip")]
    [InlineData("/patches/EverLeafLauncher.zip")]
    [InlineData("/launcher/download/extra")]
    public void RejectsUntrustedLauncherReleaseUrls(string url)
    {
        var release = new LauncherRelease("release", url, new string('a', 64), 100);
        Assert.Throws<InvalidOperationException>(() => PatchService.ValidateLauncherRelease(release));
    }

    [Fact]
    public async Task ExtractsOnlyTheSingleExpectedLauncherExecutable()
    {
        using var temp = new TemporaryDirectory();
        var archivePath = System.IO.Path.Combine(temp.Path, "launcher.zip");
        var destination = System.IO.Path.Combine(temp.Path, "extracted", LauncherConfiguration.LauncherExecutable);
        Directory.CreateDirectory(System.IO.Path.GetDirectoryName(destination)!);
        using (var archive = ZipFile.Open(archivePath, ZipArchiveMode.Create))
        {
            var entry = archive.CreateEntry(LauncherConfiguration.LauncherExecutable);
            await using var stream = entry.Open();
            await stream.WriteAsync("trusted launcher"u8.ToArray());
        }

        await LauncherUpdateService.ExtractLauncherAsync(archivePath, destination, CancellationToken.None);

        Assert.Equal("trusted launcher", await File.ReadAllTextAsync(destination));
    }

    [Fact]
    public async Task RejectsLauncherArchivesWithAdditionalFiles()
    {
        using var temp = new TemporaryDirectory();
        var archivePath = System.IO.Path.Combine(temp.Path, "launcher.zip");
        using (var archive = ZipFile.Open(archivePath, ZipArchiveMode.Create))
        {
            archive.CreateEntry(LauncherConfiguration.LauncherExecutable);
            archive.CreateEntry("unexpected.dll");
        }

        await Assert.ThrowsAsync<InvalidOperationException>(() => LauncherUpdateService.ExtractLauncherAsync(
            archivePath,
            System.IO.Path.Combine(temp.Path, "out.exe"),
            CancellationToken.None));
    }

    [Fact]
    public void UpdateHelperArgumentsPreservePathsWithSpaces()
    {
        using var temp = new TemporaryDirectory();
        var updateDirectory = System.IO.Path.Combine(System.IO.Path.GetTempPath(), "EverLeafLauncher-update-test value");
        var updater = System.IO.Path.Combine(updateDirectory, LauncherConfiguration.LauncherExecutable);
        var target = System.IO.Path.Combine(temp.Path, LauncherConfiguration.LauncherExecutable);

        var start = LauncherUpdateApplier.CreateApplyStartInfo(updater, target, 42, updateDirectory);

        Assert.Equal(updater, start.FileName);
        Assert.Equal(new[] { "--apply-launcher-update", target, "42", updateDirectory }, start.ArgumentList);
    }

    [Fact]
    public void UpdateHelperRejectsAStagingDirectoryOutsideWindowsTemp()
    {
        var outside = System.IO.Path.Combine("C:\\", "EverLeafLauncher-update-untrusted");
        var source = System.IO.Path.Combine(outside, LauncherConfiguration.LauncherExecutable);
        var target = System.IO.Path.Combine("C:\\EverLeaf", LauncherConfiguration.LauncherExecutable);

        Assert.Throws<InvalidOperationException>(() =>
            LauncherUpdateApplier.ValidateApplyPaths(source, target, outside));
    }

    private sealed class TemporaryDirectory : IDisposable
    {
        public string Path { get; } = System.IO.Path.Combine(System.IO.Path.GetTempPath(), "everleaf-tests-" + Guid.NewGuid());
        public TemporaryDirectory() => Directory.CreateDirectory(Path);
        public void Dispose() => Directory.Delete(Path, true);
    }
}
