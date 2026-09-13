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
    var donorStatus3 = RequireImage(donor, "StatusBar3.img");

    // The v83 executable still resolves StatusBar.img paths, so adapt the complete
    // later HUD into those runtime paths rather than layering the old v83 HUD over it.
    ReplaceProperty(targetStatus, "base/backgrnd", donorStatus2, "mainBar/backgrnd", p => SetCanvasOrigin((WzCanvasProperty)p, 0, 14), changes);
    ReplaceProperty(targetStatus, "base/quickSlot", donorStatus3, "mainBar/quickSlot/backgrnd", p => SetCanvasOrigin((WzCanvasProperty)p, 0, 0), changes);

    // Replace the old v83 gauge chrome with StatusBar2 gauge chrome.  The v83
    // HP/MP/EXP calculations remain the data source; only presentation is replaced.
    ReplaceProperty(targetStatus, "gauge/graduation", donorStatus2, "mainBar/gaugeBackgrd", p => SetCanvasOrigin((WzCanvasProperty)p, 0, 0), changes);
    ReplaceProperty(targetStatus, "gauge/bar", donorStatus2, "mainBar/gaugeCover", p => SetCanvasOrigin((WzCanvasProperty)p, 0, 0), changes);

    // Main controls retain their proven v83 command IDs while using later-client art.
    ReplaceProperty(targetStatus, "BtShop", donorStatus2, "starPlanet/BtCashShop", p => NormalizeButtonOrigins(p), changes);
    ReplaceProperty(targetStatus, "BtNPT", donorStatus2, "mainBar/BtMTS", p => NormalizeButtonOrigins(p), changes);
    ReplaceProperty(targetStatus, "BtMenu", donorStatus2, "starPlanet/BtMenu", p => NormalizeButtonOrigins(p), changes);
    ReplaceProperty(targetStatus, "BtShort", donorStatus2, "starPlanet/BtSystem", p => NormalizeButtonOrigins(p), changes);

    // Replace the old Equip/Item/Stat/Skill/Key buttons instead of leaving a v83
    // control strip beside the modern quickslot panel.
    ReplaceProperty(targetStatus, "EquipKey", donorStatus2, "mainBar/BtEquip", p => NormalizeButtonOrigins(p), changes);
    ReplaceProperty(targetStatus, "InvenKey", donorStatus2, "mainBar/BtInven", p => NormalizeButtonOrigins(p), changes);
    ReplaceProperty(targetStatus, "StatKey", donorStatus2, "mainBar/BtStat", p => NormalizeButtonOrigins(p), changes);
    ReplaceProperty(targetStatus, "SkillKey", donorStatus2, "mainBar/BtSkill", p => NormalizeButtonOrigins(p), changes);
    ReplaceProperty(targetStatus, "KeySet", donorStatus2, "mainBar/BtKeysetting", p => NormalizeButtonOrigins(p), changes);

    // The native client patch expands v83 from 8 to 26 quickslots.  These controls
    // now use the StatusBar3 extend/fold treatment around the 557x67 modern panel.
    ReplaceProperty(targetStatus, "QuickSlot", donorStatus3, "mainBar/quickSlot/button:Extend", p => NormalizeButtonOrigins(p), changes);
    ReplaceProperty(targetStatus, "QuickSlotD", donorStatus3, "mainBar/quickSlot/button:Fold", p => NormalizeButtonOrigins(p), changes);

    // BtNPT retains EverLeaf's TRADE -> Free Market command behavior underneath.
    target.SaveToDisk(outputPath);
}

if (Sha(targetPath) != targetBefore) throw new InvalidOperationException("Source UI.wz changed while building statusbar adapter.");

using (var output = OpenTarget(outputPath))
{
    var status = RequireImage(output, "StatusBar.img");
    foreach (var path in new[] {
        "base/backgrnd", "base/quickSlot", "gauge/graduation", "gauge/bar",
        "BtShop", "BtMenu", "BtShort", "BtNPT",
        "EquipKey", "InvenKey", "StatKey", "SkillKey", "KeySet", "QuickSlot", "QuickSlotD"
    }) _ = RequireProperty(status, path);
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
        legacyV83HudVisualsReplaced = true,
        statusBar2GaugeChrome = true,
        statusBar2MainControls = new[] { "SHOP", "TRADE", "MENU", "SYSTEM", "EQUIP", "ITEM", "STAT", "SKILL", "KEYSETTING" },
        modernTradeButton = true,
        tradeButtonRuntimeBehavior = "EverLeaf TRADE-to-Free-Market warp unchanged",
        statusBar3ExpandedQuickSlotPanel = true,
        quickSlotCount = 26,
        quickSlotLayout = "13x2",
        v83HpMpExpBehaviorPreserved = true,
        nativeRuntimeExpansionRequired = true
    },
    validation = new { sourceUnchanged = true, outputReparsed = true, requiredRuntimePathsPresent = true, nonEmptyCandidate = true }
};
File.WriteAllText(manifestPath, JsonSerializer.Serialize(manifest, new JsonSerializerOptions { WriteIndented = true }) + Environment.NewLine);
Console.WriteLine($"STATUSBAR_ADAPTER_OK changes={changes.Count} sha256={outputSha}");
return 0;
