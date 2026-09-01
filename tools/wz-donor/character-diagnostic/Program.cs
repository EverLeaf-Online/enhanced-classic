using MapleLib.WzLib;
using MapleLib.WzLib.Util;
using System.Security.Cryptography;

if (args.Length != 1)
{
    Console.Error.WriteLine("Usage: EverLeafCharacterDiagnostic <directory-containing-Character.wz-and-ZLZ.dll>");
    return 2;
}

var root = Path.GetFullPath(args[0]);
var characterPath = Path.Combine(root, "Character.wz");
var zlzPath = Path.Combine(root, "ZLZ.dll");
if (!File.Exists(characterPath) || !File.Exists(zlzPath))
{
    Console.Error.WriteLine($"Expected Character.wz and ZLZ.dll in {root}");
    return 2;
}

static string Sha256(string path)
{
    using var stream = File.OpenRead(path);
    return Convert.ToHexString(SHA256.HashData(stream)).ToLowerInvariant();
}

static bool Plausible(WzFile wz, out string detail)
{
    var names = wz.WzDirectory.WzDirectories.Select(d => d.Name)
        .Concat(wz.WzDirectory.WzImages.Select(i => i.Name))
        .Where(n => !string.IsNullOrEmpty(n))
        .ToArray();
    if (names.Length == 0)
    {
        detail = "no root names";
        return false;
    }

    var chars = names.Sum(n => n.Length);
    var printable = names.Sum(n => n.Count(c => c >= 0x20 && c <= 0x7e));
    var ratio = chars == 0 ? 0d : (double)printable / chars;
    var imageNames = wz.WzDirectory.WzImages.All(i => i.Name.EndsWith(".img", StringComparison.OrdinalIgnoreCase));
    detail = $"dirs={wz.WzDirectory.WzDirectories.Count} images={wz.WzDirectory.WzImages.Count} printable={ratio:F3} imageNames={imageNames}";
    return ratio >= 0.90 && imageNames;
}

static bool Try(string path, short? patch, WzMapleVersion locale, out string detail)
{
    WzFile? wz = null;
    try
    {
        wz = patch is null ? new WzFile(path, locale) : new WzFile(path, patch.Value, locale);
        var status = wz.ParseWzFile();
        if (status != WzFileParseStatus.Success)
        {
            detail = $"status={status}";
            return false;
        }
        var ok = Plausible(wz, out var plausibility);
        detail = $"status={status} detectedPatch={wz.Version} plausible={ok} {plausibility}";
        return ok;
    }
    catch (Exception ex)
    {
        detail = $"{ex.GetType().Name}: {ex.Message}";
        return false;
    }
    finally
    {
        wz?.Dispose();
    }
}

Console.WriteLine($"Character.wz bytes={new FileInfo(characterPath).Length} sha256={Sha256(characterPath)}");
Console.WriteLine($"ZLZ.dll bytes={new FileInfo(zlzPath).Length} sha256={Sha256(zlzPath)}");
Console.WriteLine($"Header={Convert.ToHexString(File.ReadAllBytes(characterPath).Take(64).ToArray())}");

try
{
    var detected = WzTool.DetectMapleVersion(characterPath, out var detectedPatch);
    Console.WriteLine($"WzTool.DetectMapleVersion => locale={detected} patch={detectedPatch}");
}
catch (Exception ex)
{
    Console.WriteLine($"WzTool.DetectMapleVersion => {ex.GetType().Name}: {ex.Message}");
}

var locales = new[]
{
    WzMapleVersion.GMS,
    WzMapleVersion.EMS,
    WzMapleVersion.BMS,
    WzMapleVersion.GETFROMZLZ,
};

var success = false;
foreach (var locale in locales)
{
    if (Try(characterPath, 95, locale, out var explicit95))
        success = true;
    Console.WriteLine($"explicit patch=95 locale={locale}: {explicit95}");

    if (Try(characterPath, null, locale, out var auto))
        success = true;
    Console.WriteLine($"auto patch locale={locale}: {auto}");
}

// If the exact client key is correct but the encoded patch hash differs,
// probe only ZLZ+patch combinations here. This is a 6.8 MB diagnostic file,
// so the bounded search is cheap and does not re-transfer the full donor.
for (short patch = 0; patch <= 250 && !success; patch++)
{
    if (patch == 95)
        continue;
    if (!Try(characterPath, patch, WzMapleVersion.GETFROMZLZ, out var detail))
        continue;
    Console.WriteLine($"SUCCESS ZLZ patch={patch}: {detail}");
    success = true;
}

Console.WriteLine(success ? "Character diagnostic found a plausible parse." : "Character diagnostic found no plausible parse in tested modes.");
return success ? 0 : 1;
