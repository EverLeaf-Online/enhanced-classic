#!/usr/bin/env python3
"""Profile a donor region as a complete review-only dependency cluster."""
from __future__ import annotations
import argparse, hashlib, json, re, xml.etree.ElementTree as ET
from collections import Counter, defaultdict, deque
from pathlib import Path
ID_FILE_RE=re.compile(r"^(\d+)\.img\.xml$"); NUMERIC_RE=re.compile(r"^\d+$"); QUEST_ID_MIN=100

def prop_map(node):
    return {c.attrib['name']:c.attrib['value'] for c in list(node) if 'name' in c.attrib and 'value' in c.attrib}

def family_base(root: Path, family: str) -> Path:
    direct=root/family
    return direct if direct.exists() else root/'wz'/family

def index_family(root: Path, family: str):
    base=family_base(root,family); found={}
    if not base.exists(): return found
    for path in base.rglob('*.img.xml'):
        m=ID_FILE_RE.match(path.name)
        if m: found[m.group(1)]=path
    return found

def xml_fingerprint(path: Path) -> str:
    def encode(node):
        return [node.tag, sorted(node.attrib.items()), [encode(child) for child in list(node)]]
    root=ET.parse(path).getroot()
    payload=json.dumps(encode(root),ensure_ascii=False,separators=(',',':')).encode('utf-8')
    return hashlib.sha256(payload).hexdigest()

def resolve_cluster(manifest, donor_root):
    maps=index_family(donor_root,'Map.wz'); mobs=index_family(donor_root,'Mob.wz')
    mp=[str(x) for x in manifest.get('mapPrefixes',[])]; mi={str(x) for x in manifest.get('mapIds',[])}
    bp=[str(x) for x in manifest.get('mobPrefixes',[])]; bi={str(x) for x in manifest.get('mobIds',[])}
    map_ids=sorted({x for x in maps if x in mi or any(x.startswith(p) for p in mp)},key=int)
    mob_ids=sorted({x for x in mobs if x in bi or any(x.startswith(p) for p in bp)},key=int)
    items=sorted({str(x) for x in manifest.get('itemIds',[])},key=int)
    return map_ids,mob_ids,items

def parse_map_dependencies(path):
    root=ET.parse(path).getroot(); mobs=set(); npcs=set(); reactors=set(); targets=set(); scripts=set()
    for node in root.iter():
        p=prop_map(node); typ=p.get('type'); cid=p.get('id')
        if typ=='m' and cid and cid.isdigit(): mobs.add(cid)
        elif typ=='n' and cid and cid.isdigit(): npcs.add(cid)
        tm=p.get('tm')
        if tm and tm.isdigit() and tm!='999999999': targets.add(tm)
        script=p.get('script')
        if script: scripts.add(script)
    for container in root.iter():
        if (container.attrib.get('name') or '').lower()!='reactor': continue
        for entry in list(container):
            rid=prop_map(entry).get('id')
            if rid and rid.isdigit(): reactors.add(rid)
    return {'mobs':sorted(mobs,key=int),'npcs':sorted(npcs,key=int),'reactors':sorted(reactors,key=int),'portalTargets':sorted(targets,key=int),'portalScripts':sorted(scripts)}

def parse_mob_dependencies(path: Path) -> dict:
    root=ET.parse(path).getroot(); revive=set(); links=set()
    for node in root.iter():
        if (node.attrib.get('name') or '').lower()=='revive':
            for child in list(node):
                value=child.attrib.get('value')
                if value and value.isdigit(): revive.add(value)
        if node.attrib.get('name')=='link':
            value=node.attrib.get('value')
            if value and value.isdigit(): links.add(value)
    return {'reviveMobs':sorted(revive,key=int),'linkedMobs':sorted(links,key=int)}

def expand_mob_dependencies(initial_mobs, donor_index):
    mobs=set(initial_mobs); queue=deque(sorted(mobs,key=int)); per_mob={}; revive_added=set()
    while queue:
        mob_id=queue.popleft()
        if mob_id not in donor_index or mob_id in per_mob: continue
        deps=parse_mob_dependencies(donor_index[mob_id]); per_mob[mob_id]=deps
        for target in deps['reviveMobs']:
            if target not in mobs:
                mobs.add(target); revive_added.add(target); queue.append(target)
    return mobs, per_mob, sorted(revive_added,key=int)

