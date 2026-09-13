using System.Security.Cryptography;
using System.Text.Json;
using MapleLib.WzLib;
using MapleLib.WzLib.WzProperties;

if (args.Length != 4)
{
    Console.Error.WriteLine("Usage: EverLeafV180StatusBarAdapter <target-ui.wz> <donor-ui.wz> <output-ui.wz> <manifest.json>");
    return 2;
}

var targetPath = Path.GetFullPath(args[0]);
var donorPath = Path.GetFullPath(args[1]);
var outputPath = Path.GetFullPath(args[2]);
var manifestPath = Path.GetFullPath(args[3]);
foreach (var p in new[] { targetPath, donorPath }) if (!File.Exists(p)) throw new FileNotFoundException(p);
if (File.Exists(outputPath) || File.Exists(manifestPath)) throw new IOException("Refusing to overwrite statusbar adapter output.");
Directory.CreateDirectory(Path.GetDirectoryName(outputPath)!);
Directory.CreateDirectory(Path.GetDirectoryName(manifestPath)!);

static string Sha(string p)
{
    using var s = File.OpenRead(p);
    return Convert.ToHexString(SHA256.HashData(s)).ToLowerInvariant();
}

static WzFile OpenTarget(string p)
{
    var w = new WzFile(p, WzMapleVersion.GMS);
    var st = w.ParseWzFile();
    if (st != WzFileParseStatus.Success) { w.Dispose(); throw new InvalidDataException($"Target UI parse failed: {st}"); }
    return w;
}

static WzFile OpenDonor(string p)
{
    var w = new WzFile(p, WzMapleVersion.BMS);
    var st = w.ParseWzFile();
    if (st != WzFileParseStatus.Success) { w.Dispose(); throw new InvalidDataException($"Donor UI parse failed with BMS key: {st}"); }
    return w;
}

static WzImage RequireImage(WzFile w, string name)
{
    var image = w.WzDirectory.GetImageByName(name) ?? throw new InvalidDataException($"Missing {name}");
    if (!image.Parsed) image.ParseImage();
    return image;
}

static WzImageProperty RequireProperty(WzImage image, string path)
    => image.GetFromPath(path) as WzImageProperty ?? throw new InvalidDataException($"Missing {image.Name}/{path}");

static IPropertyContainer RequireParent(WzImage image, string path, out string leaf)
{
    var parts = path.Split('/', StringSplitOptions.RemoveEmptyEntries);
    if (parts.Length == 0) throw new InvalidDataException($"Invalid property path: {path}");
    leaf = parts[^1];
    IPropertyContainer current = image;
    for (var i = 0; i < parts.Length - 1; i++)
    {
        var next = current[parts[i]] as IPropertyContainer
            ?? throw new InvalidDataException($"Missing target property parent: {image.Name}/{string.Join('/', parts.Take(i + 1))}");
        current = next;
    }
    return current;
}

static void SetCanvasOrigin(WzCanvasProperty canvas, int x, int y)
{
    var old = canvas[WzCanvasProperty.OriginPropertyName];
    if (old != null) canvas.RemoveProperty(old);
    canvas.AddProperty(new WzVectorProperty(WzCanvasProperty.OriginPropertyName, x, y));
}

static void NormalizeButtonOrigins(WzImageProperty property)
{
    if (property is WzCanvasProperty canvas) SetCanvasOrigin(canvas, 0, 0);
    if (property.WzProperties == null) return;
    foreach (var child in property.WzProperties.ToArray()) NormalizeButtonOrigins(child);
}

static void ReplaceProperty(WzImage targetImage, string targetPath, WzImage donorImage, string donorPath, Action<WzImageProperty>? mutate, List<object> changes)
{
    var donorProperty = RequireProperty(donorImage, donorPath);
    var parent = RequireParent(targetImage, targetPath, out var leaf);
    var existing = parent[leaf] ?? throw new InvalidDataException($"Target property missing: {targetImage.Name}/{targetPath}");
    var clone = donorProperty.DeepClone();
    clone.Name = leaf;
    mutate?.Invoke(clone);
    parent.RemoveProperty(existing);
    parent.AddProperty(clone);
    changes.Add(new { target = $"{targetImage.Name}/{targetPath}", donor = $"{donorImage.Name}/{donorPath}" });
}

