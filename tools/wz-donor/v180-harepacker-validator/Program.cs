using System.Security.Cryptography;
using System.Text.Json;
using System.Xml.Linq;
using MapleLib.WzLib;
using MapleLib.WzLib.Serializer;
using MapleLib.WzLib.Util;

if (args.Length != 3)
{
    Console.Error.WriteLine("Usage: EverLeafV180HaRepackerValidator <candidate.wz> <xml-output-dir> <manifest.json>");
    return 2;
}

var candidatePath = Path.GetFullPath(args[0]);
var xmlRoot = Path.GetFullPath(args[1]);
var manifestPath = Path.GetFullPath(args[2]);
if (!File.Exists(candidatePath)) throw new FileNotFoundException(candidatePath);
if (Directory.Exists(xmlRoot)) throw new IOException($"Refusing to overwrite XML directory: {xmlRoot}");
if (File.Exists(manifestPath)) throw new IOException($"Refusing to overwrite manifest: {manifestPath}");
Directory.CreateDirectory(xmlRoot);
Directory.CreateDirectory(Path.GetDirectoryName(manifestPath)!);

static string Sha(string path)
{
    using var stream = File.OpenRead(path);
    return Convert.ToHexString(SHA256.HashData(stream)).ToLowerInvariant();
}

static IEnumerable<WzImage> EnumerateImages(WzDirectory dir)
{
    foreach (var image in dir.WzImages) yield return image;
    foreach (var child in dir.WzDirectories)
        foreach (var image in EnumerateImages(child))
            yield return image;
}

var detectedVersion = WzTool.DetectMapleVersion(candidatePath, out var detectedWzVersion);
var file = new WzFile(candidatePath, WzMapleVersion.GMS);
var parseStatus = file.ParseWzFile();
if (parseStatus != WzFileParseStatus.Success)
{
    file.Dispose();
    throw new InvalidDataException($"HaRepacker/MapleLib parse failed for {Path.GetFileName(candidatePath)}: {parseStatus}");
}

var images = EnumerateImages(file.WzDirectory).ToArray();
var parsedImages = 0;
var imageParseFailures = new List<object>();
foreach (var image in images)
{
    try
    {
        if (!image.Parsed) image.ParseImage();
        _ = image.WzProperties.Count;
        parsedImages++;
    }
    catch (Exception ex)
    {
        imageParseFailures.Add(new { image = image.FullPath, error = ex.GetType().Name, message = ex.Message });
    }
}
if (imageParseFailures.Count != 0)
{
    file.Dispose();
    throw new InvalidDataException($"HaRepacker image parse failures in {Path.GetFileName(candidatePath)}: {imageParseFailures.Count}");
}

// HaRepacker's "Private server" export is the classic per-image XML shape
// without embedded canvas/sound payloads. This matches the XML structure used
// by EverLeaf's v83 server-side WZ provider.
var serializer = new WzClassicXmlSerializer(2, LineBreak.Unix, false);
serializer.SerializeFile(file, xmlRoot);
file.Dispose();

var xmlFiles = Directory.EnumerateFiles(xmlRoot, "*.xml", SearchOption.AllDirectories).OrderBy(x => x, StringComparer.OrdinalIgnoreCase).ToArray();
var malformed = new List<object>();
foreach (var xml in xmlFiles)
{
    try
    {
        using var stream = File.OpenRead(xml);
        _ = XDocument.Load(stream, LoadOptions.None);
    }
    catch (Exception ex)
    {
        malformed.Add(new { path = Path.GetRelativePath(xmlRoot, xml).Replace('\\', '/'), error = ex.GetType().Name, message = ex.Message });
    }
}
if (xmlFiles.Length != images.Length)
    throw new InvalidDataException($"Private-server XML count mismatch for {Path.GetFileName(candidatePath)}: images={images.Length}, xml={xmlFiles.Length}");
if (malformed.Count != 0)
    throw new InvalidDataException($"Malformed private-server XML files for {Path.GetFileName(candidatePath)}: {malformed.Count}");

var manifest = new
{
    schemaVersion = 1,
    kind = "everleaf-v180-harepacker-resurrected-validation",
    approved = false,
    productionApplyAllowed = false,
    harepackerCommit = "4d7fcecbdff0767e333a34d47cbf331caa16416a",
    candidate = new
    {
        path = candidatePath,
        file = Path.GetFileName(candidatePath),
        sha256 = Sha(candidatePath),
        size = new FileInfo(candidatePath).Length,
        detectedMapleVersion = detectedVersion.ToString(),
        detectedWzVersion,
        parsedAs = WzMapleVersion.GMS.ToString()
    },
    validation = new
    {
        wzParseStatus = parseStatus.ToString(),
        imageCount = images.Length,
        parsedImageCount = parsedImages,
        imageParseFailureCount = imageParseFailures.Count,
        privateServerXmlCount = xmlFiles.Length,
        malformedXmlCount = malformed.Count,
        imageAndXmlCountsMatch = xmlFiles.Length == images.Length,
        allImagesParsed = parsedImages == images.Length,
        allXmlWellFormed = malformed.Count == 0
    },
    privateServerXml = new
    {
        format = "WzClassicXmlSerializer",
        indentation = 2,
        lineBreak = "Unix",
        embeddedCanvasAndSoundPayloads = false
    }
};
File.WriteAllText(manifestPath, JsonSerializer.Serialize(manifest, new JsonSerializerOptions { WriteIndented = true }) + Environment.NewLine);
Console.WriteLine($"HAREPACKER_OK {Path.GetFileName(candidatePath)} images={images.Length:N0} xml={xmlFiles.Length:N0}");
Console.WriteLine($"MANIFEST {manifestPath}");
return 0;
