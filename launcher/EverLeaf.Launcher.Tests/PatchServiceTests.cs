using System.Security.Cryptography;
using System.Text.Json;
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
            """{"version":"production","files":[{"path":"Base.wz","url":"/patches/Base.wz","sha256":"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa","size":6540}]}""",
            PatchService.SerializerOptions);

        Assert.Equal("cGF5bG9hZA==", envelope?.Payload);
        Assert.Equal("production", manifest?.Version);
        Assert.Equal("Base.wz", Assert.Single(manifest!.Files).Path);
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

    private sealed class TemporaryDirectory : IDisposable
    {
        public string Path { get; } = System.IO.Path.Combine(System.IO.Path.GetTempPath(), "everleaf-tests-" + Guid.NewGuid());
        public TemporaryDirectory() => Directory.CreateDirectory(Path);
        public void Dispose() => Directory.Delete(Path, true);
    }
}
