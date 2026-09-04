using System.Security.Cryptography;
using System.Text.Json;
using MapleLib.WzLib;
using MapleLib.WzLib.WzProperties;

if (args.Length != 5)
{
    Console.Error.WriteLine("Usage: EverLeafQuestBaselinePatcher <target-Quest.wz> <target-String.wz> <donor-Quest.wz> <donor-String.wz> <output-dir>");
    return 2;
}

var targetQuest = Path.GetFullPath(args[0]);
var targetString = Path.GetFullPath(args[1]);
var donorQuest = Path.GetFullPath(args[2]);
var donorString = Path.GetFullPath(args[3]);
var outputDir = Path.GetFullPath(args[4]);
var questIds = Enumerable.Range(8163, 9).ToArray();

foreach (var p in new[] { targetQuest, targetString, donorQuest, donorString })
    if (!File.Exists(p)) throw new FileNotFoundException(p);
Directory.CreateDirectory(outputDir);
foreach (var name in new[] { "Quest.wz", "String.wz" })
    if (File.Exists(Path.Combine(outputDir, name))) throw new IOException($"Refusing existing output {name}");

static string Sha(string p)
{
    using var s = File.OpenRead(p);
    return Convert.ToHexString(SHA256.HashData(s)).ToLowerInvariant();
}

static WzFile OpenTarget(string p)
{
    var w = new WzFile(p, WzMapleVersion.GMS);
    var st = w.ParseWzFile();
    if (st != WzFileParseStatus.Success) { w.Dispose(); throw new InvalidDataException($"Target parse failed {Path.GetFileName(p)}: {st}"); }
    return w;
}

static WzFile OpenDonor(string p)
{
    var w = new WzFile(p, 95, WzMapleVersion.GMS);
    var st = w.ParseWzFile();
    if (st != WzFileParseStatus.Success) { w.Dispose(); throw new InvalidDataException($"Donor parse failed {Path.GetFileName(p)}: {st}"); }
    return w;
}

static bool SameId(string? name, int id) => name != null && int.TryParse(name, out var n) && n == id;

static (WzImageProperty prop, List<string> parents)? FindProp(WzImage img, int id)
{
    (WzImageProperty, List<string>)? Walk(IEnumerable<WzImageProperty> props, List<string> path)
    {
        foreach (var p in props)
        {
            if (SameId(p.Name, id)) return (p, path);
            if (p.WzProperties != null)
            {
                var hit = Walk(p.WzProperties, new List<string>(path) { p.Name });
                if (hit != null) return hit;
            }
        }
        return null;
    }
    return Walk(img.WzProperties, new List<string>());
}

static IPropertyContainer EnsureParents(WzImage img, IEnumerable<string> path)
{
    IPropertyContainer cur = img;
    foreach (var name in path)
    {
        var p = cur[name];
        if (p == null)
        {
            p = new WzSubProperty(name);
            cur.AddProperty(p);
        }
        if (p is not IPropertyContainer pc) throw new InvalidDataException($"Quest parent {name} is not a container");
        cur = pc;
    }
    return cur;
}

static WzImage RequireImage(WzFile w, string name) =>
    w.WzDirectory.GetImageByName(name) ?? throw new InvalidDataException($"Missing {name}");

static string MergeQuestNode(WzImage target, WzImage donor, int id, string label)
{
    var source = FindProp(donor, id) ?? throw new InvalidDataException($"Donor {label} missing quest {id}");
    var existing = FindProp(target, id);
    var action = "add";
    if (existing != null)
    {
        existing.Value.prop.Remove();
        action = "replace";
    }
    var parent = EnsureParents(target, source.Value.parents);
    parent.AddProperty(source.Value.prop.DeepClone());
    return action;
}

var beforeQuest = Sha(targetQuest);
var beforeString = Sha(targetString);
var donorQuestHash = Sha(donorQuest);
var donorStringHash = Sha(donorString);
var changes = new List<object>();

using (var tq = OpenTarget(targetQuest))
using (var dq = OpenDonor(donorQuest))
{
    foreach (var imageName in new[] { "Check.img", "Act.img", "QuestInfo.img" })
    {
        var ti = RequireImage(tq, imageName);
        var di = RequireImage(dq, imageName);
        foreach (var id in questIds)
        {
            var action = MergeQuestNode(ti, di, id, $"Quest.wz/{imageName}");
            changes.Add(new { family = "Quest.wz", image = imageName, questId = id, action });
        }
    }
    tq.SaveToDisk(Path.Combine(outputDir, "Quest.wz"));
}

using (var ts = OpenTarget(targetString))
using (var ds = OpenDonor(donorString))
{
    var ti = RequireImage(ts, "Quest.img");
    var di = RequireImage(ds, "Quest.img");
    foreach (var id in questIds)
    {
        var donorHit = FindProp(di, id);
        if (donorHit == null) continue; // Quest.wz is authoritative; strings are optional but copied when available.
        var action = MergeQuestNode(ti, di, id, "String.wz/Quest.img");
        changes.Add(new { family = "String.wz", image = "Quest.img", questId = id, action });
    }
    ts.SaveToDisk(Path.Combine(outputDir, "String.wz"));
}

if (Sha(targetQuest) != beforeQuest || Sha(targetString) != beforeString)
    throw new InvalidOperationException("Source client WZ changed while building quest baseline candidate");

// Reparse and require all nine quest nodes from all three Quest.wz components.
using (var q = OpenTarget(Path.Combine(outputDir, "Quest.wz")))
{
    foreach (var imageName in new[] { "Check.img", "Act.img", "QuestInfo.img" })
    {
        var img = RequireImage(q, imageName);
        foreach (var id in questIds)
            if (FindProp(img, id) == null) throw new InvalidDataException($"Reparsed output missing {imageName}:{id}");
    }
}
using (OpenTarget(Path.Combine(outputDir, "String.wz"))) { }

var manifest = new
{
    schemaVersion = 1,
    kind = "canonical-v95-quest-baseline-normalization",
    questIds,
    source = new { QuestWzSha256 = beforeQuest, StringWzSha256 = beforeString },
    donor = new { QuestWzSha256 = donorQuestHash, StringWzSha256 = donorStringHash, version = "GMS v95" },
    output = new
    {
        QuestWzSha256 = Sha(Path.Combine(outputDir, "Quest.wz")),
        StringWzSha256 = Sha(Path.Combine(outputDir, "String.wz"))
    },
    changes,
    validation = new { sourceUnchanged = true, outputReparsed = true, allQuestComponentsPresent = true }
};
File.WriteAllText(Path.Combine(outputDir, "QUEST_BASELINE_MANIFEST.json"), JsonSerializer.Serialize(manifest, new JsonSerializerOptions { WriteIndented = true }) + Environment.NewLine);
Console.WriteLine($"Canonical v95 quest baseline candidate built for quests {string.Join(',', questIds)}");
return 0;
