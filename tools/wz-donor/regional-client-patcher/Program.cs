using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using MapleLib.WzLib;
using MapleLib.WzLib.WzProperties;

if (args.Length != 4)
{
    Console.Error.WriteLine("Usage: EverLeafRegionalClientWzPatcher <contract.json> <target-wz-dir> <donor-wz-dir> <output-dir>");
    return 2;
}

var contractPath=Path.GetFullPath(args[0]); var targetDir=Path.GetFullPath(args[1]); var donorDir=Path.GetFullPath(args[2]); var outputDir=Path.GetFullPath(args[3]);
var families=new[]{"Map.wz","Mob.wz","Npc.wz","Item.wz","Quest.wz","String.wz"};
foreach(var family in families) foreach(var root in new[]{targetDir,donorDir}) if(!File.Exists(Path.Combine(root,family))) throw new FileNotFoundException($"Missing {family} in {root}");
Directory.CreateDirectory(outputDir); foreach(var family in families) if(File.Exists(Path.Combine(outputDir,family))) throw new IOException($"Refusing existing candidate {family}");
using var contractDoc=JsonDocument.Parse(File.ReadAllText(contractPath)); var c=contractDoc.RootElement;
foreach(var flag in new[]{"approved","importAllowed","automaticImport","productionApplyAllowed"}) if(c.TryGetProperty(flag,out var fv) && fv.ValueKind!=JsonValueKind.False) throw new InvalidDataException($"{flag} must remain false");
static int[] Ints(JsonElement e,string name)=>e.GetProperty(name).EnumerateArray().Select(x=>x.GetInt32()).ToArray();
var maps=Ints(c,"maps"); var mobs=Ints(c,"mobs"); var npcs=Ints(c,"castleNpcs"); var items=Ints(c,"items"); var quests=Ints(c,"questIds");
var replaceNpc=new HashSet<int>(c.GetProperty("deliberateReplacementCollisions").EnumerateArray().Select(x=>int.Parse(x.GetProperty("contentId").GetString()!)));
static string Sha(string p){using var s=File.OpenRead(p);return Convert.ToHexString(SHA256.HashData(s)).ToLowerInvariant();}
static WzFile OpenTarget(string p){var w=new WzFile(p,WzMapleVersion.GMS);var st=w.ParseWzFile();if(st!=WzFileParseStatus.Success){w.Dispose();throw new InvalidDataException($"Target parse failed {Path.GetFileName(p)}: {st}");}return w;}
static WzFile OpenDonor(string p){var w=new WzFile(p,95,WzMapleVersion.GMS);var st=w.ParseWzFile();if(st!=WzFileParseStatus.Success){w.Dispose();throw new InvalidDataException($"Donor parse failed {Path.GetFileName(p)}: {st}");}return w;}
static (WzImage image,List<string> dirs)? FindImage(WzDirectory root,string name){
    (WzImage,List<string>)? Walk(WzDirectory d,List<string> path){var i=d.GetImageByName(name);if(i!=null)return(i,path);foreach(var sd in d.WzDirectories){var r=Walk(sd,new List<string>(path){sd.Name});if(r!=null)return r;}return null;}
    return Walk(root,new List<string>());
}
static WzDirectory EnsureDirs(WzDirectory root,IEnumerable<string> dirs){var d=root;foreach(var n in dirs){var next=d.GetDirectoryByName(n);if(next==null){next=new WzDirectory(n);d.AddDirectory(next);}d=next;}return d;}
static void CopyImage(WzFile target,WzFile donor,int id,bool allowReplace,List<object> changes){var name=id+".img";var ds=FindImage(donor.WzDirectory,name)??throw new InvalidDataException($"Donor missing {name}");var ts=FindImage(target.WzDirectory,name);string action;
    if(ts!=null){if(!allowReplace)throw new InvalidOperationException($"Unexpected target collision {name}");ts.Value.image.Remove();action="replace";}else action="add";
    var parent=EnsureDirs(target.WzDirectory,ds.Value.dirs);parent.AddImage(ds.Value.image.DeepClone());changes.Add(new{contentId=id,action,directory=string.Join("/",ds.Value.dirs)});
}
static bool SameId(string? name,int id)=>name!=null&&int.TryParse(name,out var v)&&v==id;
static (WzImageProperty prop,List<string> parents)? FindProp(WzImage img,int id){
    (WzImageProperty,List<string>)? Walk(IEnumerable<WzImageProperty> ps,List<string> path){foreach(var p in ps){if(SameId(p.Name,id))return(p,path);if(p.WzProperties!=null){var r=Walk(p.WzProperties,new List<string>(path){p.Name});if(r!=null)return r;}}return null;}
    return Walk(img.WzProperties,new List<string>());
}
static IPropertyContainer EnsurePropParents(WzImage img,IEnumerable<string> path){IPropertyContainer cur=img;foreach(var n in path){var p=cur[n];if(p==null){p=new WzSubProperty(n);cur.AddProperty(p);}if(p is not IPropertyContainer pc)throw new InvalidDataException($"Parent path {n} is not a container");cur=pc;}return cur;}
static WzImage RequireImage(WzFile w,string name)=>w.WzDirectory.GetImageByName(name)??throw new InvalidDataException($"Missing image {name}");
static void MergeProp(WzImage target,WzImage donor,int id,bool replace,List<object> changes,string label){var hit=FindProp(donor,id)??throw new InvalidDataException($"Donor {label} missing {id}");var existing=FindProp(target,id);string action;if(existing!=null){if(!replace)throw new InvalidOperationException($"Unexpected {label} collision {id}");existing.Value.prop.Remove();action="replace";}else action="add";var parent=EnsurePropParents(target,hit.Value.parents);parent.AddProperty(hit.Value.prop.DeepClone());changes.Add(new{contentId=id,action,parent=string.Join("/",hit.Value.parents)});}
static (WzImage image,string imageName) FindItem(WzFile w,int id){var etc=w.WzDirectory.GetDirectoryByName("Etc")??throw new InvalidDataException("Item.wz missing Etc");var hits=new List<(WzImage,string)>();foreach(var img in etc.WzImages)if(FindProp(img,id)!=null)hits.Add((img,img.Name));if(hits.Count!=1)throw new InvalidDataException($"Expected one Item.wz container for {id}, got {hits.Count}");return hits[0];}
static void HashText(IncrementalHash h,string s){h.AppendData(Encoding.UTF8.GetBytes(s));h.AppendData(new byte[]{0});}
static string ImageDigest(WzImage img){using var h=IncrementalHash.CreateHash(HashAlgorithmName.SHA256);HashText(h,img.Name);void Walk(IEnumerable<WzImageProperty> ps){foreach(var p in ps){HashText(h,p.Name);HashText(h,p.PropertyType.ToString());if(p is WzCanvasProperty canvas){h.AppendData(canvas.PngProperty.GetCompressedBytesForExtraction(false));}else if(p.WzProperties==null){try{HashText(h,p.GetString()??"");}catch{HashText(h,p.WzValue?.ToString()??"");}}if(p.WzProperties!=null)Walk(p.WzProperties);}}Walk(img.WzProperties);return Convert.ToHexString(h.GetHashAndReset()).ToLowerInvariant();}