def quest_references(quest_root, selected_ids):
    refs=defaultdict(set)
    if not quest_root.exists() or not selected_ids: return {}
    pat=re.compile(rf"(?<!\d)(?:{'|'.join(re.escape(x) for x in sorted(selected_ids,key=len,reverse=True))})(?!\d)")
    for path in quest_root.rglob('*.xml'):
        try: text=path.read_text(encoding='utf-8',errors='ignore')
        except OSError: continue
        if not pat.search(text): continue
        try: tree=ET.fromstring(text)
        except ET.ParseError: continue
        def walk(node,quest_id=None):
            name=node.attrib.get('name'); next_quest=quest_id
            if next_quest is None and name and NUMERIC_RE.fullmatch(name) and int(name)>=QUEST_ID_MIN: next_quest=name
            matched=set(pat.findall(' '.join([node.attrib.get('value',''),node.text or ''])))
            if matched and next_quest is not None: refs[next_quest].update(matched)
            for child in list(node): walk(child,next_quest)
        walk(tree)
    return {q:sorted(v,key=int) for q,v in sorted(refs.items(),key=lambda kv:int(kv[0]))}

def baseline_script_exists(root, script):
    return any(p.is_file() for p in (root/'scripts'/'portal'/f'{script}.js',root/'scripts'/'portal'/script))

def baseline_reference_scan(root: Path, ids: set[str], sample_limit: int=12):
    results={x:{'referenceCount':0,'fileCount':0,'byRoot':Counter(),'samples':[]} for x in ids}
    if not ids: return results
    pat=re.compile(rf"(?<!\d)(?:{'|'.join(re.escape(x) for x in sorted(ids,key=len,reverse=True))})(?!\d)")
    scan_roots=('wz/Map.wz','wz/Quest.wz','wz/Etc.wz','scripts','src','sql')
    for rel_root in scan_roots:
        base=root/rel_root
        if not base.exists(): continue
        paths=[base] if base.is_file() else base.rglob('*')
        for path in paths:
            if not path.is_file() or path.suffix.lower() not in {'.xml','.js','.java','.sql','.txt','.json','.properties'}: continue
            try: text=path.read_text(encoding='utf-8',errors='ignore')
            except OSError: continue
            matches=Counter(m.group(0) for m in pat.finditer(text))
            if not matches: continue
            rel=path.relative_to(root).as_posix(); top=rel.split('/',1)[0]
            for content_id,count in matches.items():
                row=results[content_id]; row['referenceCount']+=count; row['fileCount']+=1; row['byRoot'][top]+=count
                if len(row['samples'])<sample_limit: row['samples'].append({'path':rel,'matches':count})
    for row in results.values(): row['byRoot']=dict(sorted(row['byRoot'].items()))
    return results

