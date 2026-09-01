using MapleLib.WzLib;
using MapleLib.WzLib.Serializer;

if (args.Length < 2)
{
    Console.Error.WriteLine("Usage: EverLeafWzExporter <input-directory> <output-directory> [wz-file ...]");
    return 2;
}

var inputDirectory = Path.GetFullPath(args[0]);
var outputDirectory = Path.GetFullPath(args[1]);
var requestedFiles = args.Skip(2).ToArray();

if (!Directory.Exists(inputDirectory))
{
    Console.Error.WriteLine($"Input directory does not exist: {inputDirectory}");
    return 2;
}

Directory.CreateDirectory(outputDirectory);

var files = requestedFiles.Length > 0
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

var serializer = new WzClassicXmlSerializer(2, LineBreak.Windows, false);
var failures = new List<string>();

foreach (var path in files.OrderBy(Path.GetFileName, StringComparer.OrdinalIgnoreCase))
{
    var name = Path.GetFileName(path);
    Console.WriteLine($"[EverLeaf] Parsing {name}");

    try
    {
        using var wzFile = new WzFile(path, WzMapleVersion.GMS);
        var status = wzFile.ParseWzFile();
        if (status != WzFileParseStatus.Success)
        {
            failures.Add($"{name}: parse status {status}");
            Console.Error.WriteLine($"[EverLeaf] Failed to parse {name}: {status}");
            continue;
        }

        var target = Path.Combine(outputDirectory, wzFile.Name);
        Console.WriteLine($"[EverLeaf] Exporting {name} -> {target}");
        serializer.SerializeFile(wzFile, target);
    }
    catch (Exception ex)
    {
        failures.Add($"{name}: {ex.GetType().Name}: {ex.Message}");
        Console.Error.WriteLine($"[EverLeaf] Failed {name}: {ex}");
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