var before=families.ToDictionary(x=>x,x=>Sha(Path.Combine(targetDir,x))); var donorHashes=families.ToDictionary(x=>x,x=>Sha(Path.Combine(donorDir,x))); var versions=new Dictionary<string,object>(); var fullChanges=new Dictionary<string,List<object>>(); var nodeChanges=new Dictionary<string,List<object>>();
foreach(var family in families){using var t=OpenTarget(Path.Combine(targetDir,family));using var d=OpenDonor(Path.Combine(donorDir,family));versions[family]=new{target=t.Version,donor=d.Version};var fc=new List<object>();var nc=new List<object>();
    if(family=="Map.wz")foreach(var id in maps)CopyImage(t,d,id,false,fc);
    if(family=="Mob.wz")foreach(var id in mobs)CopyImage(t,d,id,false,fc);
    if(family=="Npc.wz")foreach(var id in npcs)CopyImage(t,d,id,replaceNpc.Contains(id),fc);
    if(family=="Item.wz")foreach(var id in items){var di=FindItem(d,id);var ti=t.WzDirectory.GetDirectoryByName("Etc")?.GetImageByName(di.imageName)??throw new InvalidDataException($"Target Item.wz missing {di.imageName}");MergeProp(ti,di.image,id,false,nc,"Item.wz");}
    if(family=="Quest.wz")foreach(var imageName in new[]{"Check.img","Act.img","QuestInfo.img"}){var ti=RequireImage(t,imageName);var di=RequireImage(d,imageName);foreach(var id in quests)MergeProp(ti,di,id,false,nc,$"Quest.wz/{imageName}");}
    if(family=="String.wz")foreach(var spec in new[]{("Etc.img",items,new HashSet<int>()),("Map.img",maps,new HashSet<int>()),("Mob.img",mobs,new HashSet<int>()),("Npc.img",npcs,replaceNpc)}){var ti=RequireImage(t,spec.Item1);var di=RequireImage(d,spec.Item1);foreach(var id in spec.Item2)MergeProp(ti,di,id,spec.Item3.Contains(id),nc,$"String.wz/{spec.Item1}");}
    t.SaveToDisk(Path.Combine(outputDir,family));fullChanges[family]=fc;nodeChanges[family]=nc;
}
foreach(var family in families)if(Sha(Path.Combine(targetDir,family))!=before[family])throw new InvalidOperationException($"Live source copy changed while patching: {family}");
var digestEvidence=new List<object>();foreach(var family in new[]{("Map.wz",maps),("Mob.wz",mobs),("Npc.wz",npcs)}){using var donor=OpenDonor(Path.Combine(donorDir,family.Item1));using var output=OpenTarget(Path.Combine(outputDir,family.Item1));foreach(var id in family.Item2){var name=id+".img";var di=FindImage(donor.WzDirectory,name)??throw new InvalidDataException($"Donor validation missing {name}");var oi=FindImage(output.WzDirectory,name)??throw new InvalidDataException($"Output validation missing {name}");var dd=ImageDigest(di.Value.image);var od=ImageDigest(oi.Value.image);if(dd!=od)throw new InvalidDataException($"Reparsed image digest mismatch {family.Item1}:{id}");digestEvidence.Add(new{family=family.Item1,contentId=id,donorDigest=dd,outputDigest=od});}}
foreach(var family in new[]{"Item.wz","Quest.wz","String.wz"})using(OpenTarget(Path.Combine(outputDir,family))){}
var manifest=new{schemaVersion=1,kind="isolated-regional-client-wz-candidate",batchId=c.GetProperty("batchId").GetString(),approved=false,productionApplyAllowed=false,sourceClient=before.ToDictionary(k=>k.Key,k=>new{sha256=k.Value,size=new FileInfo(Path.Combine(targetDir,k.Key)).Length}),donor=donorHashes.ToDictionary(k=>k.Key,k=>new{sha256=k.Value,size=new FileInfo(Path.Combine(donorDir,k.Key)).Length}),output=families.ToDictionary(k=>k,k=>new{sha256=Sha(Path.Combine(outputDir,k)),size=new FileInfo(Path.Combine(outputDir,k)).Length}),versions,fullChanges,nodeChanges,fullImageDigestEvidence=digestEvidence,validation=new{sourceClientUnchanged=true,outputsReparsed=true,fullImageCanvasPayloadDigestsMatch=true,onlyFrozenScopePatched=true,deliberateNpcReplacementIds=replaceNpc.OrderBy(x=>x).ToArray()}};
File.WriteAllText(Path.Combine(outputDir,"REGIONAL_CLIENT_PATCH_MANIFEST.json"),JsonSerializer.Serialize(manifest,new JsonSerializerOptions{WriteIndented=true})+Environment.NewLine);
Console.WriteLine($"Regional client candidate built: {maps.Length} maps, {mobs.Length} mobs, {npcs.Length} NPCs, {items.Length} items, {quests.Length} quests");Console.WriteLine("approved=false / productionApplyAllowed=false");return 0;
