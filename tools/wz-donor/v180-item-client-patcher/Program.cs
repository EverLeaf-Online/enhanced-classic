using System.Security.Cryptography;
using System.Text.Json;
using MapleLib.WzLib;

if (args.Length != 7)
{
    Console.Error.WriteLine("Usage: EverLeafV180ItemPatcher <target-Item.wz> <target-String.wz> <donor-Item.wz> <donor-String.wz> <items.tsv> <output-dir> <manifest.json>");
    return 2;
}

var targetItemPath = Path.GetFullPath(args[0]);
var targetStringPath = Path.GetFullPath(args[1]);
var donorItemPath = Path.GetFullPath(args[2]);
var donorStringPath = Path.GetFullPath(args[3]);
var listPath = Path.GetFullPath(args[4]);
var outputDir = Path.GetFullPath(args[5]);
var manifestPath = Path.GetFullPath(args[6]);
Directory.CreateDirectory(outputDir);
var outputItemPath = Path.Combine(outputDir, "Item.wz");
var outputStringPath = Path.Combine(outputDir, "String.wz");
if (File.Exists(outputItemPath) || File.Exists(outputStringPath) || File.Exists(manifestPath))
    throw new IOException("Refusing to overwrite existing staging output.");
foreach (var p in new[] { targetItemPath, targetStringPath, donorItemPath, donorStringPath, listPath })
    if (!File.Exists(p)) throw new FileNotFoundException(p);

var requested = File.ReadAllLines(listPath)
    .Select(line => line.Split('\t', StringSplitOptions.TrimEntries))
    .Where(parts => parts.Length == 2 && int.TryParse(parts[1], out _))
    .Select(parts => new ItemRequest(parts[0], int.Parse(parts[1])))
    .Distinct()
    .OrderBy(x => x.Category, StringComparer.OrdinalIgnoreCase)
    .ThenBy(x => x.Id)
    .ToArray();
if (requested.Length == 0) throw new InvalidDataException("No item requests found.");

static string Sha(string path)
{
    using var s = File.OpenRead(path);
    return Convert.ToHexString(SHA256.HashData(s)).ToLowerInvariant();
}

static WzFile OpenTarget(string path)
{
    var wz = new WzFile(path, WzMapleVersion.GMS);
    var st = wz.ParseWzFile();
    if (st != WzFileParseStatus.Success) { wz.Dispose(); throw new InvalidDataException($"Target parse failed {Path.GetFileName(path)}: {st}"); }
    return wz;
}

static WzFile OpenDonor(string path)
{
    if (!File.Exists(Path.Combine(Path.GetDirectoryName(path)!, "ZLZ.dll")))
        throw new FileNotFoundException("v180 donor requires ZLZ.dll beside WZ files.");
    var wz = new WzFile(path, WzMapleVersion.GETFROMZLZ);
    var st = wz.ParseWzFile();
    if (st != WzFileParseStatus.Success) { wz.Dispose(); throw new InvalidDataException($"Donor parse failed {Path.GetFileName(path)}: {st}"); }
    return wz;
}

static WzImageProperty? FindDirect(WzImage image, int id)
{
    foreach (var name in new[] { id.ToString(), id.ToString("D8") })
        if (image[name] is WzImageProperty p) return p;
    return null;
}

