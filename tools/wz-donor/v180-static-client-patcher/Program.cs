using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using MapleLib.WzLib;
using MapleLib.WzLib.WzProperties;

if (args.Length != 5)
{
    Console.Error.WriteLine("Usage: EverLeafV180StaticPatcher <target.wz> <donor.wz> <paths.txt> <output.wz> <manifest.json>");
    return 2;
}

var targetPath = Path.GetFullPath(args[0]);
var donorPath = Path.GetFullPath(args[1]);
var pathsPath = Path.GetFullPath(args[2]);
var outputPath = Path.GetFullPath(args[3]);
var manifestPath = Path.GetFullPath(args[4]);
foreach (var p in new[] { targetPath, donorPath, pathsPath })
    if (!File.Exists(p)) throw new FileNotFoundException(p);
if (File.Exists(outputPath) || File.Exists(manifestPath))
    throw new IOException("Refusing to overwrite an existing staging output.");
Directory.CreateDirectory(Path.GetDirectoryName(outputPath)!);
Directory.CreateDirectory(Path.GetDirectoryName(manifestPath)!);

var requested = File.ReadAllLines(pathsPath)
    .Select(x => x.Trim().Replace('\\', '/'))
    .Where(x => x.Length > 0 && !x.StartsWith('#'))
    .Distinct(StringComparer.OrdinalIgnoreCase)
    .OrderBy(x => x, StringComparer.OrdinalIgnoreCase)
    .ToArray();
if (requested.Length == 0) throw new InvalidDataException("Empty path manifest.");

static string Sha(string p)
{
    using var s = File.OpenRead(p);
    return Convert.ToHexString(SHA256.HashData(s)).ToLowerInvariant();
}

static WzFile OpenTarget(string p)
{
    var w = new WzFile(p, WzMapleVersion.GMS);
    var st = w.ParseWzFile();
    if (st != WzFileParseStatus.Success) { w.Dispose(); throw new InvalidDataException($"Target parse failed {Path.GetFileName(p)}: {st}"); }
    return w;
}

static WzFile OpenDonor(string p)
{
    if (!File.Exists(Path.Combine(Path.GetDirectoryName(p)!, "ZLZ.dll")))
        throw new FileNotFoundException("v180 donor requires ZLZ.dll beside the WZ file.");
    var w = new WzFile(p, WzMapleVersion.GETFROMZLZ);
    var st = w.ParseWzFile();
    if (st != WzFileParseStatus.Success) { w.Dispose(); throw new InvalidDataException($"Donor parse failed {Path.GetFileName(p)}: {st}"); }
    return w;
}

static (WzImage image, string[] dirs)? FindImage(WzDirectory root, string relativePath)
{
    var parts = relativePath.Split('/', StringSplitOptions.RemoveEmptyEntries);
    if (parts.Length == 0) return null;
    var d = root;
    for (var i = 0; i < parts.Length - 1; i++)
    {
        d = d.GetDirectoryByName(parts[i]);
        if (d == null) return null;
    }
    var image = d.GetImageByName(parts[^1]);
    return image == null ? null : (image, parts[..^1]);
}

static WzDirectory EnsureDirs(WzDirectory root, IEnumerable<string> dirs)
{
    var d = root;
    foreach (var name in dirs)
    {
        var next = d.GetDirectoryByName(name);
        if (next == null) { next = new WzDirectory(name); d.AddDirectory(next); }
        d = next;
    }
    return d;
}

static void HashText(IncrementalHash h, string s)
{
    h.AppendData(Encoding.UTF8.GetBytes(s));
    h.AppendData(new byte[] { 0 });
}

static string ImageDigest(WzImage img)
{
    using var h = IncrementalHash.CreateHash(HashAlgorithmName.SHA256);
    HashText(h, img.Name);
    void Walk(IEnumerable<WzImageProperty> ps)
    {
        foreach (var p in ps)
        {
            HashText(h, p.Name);
            HashText(h, p.PropertyType.ToString());
            if (p is WzCanvasProperty canvas)
                h.AppendData(canvas.PngProperty.GetCompressedBytesForExtraction(false));
            else if (p.WzProperties == null)
            {
                try { HashText(h, p.GetString() ?? ""); }
                catch { HashText(h, p.WzValue?.ToString() ?? ""); }
            }
            if (p.WzProperties != null) Walk(p.WzProperties);
        }
    }
    Walk(img.WzProperties);
    return Convert.ToHexString(h.GetHashAndReset()).ToLowerInvariant();
}

var targetHashBefore = Sha(targetPath);
var donorHash = Sha(donorPath);
short targetVersion, donorVersion;
var donorDigests = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase);

using (var target = OpenTarget(targetPath))
using (var donor = OpenDonor(donorPath))
{
    targetVersion = target.Version;
    donorVersion = donor.Version;
    foreach (var rel in requested)
    {
        if (FindImage(target.WzDirectory, rel) != null)
            throw new InvalidOperationException($"Target collision: {rel}");
        var source = FindImage(donor.WzDirectory, rel)
            ?? throw new InvalidDataException($"Donor path missing: {rel}");
        donorDigests[rel] = ImageDigest(source.image);
        EnsureDirs(target.WzDirectory, source.dirs).AddImage(source.image.DeepClone());
    }
    target.SaveToDisk(outputPath);
}

if (Sha(targetPath) != targetHashBefore)
    throw new InvalidOperationException("Source target WZ changed while staging.");

var verified = 0;
using (var output = OpenTarget(outputPath))
{
    foreach (var rel in requested)
    {
        var image = FindImage(output.WzDirectory, rel)
            ?? throw new InvalidDataException($"Saved output lost: {rel}");
        var outputDigest = ImageDigest(image.image);
        if (!string.Equals(outputDigest, donorDigests[rel], StringComparison.OrdinalIgnoreCase))
            throw new InvalidDataException($"Donor/output image digest mismatch: {rel}");
        verified++;
    }
}

var manifest = new
{
    schemaVersion = 1,
    kind = "gms-v180-static-wz-staging-candidate",
    approved = false,
    productionApplyAllowed = false,
    family = Path.GetFileName(targetPath),
    requestedCount = requested.Length,
    verifiedCount = verified,
    source = new { path = targetPath, sha256 = targetHashBefore, version = targetVersion, size = new FileInfo(targetPath).Length },
    donor = new { path = donorPath, sha256 = donorHash, version = donorVersion, size = new FileInfo(donorPath).Length },
    output = new { path = outputPath, sha256 = Sha(outputPath), size = new FileInfo(outputPath).Length },
    validation = new { sourceUnchanged = true, noTargetCollisions = true, outputReparsed = true, donorImageDigestsMatch = true },
    paths = requested,
};
File.WriteAllText(manifestPath, JsonSerializer.Serialize(manifest, new JsonSerializerOptions { WriteIndented = true }) + Environment.NewLine);
Console.WriteLine($"STAGED {Path.GetFileName(targetPath)}: {verified:N0}/{requested.Length:N0} donor-only images verified");
Console.WriteLine($"OUTPUT {outputPath}");
Console.WriteLine("approved=false / productionApplyAllowed=false");
return 0;