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
    // WzComparerR2 independently auto-detects this GMS v180 archive as
    // BMS-keyed PKG1 data. GETFROMZLZ decodes the directory table incorrectly.
    var wz = new WzFile(path, WzMapleVersion.BMS);
    var st = wz.ParseWzFile();
    if (st != WzFileParseStatus.Success) { wz.Dispose(); throw new InvalidDataException($"Donor parse failed {Path.GetFileName(path)} with BMS key: {st}"); }
    return wz;
}

static WzImageProperty? FindDirect(WzImage image, int id)
{
    foreach (var name in new[] { id.ToString(), id.ToString("D8") })
        if (image[name] is WzImageProperty p) return p;
    return null;
}

static IEnumerable<ImageLocation> EnumerateImages(WzDirectory dir, string[] prefix)
{
    foreach (var image in dir.WzImages)
        yield return new ImageLocation(image, prefix);
    foreach (var sub in dir.WzDirectories)
    {
        var next = prefix.Concat(new[] { sub.Name }).ToArray();
        foreach (var row in EnumerateImages(sub, next)) yield return row;
    }
}

static WzDirectory EnsureDirectoryPath(WzDirectory root, IEnumerable<string> dirs)
{
    var cur = root;
    foreach (var name in dirs)
    {
        var next = cur.GetDirectoryByName(name);
        if (next == null) { next = new WzDirectory(name); cur.AddDirectory(next); }
        cur = next;
    }
    return cur;
}

static ItemLocation? FindItemEntry(WzFile wz, string category, int id)
{
    var categoryDir = wz.WzDirectory.GetDirectoryByName(category);
    if (categoryDir == null) return null;
    foreach (var row in EnumerateImages(categoryDir, Array.Empty<string>()))
    {
        var p = FindDirect(row.Image, id);
        if (p != null) return new ItemLocation(row.Image, p, row.Dirs);
    }
    return null;
}

static ItemLocation? FindStringEntry(WzFile wz, int id)
{
    foreach (var row in EnumerateImages(wz.WzDirectory, Array.Empty<string>()))
    {
        var p = FindDirect(row.Image, id);
        if (p != null) return new ItemLocation(row.Image, p, row.Dirs);
    }
    return null;
}

static WzImage GetOrCreateImage(WzDirectory root, IEnumerable<string> dirs, string imageName, HashSet<string> created, string family)
{
    var dir = EnsureDirectoryPath(root, dirs);
    var image = dir.GetImageByName(imageName);
    if (image != null) return image;
    image = new WzImage(imageName);
    dir.AddImage(image);
    created.Add($"{family}:{string.Join('/', dirs.Append(imageName))}");
    return image;
}

var targetItemHashBefore = Sha(targetItemPath);
var targetStringHashBefore = Sha(targetStringPath);
var donorItemHash = Sha(donorItemPath);
var donorStringHash = Sha(donorStringPath);
var merged = new List<MergedItem>();
var missingDonorItem = new List<ItemRequest>();
var missingDonorString = new List<ItemRequest>();
var existingItemCollision = new List<ItemRequest>();
var createdContainers = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
var reusedExistingStrings = 0;
var copiedDonorStrings = 0;
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
        // The TSV is donor-only by Item.wz inventory. Treat only an existing
        // target Item.wz node as a collision; an existing String.wz row is useful
        // and should be reused rather than blocking the item import.
        if (FindItemEntry(targetItem, req.Category, req.Id) != null)
        {
            existingItemCollision.Add(req);
            continue;
        }

        var donorItemEntry = FindItemEntry(donorItem, req.Category, req.Id);
        if (donorItemEntry == null) { missingDonorItem.Add(req); continue; }

        var category = targetItem.WzDirectory.GetDirectoryByName(req.Category);
        if (category == null)
        {
            category = new WzDirectory(req.Category);
            targetItem.WzDirectory.AddDirectory(category);
            createdContainers.Add($"Item:{req.Category}/");
        }
        var targetItemImage = GetOrCreateImage(category, donorItemEntry.Value.Dirs, donorItemEntry.Value.Image.Name, createdContainers, "Item");
        targetItemImage.AddProperty(donorItemEntry.Value.Property.DeepClone());

        var targetStringEntry = FindStringEntry(targetString, req.Id);
        var donorStringEntry = FindStringEntry(donorString, req.Id);
        var hasString = false;
        string? stringImage = null;
        if (targetStringEntry != null)
        {
            reusedExistingStrings++;
            hasString = true;
            stringImage = string.Join('/', targetStringEntry.Value.Dirs.Append(targetStringEntry.Value.Image.Name));
        }
        else if (donorStringEntry != null)
        {
            var targetStringImage = GetOrCreateImage(targetString.WzDirectory, donorStringEntry.Value.Dirs, donorStringEntry.Value.Image.Name, createdContainers, "String");
            targetStringImage.AddProperty(donorStringEntry.Value.Property.DeepClone());
            copiedDonorStrings++;
            hasString = true;
            stringImage = string.Join('/', donorStringEntry.Value.Dirs.Append(donorStringEntry.Value.Image.Name));
        }
        else
        {
            missingDonorString.Add(req);
        }

        merged.Add(new MergedItem(
            req.Category,
            req.Id,
            string.Join('/', donorItemEntry.Value.Dirs.Append(donorItemEntry.Value.Image.Name)),
            stringImage,
            hasString));
    }

    if (merged.Count == 0)
        throw new InvalidOperationException("No donor-only items merged; refusing false-success candidate.");
    if (missingDonorItem.Count != 0)
        throw new InvalidOperationException($"Donor inventory mismatch: {missingDonorItem.Count} requested item nodes were not found in donor binary.");

    targetItem.SaveToDisk(outputItemPath);
    targetString.SaveToDisk(outputStringPath);
}

