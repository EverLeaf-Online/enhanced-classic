using System.Security.Cryptography;
using System.Text.Json;
using MapleLib.WzLib;

if (args.Length != 5)
{
    Console.Error.WriteLine("Usage: EverLeafClientWzPatcher <target-Item.wz> <target-String.wz> <donor-Item.wz> <donor-String.wz> <output-directory>");
    return 2;
}

var targetItemPath = Path.GetFullPath(args[0]);
var targetStringPath = Path.GetFullPath(args[1]);
var donorItemPath = Path.GetFullPath(args[2]);
var donorStringPath = Path.GetFullPath(args[3]);
var outputDirectory = Path.GetFullPath(args[4]);

foreach (var path in new[] { targetItemPath, targetStringPath, donorItemPath, donorStringPath })
{
    if (!File.Exists(path))
    {
        Console.Error.WriteLine($"Missing WZ file: {path}");
        return 2;
    }
}

Directory.CreateDirectory(outputDirectory);
var outputItemPath = Path.Combine(outputDirectory, "Item.wz");
var outputStringPath = Path.Combine(outputDirectory, "String.wz");
var manifestPath = Path.Combine(outputDirectory, "CLIENT_PATCH_MANIFEST.json");

if (File.Exists(outputItemPath) || File.Exists(outputStringPath))
{
    Console.Error.WriteLine("Refusing to overwrite an existing client WZ candidate.");
    return 2;
}

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
        throw new InvalidDataException($"Failed to parse {Path.GetFileName(path)}: {status}");
    }
    return wz;
}

static WzImage RequireImage(WzDirectory directory, string imageName, string description)
{
    return directory.GetImageByName(imageName)
        ?? throw new InvalidDataException($"Missing {description} image {imageName}");
}

static WzDirectory RequireDirectory(WzDirectory directory, string directoryName, string description)
{
    return directory.GetDirectoryByName(directoryName)
        ?? throw new InvalidDataException($"Missing {description} directory {directoryName}");
}

static WzImageProperty RequireProperty(WzImage image, IEnumerable<string> names, string description)
{
    foreach (var name in names)
    {
        var property = image[name];
        if (property is not null)
            return property;
    }
    throw new InvalidDataException($"Missing {description}; tried {string.Join(", ", names)}");
}

static WzImageProperty RequireChild(WzImageProperty property, string childName, string description)
{
    return property[childName]
        ?? throw new InvalidDataException($"Missing {description} child {childName}");
}

static int? OptionalInt(WzImageProperty property, string childName)
{
    return property[childName]?.GetInt();
}

static bool HasAnyProperty(WzImage image, IEnumerable<string> names)
{
    return names.Any(name => image[name] is not null);
}

var ids = new[] { 2022711, 2022712 };
var targetItemHashBefore = Sha256(targetItemPath);
var targetStringHashBefore = Sha256(targetStringPath);
var donorItemHash = Sha256(donorItemPath);
var donorStringHash = Sha256(donorStringPath);

short targetItemVersion;
short targetStringVersion;
short donorItemVersion;
short donorStringVersion;

using (var targetItem = OpenWz(targetItemPath))
using (var targetString = OpenWz(targetStringPath))
using (var donorItem = OpenWz(donorItemPath))
using (var donorString = OpenWz(donorStringPath))
{
    targetItemVersion = targetItem.Version;
    targetStringVersion = targetString.Version;
    donorItemVersion = donorItem.Version;
    donorStringVersion = donorString.Version;

    var targetConsumeDirectory = RequireDirectory(targetItem.WzDirectory, "Consume", "target Item.wz");
    var donorConsumeDirectory = RequireDirectory(donorItem.WzDirectory, "Consume", "donor Item.wz");
    var targetItemImage = RequireImage(targetConsumeDirectory, "0202.img", "target Item.wz Consume");
    var donorItemImage = RequireImage(donorConsumeDirectory, "0202.img", "donor Item.wz Consume");
    var targetStringImage = RequireImage(targetString.WzDirectory, "Consume.img", "target String.wz");
    var donorStringImage = RequireImage(donorString.WzDirectory, "Consume.img", "donor String.wz");

    foreach (var id in ids)
    {
        var itemNames = new[] { id.ToString("D8"), id.ToString() };
        var stringNames = new[] { id.ToString() };

        if (HasAnyProperty(targetItemImage, itemNames))
            throw new InvalidOperationException($"Target Item.wz already contains item {id}; refusing collision.");
        if (HasAnyProperty(targetStringImage, stringNames))
            throw new InvalidOperationException($"Target String.wz already contains item {id}; refusing collision.");

        var donorItemProperty = RequireProperty(donorItemImage, itemNames, $"donor Item.wz item {id}");
        var donorStringProperty = RequireProperty(donorStringImage, stringNames, $"donor String.wz item {id}");

        targetItemImage.AddProperty(donorItemProperty.DeepClone());
        targetStringImage.AddProperty(donorStringProperty.DeepClone());
    }

    targetItem.SaveToDisk(outputItemPath);
    targetString.SaveToDisk(outputStringPath);
}

