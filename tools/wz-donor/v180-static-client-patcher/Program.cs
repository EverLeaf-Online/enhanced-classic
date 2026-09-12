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
    var w = new WzFile(p, WzMapleVersion.BMS);
    var st = w.ParseWzFile();
    if (st != WzFileParseStatus.Success) { w.Dispose(); throw new InvalidDataException($"Donor parse failed {Path.GetFileName(p)} with BMS key: {st}"); }
    return w;
}

static ImageLocation? FindImageExact(WzDirectory root, string relativePath)
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
    return image == null ? null : new ImageLocation(image, parts[..^1]);
}

static IEnumerable<ImageLocation> EnumerateImages(WzDirectory root, string[] prefix)
{
    foreach (var image in root.WzImages) yield return new ImageLocation(image, prefix);
    foreach (var sub in root.WzDirectories)
    {
        var next = prefix.Concat(new[] { sub.Name }).ToArray();
        foreach (var row in EnumerateImages(sub, next)) yield return row;
    }
}

static ImageLocation ResolveDonorImage(WzDirectory root, string requestedPath)
{
    var exact = FindImageExact(root, requestedPath);
    if (exact != null) return exact.Value;
    var baseName = requestedPath.Split('/', StringSplitOptions.RemoveEmptyEntries).LastOrDefault()
        ?? throw new InvalidDataException($"Invalid donor path: {requestedPath}");
    var hits = EnumerateImages(root, Array.Empty<string>())
        .Where(x => string.Equals(x.Image.Name, baseName, StringComparison.OrdinalIgnoreCase))
        .Take(3).ToArray();
    if (hits.Length == 1) return hits[0];
    if (hits.Length == 0) throw new InvalidDataException($"Donor path missing: {requestedPath}");
    throw new InvalidDataException($"Donor path ambiguous after basename fallback: {requestedPath}; matches={string.Join(',', hits.Select(h => h.FullPath))}");
}

static WzDirectory EnsureDirs(WzFile targetFile, WzDirectory root, IEnumerable<string> dirs)
{
    var d = root;
    foreach (var name in dirs)
    {
        var next = d.GetDirectoryByName(name);
        if (next == null)
        {
            // New directories must inherit the target WZ IV/version/hash context.
            // A bare new WzDirectory(name) leaves WzIv null and crashes the writer
            // as soon as a newly-created Character/Map/etc. subtree is serialized.
            next = new WzDirectory(name, targetFile);
            d.AddDirectory(next);
        }
        d = next;
    }
    return d;
}

static void HashText(IncrementalHash h, string? s)
{
    h.AppendData(Encoding.UTF8.GetBytes(s ?? string.Empty));
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
                try { HashText(h, p.GetString()); }
                catch { HashText(h, p.WzValue?.ToString()); }
            }
            if (p.WzProperties != null) Walk(p.WzProperties);
        }
    }
    Walk(img.WzProperties);
    return Convert.ToHexString(h.GetHashAndReset()).ToLowerInvariant();
}

static int SanitizeForWrite(WzImage image)
{
    var repaired = 0;
    void Walk(IEnumerable<WzImageProperty> ps)
    {
        foreach (var p in ps)
        {
            if (p is WzStringProperty s && s.Value == null) { s.Value = string.Empty; repaired++; }
            if (p is WzUOLProperty u && u.Value == null) { u.Value = string.Empty; repaired++; }
            if (p.WzProperties != null) Walk(p.WzProperties);
        }
    }
    Walk(image.WzProperties);
    return repaired;
}

var targetHashBefore = Sha(targetPath);
var donorHash = Sha(donorPath);
short targetVersion, donorVersion;
var staged = new List<StagedImage>();
var sanitizedScalarCount = 0;

using (var target = OpenTarget(targetPath))
using (var donor = OpenDonor(donorPath))
{
    targetVersion = target.Version;
    donorVersion = donor.Version;
    foreach (var requestedPath in requested)
    {
        var source = ResolveDonorImage(donor.WzDirectory, requestedPath);
        var actualPath = source.FullPath;
        if (FindImageExact(target.WzDirectory, actualPath) != null)
            throw new InvalidOperationException($"Target collision at resolved donor path: requested={requestedPath}, resolved={actualPath}");
        var donorDigest = ImageDigest(source.Image);
        var clone = source.Image.DeepClone();
        sanitizedScalarCount += SanitizeForWrite(clone);
        EnsureDirs(target, target.WzDirectory, source.Dirs).AddImage(clone);
        staged.Add(new StagedImage(requestedPath, actualPath, donorDigest));
    }
    if (staged.Count == 0) throw new InvalidOperationException("Refusing empty static candidate.");
    target.SaveToDisk(outputPath);
}

if (Sha(targetPath) != targetHashBefore)
    throw new InvalidOperationException("Source target WZ changed while staging.");

var verified = 0;
using (var output = OpenTarget(outputPath))
{
    foreach (var row in staged)
    {
        var image = FindImageExact(output.WzDirectory, row.ResolvedPath)
            ?? throw new InvalidDataException($"Saved output lost: requested={row.RequestedPath}, resolved={row.ResolvedPath}");
        var outputDigest = ImageDigest(image.Image);
        if (!string.Equals(outputDigest, row.DonorDigest, StringComparison.OrdinalIgnoreCase))
            throw new InvalidDataException($"Donor/output image digest mismatch: requested={row.RequestedPath}, resolved={row.ResolvedPath}");
        verified++;
    }
}

var fallbackCount = staged.Count(x => !string.Equals(x.RequestedPath, x.ResolvedPath, StringComparison.OrdinalIgnoreCase));
var manifest = new
{
    schemaVersion = 5,
    kind = "gms-v180-static-wz-staging-candidate",
    approved = false,
    productionApplyAllowed = false,
    family = Path.GetFileName(targetPath),
    donorCryptoKey = "BMS",
    requestedCount = requested.Length,
    stagedCount = staged.Count,
    verifiedCount = verified,
    basenameFallbackCount = fallbackCount,
    sanitizedNullStringOrUolCount = sanitizedScalarCount,
    source = new { path = targetPath, sha256 = targetHashBefore, version = targetVersion, size = new FileInfo(targetPath).Length },
    donor = new { path = donorPath, sha256 = donorHash, version = donorVersion, size = new FileInfo(donorPath).Length },
    output = new { path = outputPath, sha256 = Sha(outputPath), size = new FileInfo(outputPath).Length },
    validation = new { sourceUnchanged = true, noTargetCollisions = true, outputReparsed = true, donorImageDigestsMatch = true, nonEmptyCandidate = true, newDirectoriesInheritTargetCryptoContext = true },
    images = staged.Select(x => new { requestedPath = x.RequestedPath, resolvedPath = x.ResolvedPath }).ToArray(),
};
File.WriteAllText(manifestPath, JsonSerializer.Serialize(manifest, new JsonSerializerOptions { WriteIndented = true }) + Environment.NewLine);
Console.WriteLine($"STAGED {Path.GetFileName(targetPath)}: {verified:N0}/{requested.Length:N0} donor-only images verified; fallback={fallbackCount:N0}; sanitized={sanitizedScalarCount:N0}");
Console.WriteLine($"OUTPUT {outputPath}");
Console.WriteLine("approved=false / productionApplyAllowed=false");
return 0;

internal readonly record struct ImageLocation(WzImage Image, string[] Dirs)
{
    public string FullPath => string.Join('/', Dirs.Append(Image.Name));
}
internal readonly record struct StagedImage(string RequestedPath, string ResolvedPath, string DonorDigest);
