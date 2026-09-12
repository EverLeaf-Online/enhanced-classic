using System.Drawing;
using System.Drawing.Imaging;
using System.Runtime.InteropServices;
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
        foreach (var image in EnumerateImages(sub, next)) yield return image;
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

static WzDirectory EnsureDirs(WzDirectory root, WzFile targetFile, IEnumerable<string> dirs)
{
    var d = root;
    foreach (var name in dirs)
    {
        var next = d.GetDirectoryByName(name);
        if (next == null)
        {
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

static WzObject? ResolveUolObject(WzObject? value)
{
    var seen = new HashSet<WzObject>();
    var current = value;
    while (current is WzUOLProperty uol)
    {
        if (!seen.Add(current)) return null;
        current = uol.LinkValue;
    }
    return current;
}

static WzImage? FindOwningImage(WzObject? value)
{
    var current = value;
    while (current != null)
    {
        if (current is WzImage image) return image;
        current = current.Parent;
    }
    return null;
}

static string AlphaWzPrefix(string wzFileName)
{
    var name = Path.GetFileNameWithoutExtension(wzFileName);
    var end = name.Length;
    while (end > 0 && char.IsDigit(name[end - 1])) end--;
    return name[..end];
}

static WzImageProperty? ResolveModernCanvasLink(WzCanvasProperty canvas)
{
    var inlink = (canvas[WzCanvasProperty.InlinkPropertyName] as WzStringProperty)?.Value;
    if (!string.IsNullOrWhiteSpace(inlink))
    {
        var image = FindOwningImage(canvas);
        if (image == null) return null;
        if (!image.Parsed) image.ParseImage();
        return image.GetFromPath(inlink.Trim().Trim('/')) as WzImageProperty;
    }

    var outlink = (canvas[WzCanvasProperty.OutlinkPropertyName] as WzStringProperty)?.Value;
    if (string.IsNullOrWhiteSpace(outlink)) return null;
    var wzFile = canvas.WzFileParent;
    if (wzFile == null) return null;

    var normalized = outlink.Trim().Trim('/').Replace('\\', '/');
    var imageEnd = normalized.IndexOf(".img", StringComparison.OrdinalIgnoreCase);
    if (imageEnd < 0) return null;
    imageEnd += 4;
    var imagePath = normalized[..imageEnd];
    var propertyPath = imageEnd < normalized.Length ? normalized[(imageEnd + 1)..] : string.Empty;

    var slash = imagePath.IndexOf('/');
    if (slash >= 0)
    {
        var linkPrefix = imagePath[..slash];
        var fileBase = Path.GetFileNameWithoutExtension(wzFile.Name);
        var alphaPrefix = AlphaWzPrefix(wzFile.Name);
        if (string.Equals(linkPrefix, fileBase, StringComparison.OrdinalIgnoreCase) ||
            string.Equals(linkPrefix, alphaPrefix, StringComparison.OrdinalIgnoreCase))
            imagePath = imagePath[(slash + 1)..];
    }

    var location = FindImageExact(wzFile.WzDirectory, imagePath);
    if (location == null) return null;
    var linkedImage = location.Value.Image;
    if (!linkedImage.Parsed) linkedImage.ParseImage();
    if (string.IsNullOrEmpty(propertyPath)) return null;
    return linkedImage.GetFromPath(propertyPath) as WzImageProperty;
}

static WzPngProperty? ResolveEffectiveCanvasPng(WzCanvasProperty canvas)
{
    var seen = new HashSet<WzImageProperty>();
    WzImageProperty current = canvas;
    for (var depth = 0; depth < 64; depth++)
    {
        if (!seen.Add(current)) return null;
        if (current is WzCanvasProperty currentCanvas)
        {
            if (currentCanvas.ContainsInlinkProperty() || currentCanvas.ContainsOutlinkProperty())
            {
                var linked = ResolveModernCanvasLink(currentCanvas);
                if (linked == null || ReferenceEquals(linked, currentCanvas)) return null;
                current = linked;
                continue;
            }
            return currentCanvas.PngProperty;
        }
        if (current is WzPngProperty png) return png;
        if (current is WzUOLProperty uol && ResolveUolObject(uol) is WzImageProperty resolved)
        {
            current = resolved;
            continue;
        }
        return null;
    }
    return null;
}

static void AppendPngToken(List<string> tokens, string path, WzPngProperty png)
{
    using var bmp = png.GetImage(false);
    var rect = new Rectangle(0, 0, bmp.Width, bmp.Height);
    var data = bmp.LockBits(rect, ImageLockMode.ReadOnly, PixelFormat.Format32bppArgb);
    try
    {
        var len = Math.Abs(data.Stride) * data.Height;
        var bytes = new byte[len];
        Marshal.Copy(data.Scan0, bytes, 0, len);
        tokens.Add($"{path}|Canvas|{bmp.Width}x{bmp.Height}|{Convert.ToHexString(SHA256.HashData(bytes)).ToLowerInvariant()}");
    }
    finally { bmp.UnlockBits(data); }
}

static bool AppendCanvasToken(List<string> tokens, string path, WzCanvasProperty canvas)
{
    var hasModernLink = canvas.ContainsInlinkProperty() || canvas.ContainsOutlinkProperty();
    var effective = hasModernLink ? ResolveEffectiveCanvasPng(canvas) : canvas.PngProperty;
    if (effective == null)
    {
        AppendPngToken(tokens, path, canvas.PngProperty);
        return false;
    }
    AppendPngToken(tokens, path, effective);
    return hasModernLink;
}

static void AppendSemanticProperty(List<string> tokens, WzImageProperty p, string path, bool resolveUol)
{
    if (p is WzUOLProperty uol)
    {
        if (resolveUol && ResolveUolObject(uol) is WzImageProperty resolved)
        {
            // Compare a resolved UOL as the property it points to, but do not recursively
            // resolve nested UOLs. This makes a materialized property semantically equivalent
            // to its donor link while bounding traversal across circular/cross-linked graphs.
            AppendSemanticProperty(tokens, resolved, path, false);
            return;
        }
        tokens.Add($"{path}|UOL|{uol.Value ?? string.Empty}");
        return;
    }

    if (p is WzShortProperty || p is WzIntProperty || p is WzLongProperty)
    {
        tokens.Add($"{path}|IntegralNumber|{Convert.ToInt64(p.WzValue).ToString(System.Globalization.CultureInfo.InvariantCulture)}");
        return;
    }

    var resolvedModernCanvasLink = false;
    if (p is WzCanvasProperty canvas)
    {
        resolvedModernCanvasLink = AppendCanvasToken(tokens, path, canvas);
    }
    else if (p.WzProperties == null)
    {
        string? value;
        try { value = p.GetString(); }
        catch { value = p.WzValue?.ToString(); }
        tokens.Add($"{path}|{p.PropertyType}|{value ?? string.Empty}");
        return;
    }
    else tokens.Add($"{path}|{p.PropertyType}|");

    if (p.WzProperties != null)
    {
        foreach (var child in p.WzProperties)
        {
            if (resolvedModernCanvasLink && (string.Equals(child.Name, WzCanvasProperty.InlinkPropertyName, StringComparison.OrdinalIgnoreCase) || string.Equals(child.Name, WzCanvasProperty.OutlinkPropertyName, StringComparison.OrdinalIgnoreCase)))
                continue;
            AppendSemanticProperty(tokens, child, path + "/" + child.Name, resolveUol);
        }
    }
}

static string PropertySemanticDigest(WzImageProperty property)
{
    var tokens = new List<string>();
    AppendSemanticProperty(tokens, property, "$", false);
    tokens.Sort(StringComparer.Ordinal);
    using var h = IncrementalHash.CreateHash(HashAlgorithmName.SHA256);
    foreach (var token in tokens) HashText(h, token);
    return Convert.ToHexString(h.GetHashAndReset()).ToLowerInvariant();
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
            else if (p is WzUOLProperty uol)
                HashText(h, uol.Value);
            else if (p.WzProperties == null)
            {
                try { HashText(h, p.GetString()); }
                catch { HashText(h, p.WzValue?.ToString()); }
            }
            if (p is not WzUOLProperty && p.WzProperties != null) Walk(p.WzProperties);
        }
    }
    Walk(img.WzProperties);
    return Convert.ToHexString(h.GetHashAndReset()).ToLowerInvariant();
}

static List<string> SemanticTokens(WzImage img)
{
    var tokens = new List<string> { $"image|{img.Name}" };
    foreach (var p in img.WzProperties)
        AppendSemanticProperty(tokens, p, p.Name, true);
    tokens.Sort(StringComparer.Ordinal);
    return tokens;
}

static string ImageSemanticDigest(WzImage img)
{
    using var h = IncrementalHash.CreateHash(HashAlgorithmName.SHA256);
    foreach (var token in SemanticTokens(img)) HashText(h, token);
    return Convert.ToHexString(h.GetHashAndReset()).ToLowerInvariant();
}

static string FirstSemanticDifference(WzImage donor, WzImage output)
{
    var a = SemanticTokens(donor);
    var b = SemanticTokens(output);
    var n = Math.Min(a.Count, b.Count);
    for (var i = 0; i < n; i++)
    {
        if (!string.Equals(a[i], b[i], StringComparison.Ordinal))
        {
            static string Clip(string s) => s.Length <= 500 ? s : s[..500] + "...";
            return $"token={i}; donor={Clip(a[i])}; output={Clip(b[i])}";
        }
    }
    if (a.Count != b.Count) return $"token-count donor={a.Count} output={b.Count}";
    return "semantic-token-streams-identical";
}

static Dictionary<string, WzImageProperty> RawPropertyMap(WzImage image)
{
    var map = new Dictionary<string, WzImageProperty>(StringComparer.Ordinal);
    void Walk(IEnumerable<WzImageProperty> ps, string parent)
    {
        foreach (var p in ps)
        {
            var path = parent.Length == 0 ? p.Name : parent + "/" + p.Name;
            map[path] = p;
            if (p is not WzUOLProperty && p.WzProperties != null) Walk(p.WzProperties, path);
        }
    }
    Walk(image.WzProperties, string.Empty);
    return map;
}

static int MaterializeIncompatibleUolDependencies(WzImage donorImage, WzImage candidateImage)
{
    var donorProps = RawPropertyMap(donorImage);
    var candidateProps = RawPropertyMap(candidateImage);
    var replacements = new List<(WzUOLProperty Candidate, WzImageProperty DonorResolved)>();

    foreach (var (path, donorProperty) in donorProps)
    {
        if (donorProperty is not WzUOLProperty donorUol) continue;
        if (!candidateProps.TryGetValue(path, out var candidateProperty) || candidateProperty is not WzUOLProperty candidateUol)
            continue;

        var donorResolved = ResolveUolObject(donorUol) as WzImageProperty;
        if (donorResolved == null) continue;
        var candidateResolved = ResolveUolObject(candidateUol) as WzImageProperty;
        if (candidateResolved != null && string.Equals(PropertySemanticDigest(donorResolved), PropertySemanticDigest(candidateResolved), StringComparison.OrdinalIgnoreCase))
            continue;

        replacements.Add((candidateUol, donorResolved));
    }

    foreach (var (candidateUol, donorResolved) in replacements)
    {
        if (candidateUol.Parent is not IPropertyContainer parent)
            throw new InvalidDataException($"Cannot materialize UOL without property-container parent: {candidateUol.FullPath}");
        var replacement = donorResolved.DeepClone();
        replacement.Name = candidateUol.Name;
        parent.RemoveProperty(candidateUol);
        parent.AddProperty(replacement);
    }
    return replacements.Count;
}

static (int Found, int Materialized, int Unresolved) MaterializeModernCanvasLinks(WzImage donorImage, WzImage candidateImage)
{
    var donorProps = RawPropertyMap(donorImage);
    var candidateProps = RawPropertyMap(candidateImage);
    var found = 0;
    var materialized = 0;
    var unresolved = 0;

    foreach (var (path, donorProperty) in donorProps)
    {
        if (donorProperty is not WzCanvasProperty donorCanvas) continue;
        if (!donorCanvas.ContainsInlinkProperty() && !donorCanvas.ContainsOutlinkProperty()) continue;
        found++;
        if (!candidateProps.TryGetValue(path, out var candidateProperty) || candidateProperty is not WzCanvasProperty candidateCanvas)
        {
            unresolved++;
            continue;
        }
        var effectivePng = ResolveEffectiveCanvasPng(donorCanvas);
        if (effectivePng == null)
        {
            unresolved++;
            continue;
        }

        candidateCanvas.PngProperty = (WzPngProperty)effectivePng.DeepClone();
        var inlink = candidateCanvas[WzCanvasProperty.InlinkPropertyName];
        if (inlink != null) candidateCanvas.RemoveProperty(inlink);
        var outlink = candidateCanvas[WzCanvasProperty.OutlinkPropertyName];
        if (outlink != null) candidateCanvas.RemoveProperty(outlink);
        materialized++;
    }

    return (found, materialized, unresolved);
}

static int SanitizeForWrite(WzImage image)
{
    var repaired = 0;
    void Walk(IEnumerable<WzImageProperty> ps)
    {
        foreach (var p in ps)
        {
            if (p is WzStringProperty s && s.Value == null) { s.Value = string.Empty; repaired++; }
            if (p is WzUOLProperty u)
            {
                if (u.Value == null) { u.Value = string.Empty; repaired++; }
                continue;
            }
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
var materializedUolDependencyCount = 0;
var modernCanvasLinkCount = 0;
var materializedModernCanvasLinkCount = 0;
var unresolvedModernCanvasLinkCount = 0;

using (var target = OpenTarget(targetPath))
using (var donor = OpenDonor(donorPath))
{
    targetVersion = target.Version;
    donorVersion = donor.Version;
    var clonePairs = new List<(WzImage Donor, WzImage Candidate)>();
    foreach (var requestedPath in requested)
    {
        var source = ResolveDonorImage(donor.WzDirectory, requestedPath);
        var actualPath = source.FullPath;
        if (FindImageExact(target.WzDirectory, actualPath) != null)
            throw new InvalidOperationException($"Target collision at resolved donor path: requested={requestedPath}, resolved={actualPath}");
        var donorDigest = ImageDigest(source.Image);
        var clone = source.Image.DeepClone();
        sanitizedScalarCount += SanitizeForWrite(clone);
        EnsureDirs(target.WzDirectory, target, source.Dirs).AddImage(clone);
        clonePairs.Add((source.Image, clone));
        staged.Add(new StagedImage(requestedPath, actualPath, donorDigest));
    }
    if (staged.Count == 0) throw new InvalidOperationException("Refusing empty static candidate.");

    // A donor-only image can UOL-link into a shared image whose old v83 contents are incomplete.
    // Preserve the donor semantics without replacing the shared target image by materializing only
    // those UOL targets that do not resolve equivalently after the donor-only image is attached.
    foreach (var pair in clonePairs)
    {
        materializedUolDependencyCount += MaterializeIncompatibleUolDependencies(pair.Donor, pair.Candidate);
        var canvasLinks = MaterializeModernCanvasLinks(pair.Donor, pair.Candidate);
        modernCanvasLinkCount += canvasLinks.Found;
        materializedModernCanvasLinkCount += canvasLinks.Materialized;
        unresolvedModernCanvasLinkCount += canvasLinks.Unresolved;
    }

    target.SaveToDisk(outputPath);
}

if (Sha(targetPath) != targetHashBefore)
    throw new InvalidOperationException("Source target WZ changed while staging.");

var verified = 0;
var semanticFallbackCount = 0;
using (var output = OpenTarget(outputPath))
using (var donor = OpenDonor(donorPath))
{
    foreach (var row in staged)
    {
        var image = FindImageExact(output.WzDirectory, row.ResolvedPath)
            ?? throw new InvalidDataException($"Saved output lost: requested={row.RequestedPath}, resolved={row.ResolvedPath}");
        var outputDigest = ImageDigest(image.Image);
        if (!string.Equals(outputDigest, row.DonorDigest, StringComparison.OrdinalIgnoreCase))
        {
            var donorImage = FindImageExact(donor.WzDirectory, row.ResolvedPath)
                ?? throw new InvalidDataException($"Donor image disappeared during semantic verification: {row.ResolvedPath}");
            var donorSemantic = ImageSemanticDigest(donorImage.Image);
            var outputSemantic = ImageSemanticDigest(image.Image);
            if (!string.Equals(donorSemantic, outputSemantic, StringComparison.OrdinalIgnoreCase))
            {
                var detail = FirstSemanticDifference(donorImage.Image, image.Image);
                throw new InvalidDataException($"Donor/output semantic image digest mismatch: requested={row.RequestedPath}, resolved={row.ResolvedPath}; {detail}");
            }
            semanticFallbackCount++;
        }
        verified++;
    }
}

var fallbackCount = staged.Count(x => !string.Equals(x.RequestedPath, x.ResolvedPath, StringComparison.OrdinalIgnoreCase));
var manifest = new
{
    schemaVersion = 14,
    kind = "gms-v180-static-wz-staging-candidate",
    approved = false,
    productionApplyAllowed = false,
    family = Path.GetFileName(targetPath),
    donorCryptoKey = "BMS",
    requestedCount = requested.Length,
    stagedCount = staged.Count,
    verifiedCount = verified,
    basenameFallbackCount = fallbackCount,
    semanticCanvasVerificationFallbackCount = semanticFallbackCount,
    sanitizedNullStringOrUolCount = sanitizedScalarCount,
    materializedIncompatibleUolDependencyCount = materializedUolDependencyCount,
    modernCanvasLinkCount,
    materializedModernCanvasLinkCount,
    unresolvedModernCanvasLinkCount,
    targetCryptoContextInheritedForCreatedDirectories = true,
    source = new { path = targetPath, sha256 = targetHashBefore, version = targetVersion, size = new FileInfo(targetPath).Length },
    donor = new { path = donorPath, sha256 = donorHash, version = donorVersion, size = new FileInfo(donorPath).Length },
    output = new { path = outputPath, sha256 = Sha(outputPath), size = new FileInfo(outputPath).Length },
    validation = new { sourceUnchanged = true, noTargetCollisions = true, outputReparsed = true, donorImageDigestsMatch = true, compressedOrSemanticCanvasVerification = true, semanticIntegralWidthNormalization = true, semanticResolvedUolDependencyVerification = true, modernCanvasLinksMaterializedWhenResolvable = true, customLegacyOutlinkResolver = true, semanticPropertyOrderNormalized = true, nonEmptyCandidate = true },
    images = staged.Select(x => new { requestedPath = x.RequestedPath, resolvedPath = x.ResolvedPath }).ToArray(),
};
File.WriteAllText(manifestPath, JsonSerializer.Serialize(manifest, new JsonSerializerOptions { WriteIndented = true }) + Environment.NewLine);
Console.WriteLine($"STAGED {Path.GetFileName(targetPath)}: {verified:N0}/{requested.Length:N0} donor-only images verified; fallback={fallbackCount:N0}; semantic-fallback={semanticFallbackCount:N0}; sanitized={sanitizedScalarCount:N0}; materialized-uol={materializedUolDependencyCount:N0}; canvas-links={materializedModernCanvasLinkCount:N0}/{modernCanvasLinkCount:N0}; unresolved-canvas-links={unresolvedModernCanvasLinkCount:N0}");
Console.WriteLine($"OUTPUT {outputPath}");
Console.WriteLine("approved=false / productionApplyAllowed=false");
return 0;

internal readonly record struct ImageLocation(WzImage Image, string[] Dirs)
{
    public string FullPath => string.Join('/', Dirs.Append(Image.Name));
}
internal readonly record struct StagedImage(string RequestedPath, string ResolvedPath, string DonorDigest);