if (Sha256(targetItemPath) != targetItemHashBefore || Sha256(targetStringPath) != targetStringHashBefore)
    throw new InvalidOperationException("Source EverLeaf client WZ changed while building candidate.");

var semantics = new List<ClientSemantic>();
using (var checkItem = OpenWz(outputItemPath))
using (var checkString = OpenWz(outputStringPath))
{
    var checkConsumeDirectory = RequireDirectory(checkItem.WzDirectory, "Consume", "patched Item.wz");
    var checkItemImage = RequireImage(checkConsumeDirectory, "0202.img", "patched Item.wz Consume");
    var checkStringImage = RequireImage(checkString.WzDirectory, "Consume.img", "patched String.wz");

    foreach (var id in ids)
    {
        var itemNames = new[] { id.ToString("D8"), id.ToString() };
        var item = RequireProperty(checkItemImage, itemNames, $"patched Item.wz item {id}");
        var strings = checkStringImage[id.ToString()]
            ?? throw new InvalidDataException($"Patched String.wz lost item {id} after save/reparse.");
        var info = RequireChild(item, "info", $"patched Item.wz item {id}");
        var spec = RequireChild(item, "spec", $"patched Item.wz item {id}");
        var icon = RequireChild(info, "icon", $"patched Item.wz item {id} info");
        var iconRaw = RequireChild(info, "iconRaw", $"patched Item.wz item {id} info");
        var name = RequireChild(strings, "name", $"patched String.wz item {id}").GetString();
        var description = strings["desc"]?.GetString() ?? string.Empty;
        var hp = OptionalInt(spec, "hp") ?? 0;
        var mp = OptionalInt(spec, "mp") ?? 0;
        var price = OptionalInt(info, "price");
        var slotMax = OptionalInt(info, "slotMax") ?? OptionalInt(info, "slotmax");

        if (string.IsNullOrWhiteSpace(name))
            throw new InvalidDataException($"Patched String.wz item {id} has no usable name.");
        if (!icon.GetType().Name.Contains("Canvas", StringComparison.OrdinalIgnoreCase) ||
            !iconRaw.GetType().Name.Contains("Canvas", StringComparison.OrdinalIgnoreCase))
            throw new InvalidDataException($"Patched item {id} did not preserve canvas icon properties.");

        semantics.Add(new ClientSemantic(
            id,
            name,
            description,
            hp,
            mp,
            price,
            slotMax,
            icon.GetType().Name,
            iconRaw.GetType().Name));
    }
}

var manifest = new
{
    schemaVersion = 2,
    kind = "isolated-client-wz-candidate",
    batchId = "gms-v95-consume-batch-001",
    candidateIds = ids,
    approved = false,
    productionApplyAllowed = false,
    sourceClient = new
    {
        item = new { sha256 = targetItemHashBefore, version = targetItemVersion, size = new FileInfo(targetItemPath).Length },
        @string = new { sha256 = targetStringHashBefore, version = targetStringVersion, size = new FileInfo(targetStringPath).Length }
    },
    donor = new
    {
        item = new { sha256 = donorItemHash, version = donorItemVersion, size = new FileInfo(donorItemPath).Length },
        @string = new { sha256 = donorStringHash, version = donorStringVersion, size = new FileInfo(donorStringPath).Length }
    },
    output = new
    {
        item = new { sha256 = Sha256(outputItemPath), size = new FileInfo(outputItemPath).Length },
        @string = new { sha256 = Sha256(outputStringPath), size = new FileInfo(outputStringPath).Length }
    },
    semantics,
    validation = new
    {
        sourceClientUnchanged = true,
        outputReparsed = true,
        exactCandidateIds = true,
        donorNodesDeepCloned = true,
        iconCanvasesPreserved = true,
        semanticValuesReadAfterReparse = true
    }
};

File.WriteAllText(manifestPath, JsonSerializer.Serialize(manifest, new JsonSerializerOptions { WriteIndented = true }) + Environment.NewLine);
Console.WriteLine($"Client WZ candidate built for IDs: {string.Join(", ", ids)}");
Console.WriteLine($"Target versions: Item={targetItemVersion}, String={targetStringVersion}");
Console.WriteLine($"Donor versions: Item={donorItemVersion}, String={donorStringVersion}");
foreach (var semantic in semantics)
    Console.WriteLine($"Client semantic {semantic.ContentId}: {semantic.Name}; hp={semantic.Hp}; mp={semantic.Mp}; price={semantic.Price?.ToString() ?? "<none>"}; slotMax={semantic.SlotMax?.ToString() ?? "<none>"}");
Console.WriteLine("approved=false / productionApplyAllowed=false");
Console.WriteLine($"Manifest: {manifestPath}");
return 0;

internal sealed record ClientSemantic(
    int ContentId,
    string Name,
    string Description,
    int Hp,
    int Mp,
    int? Price,
    int? SlotMax,
    string IconPropertyType,
    string IconRawPropertyType);