var targetBefore = Sha(targetPath);
var donorSha = Sha(donorPath);
var changes = new List<object>();
short targetVersion, donorVersion;

using (var target = OpenTarget(targetPath))
using (var donor = OpenDonor(donorPath))
{
    targetVersion = target.Version;
    donorVersion = donor.Version;
    var targetStatus = RequireImage(target, "StatusBar.img");
    var donorStatus2 = RequireImage(donor, "StatusBar2.img");

    ReplaceProperty(targetStatus, "base/backgrnd", donorStatus2, "mainBar/backgrnd", p => SetCanvasOrigin((WzCanvasProperty)p, 0, 14), changes);
    ReplaceProperty(targetStatus, "base/quickSlot", donorStatus2, "mainBar/quickSlot/quickSlot", p => SetCanvasOrigin((WzCanvasProperty)p, 0, 13), changes);

    // Keep the four v83 controls on one later-client generation.  The previous
    // mixed StatusBar2/StatusBar3 row left 34px controls inside 54px v83 slots,
    // which created the uneven gaps visible in-game.  These StatusBar2 assets are
    // the native 55/56x35 row, so they fit the existing v83 control/hitbox spacing.
    ReplaceProperty(targetStatus, "BtShop", donorStatus2, "starPlanet/BtCashShop", p => NormalizeButtonOrigins(p), changes);
    ReplaceProperty(targetStatus, "BtNPT", donorStatus2, "mainBar/BtMTS", p => NormalizeButtonOrigins(p), changes);
    ReplaceProperty(targetStatus, "BtMenu", donorStatus2, "starPlanet/BtMenu", p => NormalizeButtonOrigins(p), changes);
    ReplaceProperty(targetStatus, "BtShort", donorStatus2, "starPlanet/BtSystem", p => NormalizeButtonOrigins(p), changes);

    // BtNPT keeps the existing TRADE -> Free Market runtime behavior.  HP/MP/EXP
    // and v83 shortcut behavior stay untouched while the visible main row is now
    // internally consistent with the StatusBar2 HUD shell.
    target.SaveToDisk(outputPath);
}

if (Sha(targetPath) != targetBefore) throw new InvalidOperationException("Source UI.wz changed while building statusbar adapter.");

using (var output = OpenTarget(outputPath))
{
    var status = RequireImage(output, "StatusBar.img");
    foreach (var path in new[] { "base/backgrnd", "base/quickSlot", "BtShop", "BtMenu", "BtShort", "BtNPT", "gauge" })
        _ = RequireProperty(status, path);
}

var outputSha = Sha(outputPath);
var manifest = new
{
    schemaVersion = 1,
    kind = "everleaf-v180-statusbar2-3-v83-adapter",
    approved = false,
    productionApplyAllowed = false,
    source = new { path = targetPath, sha256 = targetBefore, size = new FileInfo(targetPath).Length, version = targetVersion },
    donor = new { path = donorPath, sha256 = donorSha, size = new FileInfo(donorPath).Length, version = donorVersion, cryptoKey = "BMS" },
    output = new { path = outputPath, sha256 = outputSha, size = new FileInfo(outputPath).Length },
    changes,
    behavior = new
    {
        fullWidthStatusBar2Background = true,
        statusBar2MainControls = new[] { "SHOP", "TRADE", "MENU", "SYSTEM/SHORTCUT" },
        consistentMainControlWidth = true,
        modernTradeButton = true,
        tradeButtonRuntimeBehavior = "EverLeaf TRADE-to-Free-Market warp unchanged",
        modernQuickSlotTray = true,
        v83HpMpExpBehaviorPreserved = true,
        v83CompactShortcutBehaviorPreserved = true
    },
    validation = new { sourceUnchanged = true, outputReparsed = true, requiredRuntimePathsPresent = true, nonEmptyCandidate = true }
};
File.WriteAllText(manifestPath, JsonSerializer.Serialize(manifest, new JsonSerializerOptions { WriteIndented = true }) + Environment.NewLine);
Console.WriteLine($"STATUSBAR_ADAPTER_OK changes={changes.Count} sha256={outputSha}");
return 0;
