using System.Security.Cryptography;
using System.Text.Json;
using MapleLib.WzLib;
using MapleLib.WzLib.WzProperties;

if (args.Length != 2)
{
    Console.Error.WriteLine("Usage: RateCouponProgram <target-Etc.wz> <output-directory>");
    return 2;
}

var targetPath = Path.GetFullPath(args[0]);
var outputDirectory = Path.GetFullPath(args[1]);
Directory.CreateDirectory(outputDirectory);
if (!File.Exists(targetPath)) throw new FileNotFoundException(targetPath);

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

static bool IsRateCoupon(int itemId)
{
    var itemType = itemId / 1000;
    return itemType == 5211 || itemType == 5360;
}

var sourceHash = Sha256(targetPath);
var outputPath = Path.Combine(outputDirectory, "Etc.wz");
var manifestPath = Path.Combine(outputDirectory, "RATE_COUPON_PATCH_MANIFEST.json");
if (File.Exists(outputPath)) throw new IOException("Refusing to overwrite candidate Etc.wz output.");

var disabled = new List<(int sn, int itemId)>();

using (var target = OpenWz(targetPath))
{
    var commodity = target.WzDirectory.GetImageByName("Commodity.img")
        ?? throw new InvalidDataException("Missing Commodity.img");
    commodity.ParseImage();

    foreach (var entry in commodity.WzProperties)
    {
        var itemIdProp = entry["ItemId"];
        if (itemIdProp == null) continue;
        var itemId = itemIdProp.GetInt();
        if (!IsRateCoupon(itemId)) continue;

        var onSale = entry["OnSale"];
        if (onSale is WzIntProperty onSaleInt)
        {
            if (onSaleInt.Value != 0)
            {
                onSaleInt.Value = 0;
                commodity.Changed = true;
            }
        }
        else if (onSale != null)
        {
            throw new InvalidDataException($"Unexpected OnSale property type for SN {entry.Name}, item {itemId}: {onSale.GetType().Name}");
        }

        if (!int.TryParse(entry.Name, out var sn))
            throw new InvalidDataException($"Invalid Commodity SN name: {entry.Name}");
        disabled.Add((sn, itemId));
    }

    if (disabled.Count == 0)
        throw new InvalidOperationException("No EXP/drop rate coupons were found in Commodity.img; refusing no-op patch.");

    target.SaveToDisk(outputPath);
}

if (Sha256(targetPath) != sourceHash)
    throw new InvalidOperationException("Live source Etc.wz changed during candidate build.");

using (var check = OpenWz(outputPath))
{
    var commodity = check.WzDirectory.GetImageByName("Commodity.img")
        ?? throw new InvalidDataException("Patched Etc.wz lost Commodity.img");
    commodity.ParseImage();
    foreach (var entry in commodity.WzProperties)
    {
        var itemIdProp = entry["ItemId"];
        if (itemIdProp == null) continue;
        var itemId = itemIdProp.GetInt();
        if (!IsRateCoupon(itemId)) continue;
        var onSale = entry["OnSale"];
        if (onSale != null && onSale.GetInt() != 0)
            throw new InvalidDataException($"Rate coupon still on sale after patch: SN {entry.Name}, item {itemId}");
    }
}

var manifest = new
{
    schemaVersion = 1,
    kind = "everleaf-disable-rate-coupons",
    policy = new { itemTypes = new[] { 5211, 5360 }, effect = "OnSale=0-or-absent" },
    disabled = disabled.OrderBy(x => x.sn).Select(x => new { sn = x.sn, itemId = x.itemId }).ToArray(),
    source = new { etcSha256 = sourceHash },
    output = new { etcSha256 = Sha256(outputPath) },
    validation = new { outputReparsed = true, disabledCount = disabled.Count }
};
File.WriteAllText(manifestPath, JsonSerializer.Serialize(manifest, new JsonSerializerOptions { WriteIndented = true }) + Environment.NewLine);
Console.WriteLine($"Disabled {disabled.Count} EXP/drop rate coupon commodity entries.");
Console.WriteLine($"Manifest: {manifestPath}");
return 0;