if (Sha(targetItemPath) != targetItemHashBefore || Sha(targetStringPath) != targetStringHashBefore)
    throw new InvalidOperationException("Source target WZ changed while staging.");

var verifiedItems = 0;
var verifiedStrings = 0;
using (var checkItem = OpenTarget(outputItemPath))
using (var checkString = OpenTarget(outputStringPath))
{
    foreach (var row in merged)
    {
        if (FindItemEntry(checkItem, row.Category, row.Id) == null)
            throw new InvalidDataException($"Output Item.wz lost {row.Category}:{row.Id}");
        verifiedItems++;
        if (row.HasString)
        {
            if (FindStringEntry(checkString, row.Id) == null)
                throw new InvalidDataException($"Output String.wz lost item string {row.Id}");
            verifiedStrings++;
        }
    }
}

var byCategory = merged.GroupBy(x => x.Category).ToDictionary(g => g.Key, g => g.Count(), StringComparer.OrdinalIgnoreCase);
var manifest = new
{
    schemaVersion = 5,
    kind = "gms-v180-item-node-staging-candidate",
    approved = false,
    productionApplyAllowed = false,
    requestedCount = requested.Length,
    mergedCount = merged.Count,
    verifiedItemCount = verifiedItems,
    verifiedStringCount = verifiedStrings,
    mergedByCategory = byCategory,
    donorCryptoKey = "BMS",
    strings = new
    {
        copiedFromDonor = copiedDonorStrings,
        reusedFromTarget = reusedExistingStrings,
        missingInDonorAndTarget = missingDonorString.Count,
    },
    containers = new { createdCount = createdContainers.Count, created = createdContainers.OrderBy(x => x).ToArray() },
    skipped = new
    {
        existingItemCollision = existingItemCollision.Count,
        missingDonorItem = missingDonorItem.Count,
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
        allMergedItemNodesVerified = verifiedItems == merged.Count,
        allExpectedStringsVerified = verifiedStrings == merged.Count(x => x.HasString),
        fullRequestedItemCoverage = merged.Count + existingItemCollision.Count == requested.Length,
        nonEmptyCandidate = merged.Count > 0,
        productionApplyAllowed = false,
    },
    missingStringItems = missingDonorString.ToArray(),
    collisions = existingItemCollision.Take(500).ToArray(),
};
File.WriteAllText(manifestPath, JsonSerializer.Serialize(manifest, new JsonSerializerOptions { WriteIndented = true }) + Environment.NewLine);
Console.WriteLine($"REQUESTED={requested.Length:N0}");
Console.WriteLine($"MERGED={merged.Count:N0} VERIFIED_ITEMS={verifiedItems:N0}");
foreach (var kv in byCategory.OrderBy(x => x.Key)) Console.WriteLine($"{kv.Key}={kv.Value:N0}");
Console.WriteLine($"STRINGS_DONOR={copiedDonorStrings:N0} STRINGS_REUSED={reusedExistingStrings:N0} STRINGS_MISSING={missingDonorString.Count:N0}");
Console.WriteLine($"CREATED_CONTAINERS={createdContainers.Count:N0}");
Console.WriteLine($"ITEM_COLLISIONS={existingItemCollision.Count:N0} MISSING_DONOR_ITEMS={missingDonorItem.Count:N0}");
Console.WriteLine("approved=false / productionApplyAllowed=false");
return 0;

internal readonly record struct ItemRequest(string Category, int Id);
internal readonly record struct ImageLocation(WzImage Image, string[] Dirs);
internal readonly record struct ItemLocation(WzImage Image, WzImageProperty Property, string[] Dirs);
internal readonly record struct MergedItem(string Category, int Id, string ItemImage, string? StringImage, bool HasString);