def build_report(manifest, donor_root, baseline_root):
    map_ids,selected_mobs,item_ids=resolve_cluster(manifest,donor_root)
    dm=index_family(donor_root,'Map.wz'); dmo=index_family(donor_root,'Mob.wz'); dn=index_family(donor_root,'Npc.wz'); dr=index_family(donor_root,'Reactor.wz')
    bm=index_family(baseline_root,'Map.wz'); bmo=index_family(baseline_root,'Mob.wz'); bn=index_family(baseline_root,'Npc.wz'); br=index_family(baseline_root,'Reactor.wz')
    mobs=set(selected_mobs); npcs=set(); reactors=set(); targets=set(); scripts=set(); per_map={}
    for mid in map_ids:
        deps=parse_map_dependencies(dm[mid]); per_map[mid]=deps; mobs.update(deps['mobs']); npcs.update(deps['npcs']); reactors.update(deps['reactors']); targets.update(deps['portalTargets']); scripts.update(deps['portalScripts'])
    mobs,mob_deps,revive_added=expand_mob_dependencies(mobs,dmo)
    quests=quest_references(family_base(donor_root,'Quest.wz'),set(map_ids)|mobs|set(item_ids))
    def classify(ids,di,bi,family):
        rows=[]
        for x in sorted(set(ids),key=int):
            row={'contentId':x,'inDonor':x in di,'inBaseline':x in bi,'needsBackport':x in di and x not in bi}
            if x in di and x in bi:
                donor_hash=xml_fingerprint(di[x]); baseline_hash=xml_fingerprint(bi[x]); row.update({'sameContent':donor_hash==baseline_hash,'donorFingerprint':donor_hash,'baselineFingerprint':baseline_hash,'family':family})
            rows.append(row)
        return rows
    map_rows=classify(map_ids,dm,bm,'Map.wz'); mob_rows=classify(mobs,dmo,bmo,'Mob.wz'); npc_rows=classify(npcs,dn,bn,'Npc.wz'); reactor_rows=classify(reactors,dr,br,'Reactor.wz')
    collision_rows=[r for rows in (map_rows,mob_rows,npc_rows,reactor_rows) for r in rows if r.get('sameContent') is False]
    collision_ids={r['contentId'] for r in collision_rows}; baseline_refs=baseline_reference_scan(baseline_root,collision_ids)
    for row in collision_rows: row['baselineReferences']=baseline_refs[row['contentId']]
    map_set=set(map_ids); target_rows=[{'mapId':x,'insideCluster':x in map_set,'inDonor':x in dm,'inBaseline':x in bm,'unresolved':x not in dm and x not in bm} for x in sorted(targets,key=int)]
    script_rows=[{'script':s,'baselineScriptExists':baseline_script_exists(baseline_root,s)} for s in sorted(scripts)]
    return {'schemaVersion':2,'kind':'review-only-region-cluster-profile','clusterId':manifest.get('clusterId'),'donorId':manifest.get('donorId'),'selection':{'mapPrefixes':manifest.get('mapPrefixes',[]),'mapIds':manifest.get('mapIds',[]),'mobPrefixes':manifest.get('mobPrefixes',[]),'mobIds':manifest.get('mobIds',[]),'itemIds':item_ids},'counts':{'maps':len(map_ids),'mapReferencedMobs':len(mobs),'reviveDependencyMobsAdded':len(revive_added),'mapReferencedNpcs':len(npcs),'mapReferencedReactors':len(reactors),'portalTargets':len(targets),'portalScripts':len(scripts),'questNodes':len(quests),'selectedItems':len(item_ids),'changedCollisions':len(collision_rows)},'maps':map_rows,'mobs':mob_rows,'npcs':npc_rows,'reactors':reactor_rows,'mobDependencies':mob_deps,'reviveDependencyMobsAdded':revive_added,'changedCollisions':collision_rows,'portalTargets':target_rows,'portalScripts':script_rows,'questReferences':quests,'items':item_ids,'perMapDependencies':per_map,'blockingReview':{'missingPortalScripts':[r['script'] for r in script_rows if not r['baselineScriptExists']],'unresolvedPortalTargets':[r['mapId'] for r in target_rows if r['unresolved']],'changedContentCollisions':[r['contentId'] for r in collision_rows]},'approved':False,'importAllowed':False,'automaticImport':False,'note':'This report only scopes dependencies. It does not establish gameplay correctness, script compatibility, client parity, drop tables, or import safety.'}

def main():
    p=argparse.ArgumentParser(); p.add_argument('manifest',type=Path); p.add_argument('--donor',type=Path,required=True); p.add_argument('--baseline',type=Path,required=True); p.add_argument('--output',type=Path,required=True); a=p.parse_args()
    r=build_report(json.loads(a.manifest.read_text(encoding='utf-8')),a.donor,a.baseline); a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(json.dumps(r,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps(r['counts'],sort_keys=True)); print('missing portal scripts:',len(r['blockingReview']['missingPortalScripts'])); print('unresolved portal targets:',len(r['blockingReview']['unresolvedPortalTargets'])); print('changed collisions:',len(r['blockingReview']['changedContentCollisions'])); print('approved=false / importAllowed=false / automaticImport=false'); return 0
if __name__=='__main__': raise SystemExit(main())
