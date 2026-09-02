using System.Security.Cryptography;
using System.Text.Json;
using MapleLib.WzLib;

if (args.Length is < 5 or > 6)
{
    Console.Error.WriteLine("Usage: ChairProgram <target-Item.wz> <target-String.wz> <donor-Item.wz> <donor-String.wz> <output-directory> [count]");
    return 2;
}

var targetItemPath = Path.GetFullPath(args[0]);
var targetStringPath = Path.GetFullPath(args[1]);
var donorItemPath = Path.GetFullPath(args[2]);
var donorStringPath = Path.GetFullPath(args[3]);
var outputDirectory = Path.GetFullPath(args[4]);
var batchCount = args.Length == 6 && int.TryParse(args[5], out var parsedCount) ? parsedCount : 3;
if (batchCount < 1 || batchCount > 50) throw new ArgumentOutOfRangeException(nameof(batchCount), "Chair batch count must be between 1 and 50.");
Directory.CreateDirectory(outputDirectory);

static string Sha256(string path)
{
    using var stream = File.OpenRead(path);
    return Convert.ToHexString(SHA256.HashData(stream)).ToLowerInvariant();
}

static WzFile OpenWz(string path)
{
    var wz = new WzFile(path, WzMapleVersion.GMS);
    var status = wz.ParseWzFile();
    if (status != WzFileParseStatus.Success)
    {
        wz.Dispose();
        throw new InvalidDataException($"Failed to parse {path}: {status}");
    }
    return wz;
}

static WzDirectory RequireDirectory(WzDirectory root, string name)
    => root.GetDirectoryByName(name) ?? throw new InvalidDataException($"Missing directory {name}");

static WzImage RequireImage(WzDirectory dir, string name)
    => dir.GetImageByName(name) ?? throw new InvalidDataException($"Missing image {name}");

static bool TryChairId(string name, out int id)
{
    id = 0;
    if (!int.TryParse(name, out var parsed)) return false;
    if (parsed >= 3010000 && parsed <= 3019999) { id = parsed; return true; }
    if (parsed >= 30100000 && parsed <= 30199999) { id = parsed / 10; return true; }
    return false;
}

static WzImageProperty? FindDirect(WzImage image, int id)
{
    var names = new[] { id.ToString(), id.ToString("D8") };
    foreach (var n in names)
    {
        var p = image[n];
        if (p != null) return p;
    }
    return null;
}

static (WzImage image, WzImageProperty property)? FindStringEntry(WzFile wz, int id)
{
    foreach (var image in wz.WzDirectory.WzImages)
    {
        var p = FindDirect(image, id);
        if (p != null) return (image, p);
    }
    return null;
}

static string ReadName(WzImageProperty strings, int id)
{
    var p = strings["name"];
    return p?.GetString() ?? $"Chair {id}";
}

foreach (var p in new[] { targetItemPath, targetStringPath, donorItemPath, donorStringPath })
    if (!File.Exists(p)) throw new FileNotFoundException(p);

var targetItemHashBefore = Sha256(targetItemPath);
var targetStringHashBefore = Sha256(targetStringPath);
var outputItemPath = Path.Combine(outputDirectory, "Item.wz");
var outputStringPath = Path.Combine(outputDirectory, "String.wz");
var manifestPath = Path.Combine(outputDirectory, "CHAIR_PATCH_MANIFEST.json");
if (File.Exists(outputItemPath) || File.Exists(outputStringPath)) throw new IOException("Refusing to overwrite candidate WZ output.");

var selected = new List<(int id, string name, string stringImage)>();

using (var targetItem = OpenWz(targetItemPath))
using (var targetString = OpenWz(targetStringPath))
using (var donorItem = OpenWz(donorItemPath))
using (var donorString = OpenWz(donorStringPath))
{
    var targetInstall = RequireImage(RequireDirectory(targetItem.WzDirectory, "Install"), "0301.img");
    var donorInstall = RequireImage(RequireDirectory(donorItem.WzDirectory, "Install"), "0301.img");

    var donorCandidates = donorInstall.WzProperties
        .Select(p => (property: p, ok: TryChairId(p.Name, out var id), id))
        .Where(x => x.ok)
        .OrderBy(x => x.id)
        .ToList();

    foreach (var candidate in donorCandidates)
    {
        if (selected.Count >= batchCount) break;
        var id = candidate.id;
        if (FindDirect(targetInstall, id) != null) continue;
        var donorStringEntry = FindStringEntry(donorString, id);
        if (donorStringEntry == null) continue;
        if (FindStringEntry(targetString, id) != null) continue;

        var targetStringImage = targetString.WzDirectory.GetImageByName(donorStringEntry.Value.image.Name);
        if (targetStringImage == null) continue;

        targetInstall.AddProperty(candidate.property.DeepClone());
        targetStringImage.AddProperty(donorStringEntry.Value.property.DeepClone());
        selected.Add((id, ReadName(donorStringEntry.Value.property, id), donorStringEntry.Value.image.Name));
    }

    if (selected.Count < batchCount)
        throw new InvalidOperationException($"Only found {selected.Count} donor-only chair(s) with matching String.wz entries; expected {batchCount}.");

    targetItem.SaveToDisk(outputItemPath);
    targetString.SaveToDisk(outputStringPath);
}

if (Sha256(targetItemPath) != targetItemHashBefore || Sha256(targetStringPath) != targetStringHashBefore)
    throw new InvalidOperationException("Live source WZ files changed during candidate build.");

using (var checkItem = OpenWz(outputItemPath))
using (var checkString = OpenWz(outputStringPath))
{
    var install = RequireImage(RequireDirectory(checkItem.WzDirectory, "Install"), "0301.img");
    foreach (var row in selected)
    {
        if (FindDirect(install, row.id) == null) throw new InvalidDataException($"Patched Item.wz lost chair {row.id}");
        if (FindStringEntry(checkString, row.id) == null) throw new InvalidDataException($"Patched String.wz lost chair strings {row.id}");
    }
}

var manifest = new
{
    schemaVersion = 2,
    kind = "community-chair-batch-candidate",
    requestedCount = batchCount,
    selected = selected.Select(x => new { contentId = x.id, name = x.name, stringImage = x.stringImage }).ToArray(),
    source = new
    {
        itemSha256 = targetItemHashBefore,
        stringSha256 = targetStringHashBefore,
        donorItemSha256 = Sha256(donorItemPath),
        donorStringSha256 = Sha256(donorStringPath)
    },
    output = new
    {
        itemSha256 = Sha256(outputItemPath),
        stringSha256 = Sha256(outputStringPath)
    },
    validation = new { outputReparsed = true, exactSelectedCount = selected.Count == batchCount, sourceUnchanged = true }
};
File.WriteAllText(manifestPath, JsonSerializer.Serialize(manifest, new JsonSerializerOptions { WriteIndented = true }) + Environment.NewLine);
foreach (var row in selected) Console.WriteLine($"Selected chair {row.id}: {row.name}");
Console.WriteLine($"Manifest: {manifestPath}");
return 0;