static (WzImage image, WzImageProperty property)? FindItemEntry(WzFile wz, string category, int id)
{
    var dir = wz.WzDirectory.GetDirectoryByName(category);
    if (dir == null) return null;
    foreach (var image in dir.WzImages)
    {
        var p = FindDirect(image, id);
        if (p != null) return (image, p);
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

var targetItemHashBefore = Sha(targetItemPath);
var targetStringHashBefore = Sha(targetStringPath);
var donorItemHash = Sha(donorItemPath);
var donorStringHash = Sha(donorStringPath);
var merged = new List<MergedItem>();
var skippedMissingDonorItem = new List<ItemRequest>();
var skippedMissingTargetContainer = new List<ItemRequest>();
var skippedMissingString = new List<ItemRequest>();
var skippedStringContainerMissing = new List<ItemRequest>();
var skippedCollision = new List<ItemRequest>();
short targetItemVersion, targetStringVersion, donorItemVersion, donorStringVersion;

using (var targetItem = OpenTarget(targetItemPath))
using (var targetString = OpenTarget(targetStringPath))
using (var donorItem = OpenDonor(donorItemPath))
using (var donorString = OpenDonor(donorStringPath))
{
    targetItemVersion = targetItem.Version;
    targetStringVersion = targetString.Version;
    donorItemVersion = donorItem.Version;
    donorStringVersion = donorString.Version;

    foreach (var req in requested)
    {
        if (FindItemEntry(targetItem, req.Category, req.Id) != null || FindStringEntry(targetString, req.Id) != null)
        {
            skippedCollision.Add(req);
            continue;
        }

        var donorItemEntry = FindItemEntry(donorItem, req.Category, req.Id);
        if (donorItemEntry == null) { skippedMissingDonorItem.Add(req); continue; }
        var targetCategory = targetItem.WzDirectory.GetDirectoryByName(req.Category);
        var targetImage = targetCategory?.GetImageByName(donorItemEntry.Value.image.Name);
        if (targetImage == null) { skippedMissingTargetContainer.Add(req); continue; }

        var donorStringEntry = FindStringEntry(donorString, req.Id);
        if (donorStringEntry == null) { skippedMissingString.Add(req); continue; }
        var targetStringImage = targetString.WzDirectory.GetImageByName(donorStringEntry.Value.image.Name);
        if (targetStringImage == null) { skippedStringContainerMissing.Add(req); continue; }

        targetImage.AddProperty(donorItemEntry.Value.property.DeepClone());
        targetStringImage.AddProperty(donorStringEntry.Value.property.DeepClone());
        merged.Add(new MergedItem(req.Category, req.Id, donorItemEntry.Value.image.Name, donorStringEntry.Value.image.Name));
    }

    targetItem.SaveToDisk(outputItemPath);
    targetString.SaveToDisk(outputStringPath);
}

if (Sha(targetItemPath) != targetItemHashBefore || Sha(targetStringPath) != targetStringHashBefore)
    throw new InvalidOperationException("Source target WZ changed while staging.");

var verified = 0;
using (var checkItem = OpenTarget(outputItemPath))
using (var checkString = OpenTarget(outputStringPath))
{
    foreach (var row in merged)
    {
        if (FindItemEntry(checkItem, row.Category, row.Id) == null)
            throw new InvalidDataException($"Output Item.wz lost {row.Category}:{row.Id}");
        if (FindStringEntry(checkString, row.Id) == null)
            throw new InvalidDataException($"Output String.wz lost item string {row.Id}");
        verified++;
    }
}

var byCategory = merged.GroupBy(x => x.Category).ToDictionary(g => g.Key, g => g.Count(), StringComparer.OrdinalIgnoreCase);
var manifest = new
{
    schemaVersion = 1,
    kind = "gms-v180-item-node-staging-candidate",
    approved = false,
    productionApplyAllowed = false,
    requestedCount = requested.Length,
    mergedCount = merged.Count,
    verifiedCount = verified,
    mergedByCategory = byCategory,
    skipped = new
    {
        collision = skippedCollision.Count,
        missingDonorItem = skippedMissingDonorItem.Count,
        missingTargetContainer = skippedMissingTargetContainer.Count,
        missingDonorString = skippedMissingString.Count,
        missingTargetStringContainer = skippedStringContainerMissing.Count,
    },
    source = new
    {
        item = new { sha256 = targetItemHashBefore, version = targetItemVersion, size = new FileInfo(targetItemPath).Length },
        @string = new { sha256 = targetStringHashBefore, version = targetStringVersion, size = new FileInfo(targetStringPath).Length },
    },
    donor = new
    {
        item = new { sha256 = donorItemHash, version = donorItemVersion, size = new FileInfo(donorItemPath).Length },
        @string = new { sha256 = donorStringHash, version = donorStringVersion, size = new FileInfo(donorStringPath).Length },
    },
    output = new
    {
        item = new { sha256 = Sha(outputItemPath), size = new FileInfo(outputItemPath).Length },
        @string = new { sha256 = Sha(outputStringPath), size = new FileInfo(outputStringPath).Length },
    },
    validation = new
    {
        sourceUnchanged = true,
        outputsReparsed = true,
        allMergedNodesVerified = verified == merged.Count,
        productionApplyAllowed = false,
    },
    missingTargetContainer = skippedMissingTargetContainer.Take(500).ToArray(),
    missingTargetStringContainer = skippedStringContainerMissing.Take(500).ToArray(),
};
File.WriteAllText(manifestPath, JsonSerializer.Serialize(manifest, new JsonSerializerOptions { WriteIndented = true }) + Environment.NewLine);
Console.WriteLine($"REQUESTED={requested.Length:N0}");
Console.WriteLine($"MERGED={merged.Count:N0} VERIFIED={verified:N0}");
foreach (var kv in byCategory.OrderBy(x => x.Key)) Console.WriteLine($"{kv.Key}={kv.Value:N0}");
Console.WriteLine($"SKIP_COLLISION={skippedCollision.Count:N0}");
Console.WriteLine($"SKIP_MISSING_TARGET_CONTAINER={skippedMissingTargetContainer.Count:N0}");
Console.WriteLine($"SKIP_MISSING_STRING={skippedMissingString.Count:N0}");
Console.WriteLine($"SKIP_MISSING_TARGET_STRING_CONTAINER={skippedStringContainerMissing.Count:N0}");
Console.WriteLine("approved=false / productionApplyAllowed=false");
return 0;

internal readonly record struct ItemRequest(string Category, int Id);
internal readonly record struct MergedItem(string Category, int Id, string ItemImage, string StringImage);
