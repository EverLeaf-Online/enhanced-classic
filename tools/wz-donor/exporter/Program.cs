using MapleLib.WzLib;
using MapleLib.WzLib.Serializer;

if (args.Length < 2)
{
    Console.Error.WriteLine("Usage: EverLeafWzExporter <input-directory> <output-directory> [--patch-version=N] [--probe-patch-range=MIN:MAX] [--try-zlz] [wz-file ...]");
    return 2;
}

var inputDirectory = Path.GetFullPath(args[0]);
var outputDirectory = Path.GetFullPath(args[1]);
short patchVersion = -1;
(short Min, short Max)? probePatchRange = null;
bool tryZlz = false;
var requestedFiles = new List<string>();

foreach (var arg in args.Skip(2))
{
    const string patchPrefix = "--patch-version=";
    const string probePrefix = "--probe-patch-range=";

    if (arg.StartsWith(patchPrefix, StringComparison.OrdinalIgnoreCase))
    {
        var raw = arg[patchPrefix.Length..];
        if (!short.TryParse(raw, out patchVersion) || patchVersion < 0)
        {
            Console.Error.WriteLine($"Invalid patch version: {raw}");
            return 2;
        }
        continue;
    }

    if (arg.StartsWith(probePrefix, StringComparison.OrdinalIgnoreCase))
    {
        var raw = arg[probePrefix.Length..];
        var parts = raw.Split(':', 2);
        if (parts.Length != 2 ||
            !short.TryParse(parts[0], out var minVersion) ||
            !short.TryParse(parts[1], out var maxVersion) ||
            minVersion < 0 || maxVersion < minVersion)
        {
            Console.Error.WriteLine($"Invalid patch probe range: {raw}");
            return 2;
        }
        probePatchRange = (minVersion, maxVersion);
        continue;
    }

    if (string.Equals(arg, "--try-zlz", StringComparison.OrdinalIgnoreCase))
    {
        tryZlz = true;
        continue;
    }

    requestedFiles.Add(arg);
}

if (probePatchRange is not null && patchVersion < 0)
{
    Console.Error.WriteLine("--probe-patch-range requires --patch-version as the preferred version");
    return 2;
}

if (tryZlz && !File.Exists(Path.Combine(inputDirectory, "ZLZ.dll")))
{
    Console.Error.WriteLine($"--try-zlz requires ZLZ.dll beside the donor WZ files: {inputDirectory}");
    return 2;
}

if (!Directory.Exists(inputDirectory))
{
    Console.Error.WriteLine($"Input directory does not exist: {inputDirectory}");
    return 2;
}

Directory.CreateDirectory(outputDirectory);

var files = requestedFiles.Count > 0
    ? requestedFiles.Select(name => Path.Combine(inputDirectory, name)).ToArray()
    : Directory.GetFiles(inputDirectory, "*.wz", SearchOption.TopDirectoryOnly);

if (files.Length == 0)
{
    Console.Error.WriteLine("No WZ files selected.");
    return 2;
}

foreach (var path in files)
{
    if (!File.Exists(path))
    {
        Console.Error.WriteLine($"Missing WZ file: {path}");
        return 2;
    }
}

static bool HasPlausibleRootNames(WzFile wzFile, out string summary)
{
    var names = wzFile.WzDirectory.WzDirectories.Select(directory => directory.Name)
        .Concat(wzFile.WzDirectory.WzImages.Select(image => image.Name))
        .Where(name => !string.IsNullOrEmpty(name))
        .ToArray();

    if (names.Length == 0)
    {
        summary = "root has no named directories or images";
        return false;
    }

    var totalCharacters = names.Sum(name => name.Length);
    var recognizedCharacters = names.Sum(name => name.Count(character => character >= 0x20 && character <= 0x7e));
    var printableRatio = totalCharacters == 0 ? 0.0 : (double)recognizedCharacters / totalCharacters;
    var imageNamesPlausible = wzFile.WzDirectory.WzImages.All(image => image.Name.EndsWith(".img", StringComparison.OrdinalIgnoreCase));

    summary = $"rootEntries={names.Length}, printableRatio={printableRatio:F3}, imageNamesPlausible={imageNamesPlausible}";
    return printableRatio >= 0.90 && imageNamesPlausible;
}

static WzFile? ValidateParsed(WzFile wzFile, WzFileParseStatus status, out string detail)
{
    if (status != WzFileParseStatus.Success)
    {
        detail = $"parse status {status}";
        wzFile.Dispose();
        return null;
    }

    if (!HasPlausibleRootNames(wzFile, out var plausibility))
    {
        detail = $"parsed but failed plausibility check ({plausibility})";
        wzFile.Dispose();
        return null;
    }

    detail = $"success ({plausibility})";
    return wzFile;
}

static WzFile? TryParseVersion(string path, short version, out string detail)
{
    WzFile? wzFile = null;
    try
    {
        wzFile = new WzFile(path, version, WzMapleVersion.GMS);
        return ValidateParsed(wzFile, wzFile.ParseWzFile(), out detail);
    }
    catch (Exception ex)
    {
        detail = $"{ex.GetType().Name}: {ex.Message}";
        wzFile?.Dispose();
        return null;
    }
}

static WzFile? TryParseZlz(string path, out string detail)
{
    WzFile? wzFile = null;
    try
    {
        wzFile = new WzFile(path, WzMapleVersion.GETFROMZLZ);
        return ValidateParsed(wzFile, wzFile.ParseWzFile(), out detail);
    }
    catch (Exception ex)
    {
        detail = $"{ex.GetType().Name}: {ex.Message}";
        wzFile?.Dispose();
        return null;
    }
}

static IEnumerable<short> ProbeOrder(short preferred, (short Min, short Max) range)
{
    return Enumerable.Range(range.Min, range.Max - range.Min + 1)
        .Select(value => (short)value)
        .Where(value => value != preferred)
        .OrderBy(value => Math.Abs(value - preferred))
        .ThenBy(value => value);
}

var serializer = new WzClassicXmlSerializer(2, LineBreak.Windows, false);
var failures = new List<string>();

Console.WriteLine(patchVersion >= 0
    ? $"[EverLeaf] Using preferred MapleStory patch version {patchVersion}"
    : "[EverLeaf] Using MapleLib patch-version auto-detection");
if (probePatchRange is { } range)
    Console.WriteLine($"[EverLeaf] Bounded fallback patch probe enabled: {range.Min}:{range.Max}");
if (tryZlz)
    Console.WriteLine("[EverLeaf] Exact-client ZLZ key fallback enabled");

foreach (var path in files.OrderBy(Path.GetFileName, StringComparer.OrdinalIgnoreCase))
{
    var name = Path.GetFileName(path);
    Console.WriteLine($"[EverLeaf] Parsing {name}");

    WzFile? wzFile = null;
    string selectedMode = "unknown";
    string failureDetail = "unknown parse failure";

    if (patchVersion >= 0)
    {
        wzFile = TryParseVersion(path, patchVersion, out failureDetail);
        if (wzFile is not null)
        {
            selectedMode = $"patch {patchVersion}";
        }
        else if (probePatchRange is { } probeRange)
        {
            Console.WriteLine($"[EverLeaf] Preferred patch {patchVersion} failed for {name}: {failureDetail}");
            foreach (var candidate in ProbeOrder(patchVersion, probeRange))
            {
                wzFile = TryParseVersion(path, candidate, out var candidateDetail);
                Console.WriteLine($"[EverLeaf] Probe {name} patch {candidate}: {candidateDetail}");
                if (wzFile is null)
                {
                    failureDetail = $"patch {candidate}: {candidateDetail}";
                    continue;
                }

                selectedMode = $"patch {candidate}";
                break;
            }
        }
    }
    else
    {
        try
        {
            wzFile = new WzFile(path, WzMapleVersion.GMS);
            wzFile = ValidateParsed(wzFile, wzFile.ParseWzFile(), out failureDetail);
            if (wzFile is not null)
                selectedMode = $"auto-detected patch {wzFile.Version}";
        }
        catch (Exception ex)
        {
            failureDetail = $"{ex.GetType().Name}: {ex.Message}";
            wzFile?.Dispose();
            wzFile = null;
        }
    }

    if (wzFile is null && tryZlz)
    {
        wzFile = TryParseZlz(path, out var zlzDetail);
        Console.WriteLine($"[EverLeaf] ZLZ fallback {name}: {zlzDetail}");
        if (wzFile is not null)
            selectedMode = $"ZLZ key, detected patch {wzFile.Version}";
        else
            failureDetail = $"ZLZ fallback: {zlzDetail}";
    }

    if (wzFile is null)
    {
        failures.Add($"{name}: {failureDetail}");
        Console.Error.WriteLine($"[EverLeaf] Failed {name}: {failureDetail}");
        continue;
    }

    using (wzFile)
    {
        var target = Path.Combine(outputDirectory, wzFile.Name);
        Console.WriteLine($"[EverLeaf] Exporting {name} using {selectedMode} -> {target}");
        try
        {
            serializer.SerializeFile(wzFile, target);
        }
        catch (Exception ex)
        {
            failures.Add($"{name}: serialization {ex.GetType().Name}: {ex.Message}");
            Console.Error.WriteLine($"[EverLeaf] Failed to serialize {name}: {ex}");
        }
    }
}

if (failures.Count > 0)
{
    Console.Error.WriteLine("[EverLeaf] Export failures:");
    foreach (var failure in failures)
        Console.Error.WriteLine($"  - {failure}");
    return 1;
}

var xmlCount = Directory.EnumerateFiles(outputDirectory, "*.xml", SearchOption.AllDirectories).Count();
Console.WriteLine($"[EverLeaf] Export complete: {xmlCount:N0} XML files");
return xmlCount > 0 ? 0 : 1;
