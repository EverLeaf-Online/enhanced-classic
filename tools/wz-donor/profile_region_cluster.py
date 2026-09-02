#!/usr/bin/env python3
"""Profile a donor region as a complete review-only dependency cluster."""
from __future__ import annotations
import argparse, hashlib, json, re, xml.etree.ElementTree as ET
from collections import Counter, defaultdict, deque
from pathlib import Path
ID_FILE_RE=re.compile(r"^(\d+)\.img\.xml$"); NUMERIC_RE=re.compile(r"^\d+$"); QUEST_ID_MIN=100

def prop_map(node): return {c.attrib['name']:c.attrib['value'] for c in list(node) if 'name' in c.attrib and 'value' in c.attrib}
def family_base(root:Path,family:str)->Path:
    direct=root/family; return direct if direct.exists() else root/'wz'/family
def index_family(root:Path,family:str):
    base=family_base(root,family); found={}
    if not base.exists(): return found
    for path in base.rglob('*.img.xml'):
        m=ID_FILE_RE.match(path.name)
        if m: found[m.group(1)]=path
    return found
def xml_fingerprint(path:Path)->str:
    def enc(node): return [node.tag,sorted(node.attrib.items()),[enc(c) for c in list(node)]]
    payload=json.dumps(enc(ET.parse(path).getroot()),ensure_ascii=False,separators=(',',':')).encode(); return hashlib.sha256(payload).hexdigest()
def resolve_cluster(manifest,donor_root):
    maps=index_family(donor_root,'Map.wz'); mobs=index_family(donor_root,'Mob.wz'); mp=[str(x) for x in manifest.get('mapPrefixes',[])]; mi={str(x) for x in manifest.get('mapIds',[])}; bp=[str(x) for x in manifest.get('mobPrefixes',[])]; bi={str(x) for x in manifest.get('mobIds',[])}
    return sorted({x for x in maps if x in mi or any(x.startswith(p) for p in mp)},key=int),sorted({x for x in mobs if x in bi or any(x.startswith(p) for p in bp)},key=int),sorted({str(x) for x in manifest.get('itemIds',[])},key=int)
def parse_map_dependencies(path):
    root=ET.parse(path).getroot(); mobs=set(); npcs=set(); reactors=set(); targets=set(); scripts=set()
    for node in root.iter():
        p=prop_map(node); typ=p.get('type'); cid=p.get('id')
        if typ=='m' and cid and cid.isdigit(): mobs.add(cid)
        elif typ=='n' and cid and cid.isdigit(): npcs.add(cid)
        tm=p.get('tm'); script=p.get('script')
        if tm and tm.isdigit() and tm!='999999999': targets.add(tm)
        if script: scripts.add(script)
    for container in root.iter():
        if (container.attrib.get('name') or '').lower()=='reactor':
            for entry in list(container):
                rid=prop_map(entry).get('id')
                if rid and rid.isdigit(): reactors.add(rid)
    return {'mobs':sorted(mobs,key=int),'npcs':sorted(npcs,key=int),'reactors':sorted(reactors,key=int),'portalTargets':sorted(targets,key=int),'portalScripts':sorted(scripts)}
def parse_mob_dependencies(path):
    root=ET.parse(path).getroot(); revive=set(); links=set()
    for node in root.iter():
        if (node.attrib.get('name') or '').lower()=='revive':
            for child in list(node):
                v=child.attrib.get('value')
                if v and v.isdigit(): revive.add(v)
        if node.attrib.get('name')=='link':
            v=node.attrib.get('value')
            if v and v.isdigit(): links.add(v)
    return {'reviveMobs':sorted(revive,key=int),'linkedMobs':sorted(links,key=int)}
def expand_mob_dependencies(initial,donor_index):
    mobs=set(initial); q=deque(sorted(mobs,key=int)); per={}; added=set()
    while q:
        mid=q.popleft()
        if mid not in donor_index or mid in per: continue
        deps=parse_mob_dependencies(donor_index[mid]); per[mid]=deps
        for target in deps['reviveMobs']:
            if target not in mobs: mobs.add(target); added.add(target); q.append(target)
    return mobs,per,sorted(added,key=int)
def quest_references(quest_root,selected_ids):
    refs=defaultdict(set)
    if not quest_root.exists() or not selected_ids: return {}
    pat=re.compile(rf"(?<!\d)(?:{'|'.join(re.escape(x) for x in sorted(selected_ids,key=len,reverse=True))})(?!\d)")
    for path in quest_root.rglob('*.xml'):
        try: text=path.read_text(encoding='utf-8',errors='ignore')
        except OSError: continue
        if not pat.search(text): continue
        try: tree=ET.fromstring(text)
        except ET.ParseError: continue
        def walk(node,qid=None):
            name=node.attrib.get('name'); nq=qid
            if nq is None and name and NUMERIC_RE.fullmatch(name) and int(name)>=QUEST_ID_MIN: nq=name
            matched=set(pat.findall(' '.join([node.attrib.get('value',''),node.text or ''])))
            if matched and nq is not None: refs[nq].update(matched)
            for child in list(node): walk(child,nq)
        walk(tree)
    return {q:sorted(v,key=int) for q,v in sorted(refs.items(),key=lambda kv:int(kv[0]))}
def portal_script_exists(root,script): return any(p.is_file() for p in (root/'scripts'/'portal'/f'{script}.js',root/'scripts'/'portal'/script))
def npc_script_exists(root,npc_id): return (root/'scripts'/'npc'/f'{npc_id}.js').is_file()
def baseline_reference_scan(root,ids,sample_limit=12):
    results={x:{'referenceCount':0,'fileCount':0,'byRoot':Counter(),'samples':[]} for x in ids}
    if not ids:return results
    pat=re.compile(rf"(?<!\d)(?:{'|'.join(re.escape(x) for x in sorted(ids,key=len,reverse=True))})(?!\d)")
    for rel_root in ('wz/Map.wz','wz/Quest.wz','wz/Etc.wz','scripts','src','sql'):
        base=root/rel_root
        if not base.exists():continue
        for path in ([base] if base.is_file() else base.rglob('*')):
            if not path.is_file() or path.suffix.lower() not in {'.xml','.js','.java','.sql','.txt','.json','.properties'}:continue
            try:text=path.read_text(encoding='utf-8',errors='ignore')
            except OSError:continue
            matches=Counter(m.group(0) for m in pat.finditer(text))
            for cid,count in matches.items():
                row=results[cid]; rel=path.relative_to(root).as_posix(); row['referenceCount']+=count; row['fileCount']+=1; row['byRoot'][rel.split('/',1)[0]]+=count
                if len(row['samples'])<sample_limit:row['samples'].append({'path':rel,'matches':count})
    for row in results.values():row['byRoot']=dict(sorted(row['byRoot'].items()))
    return results
def dormant_collision_candidate(row):
    refs=row.get('baselineReferences',{}); samples=refs.get('samples',[])
    return bool(samples) and all(s['path']=='wz/Etc.wz/NpcLocation.img.xml' for s in samples) and refs.get('fileCount')==1

def build_report(manifest,donor_root,baseline_root):
    map_ids,selected_mobs,item_ids=resolve_cluster(manifest,donor_root); dm=index_family(donor_root,'Map.wz'); dmo=index_family(donor_root,'Mob.wz'); dn=index_family(donor_root,'Npc.wz'); dr=index_family(donor_root,'Reactor.wz'); bm=index_family(baseline_root,'Map.wz'); bmo=index_family(baseline_root,'Mob.wz'); bn=index_family(baseline_root,'Npc.wz'); br=index_family(baseline_root,'Reactor.wz')
    mobs=set(selected_mobs); npcs=set(); reactors=set(); targets=set(); scripts=set(); per_map={}
    for mid in map_ids:
        deps=parse_map_dependencies(dm[mid]); per_map[mid]=deps; mobs.update(deps['mobs']); npcs.update(deps['npcs']); reactors.update(deps['reactors']); targets.update(deps['portalTargets']); scripts.update(deps['portalScripts'])
    mobs,mob_deps,revive_added=expand_mob_dependencies(mobs,dmo)
    quests=quest_references(family_base(donor_root,'Quest.wz'),set(map_ids)|mobs|npcs|set(item_ids))
    npc_quests=defaultdict(list)
    for qid,ids in quests.items():
        for nid in npcs:
            if nid in ids:npc_quests[nid].append(qid)
    def classify(ids,di,bi,family):
        rows=[]
        for x in sorted(set(ids),key=int):
            row={'contentId':x,'inDonor':x in di,'inBaseline':x in bi,'needsBackport':x in di and x not in bi}
            if x in di and x in bi:
                dh=xml_fingerprint(di[x]); bh=xml_fingerprint(bi[x]); row.update({'sameContent':dh==bh,'donorFingerprint':dh,'baselineFingerprint':bh,'family':family})
            rows.append(row)
        return rows
    map_rows=classify(map_ids,dm,bm,'Map.wz'); mob_rows=classify(mobs,dmo,bmo,'Mob.wz'); npc_rows=classify(npcs,dn,bn,'Npc.wz'); reactor_rows=classify(reactors,dr,br,'Reactor.wz'); collisions=[r for rows in (map_rows,mob_rows,npc_rows,reactor_rows) for r in rows if r.get('sameContent') is False]; refs=baseline_reference_scan(baseline_root,{r['contentId'] for r in collisions})
    for row in collisions:
        row['baselineReferences']=refs[row['contentId']]; row['proposedDormantReplacementCandidate']=dormant_collision_candidate(row); row['replacementApproved']=False
    npc_scripts=[{'npcId':nid,'baselineScriptExists':npc_script_exists(baseline_root,nid),'questReferences':sorted(npc_quests[nid],key=int),'questReferenced':bool(npc_quests[nid])} for nid in sorted(npcs,key=int)]
    missing_quest_npc=[r['npcId'] for r in npc_scripts if r['questReferenced'] and not r['baselineScriptExists']]
    map_set=set(map_ids); target_rows=[{'mapId':x,'insideCluster':x in map_set,'inDonor':x in dm,'inBaseline':x in bm,'unresolved':x not in dm and x not in bm} for x in sorted(targets,key=int)]; portal_rows=[{'script':s,'baselineScriptExists':portal_script_exists(baseline_root,s)} for s in sorted(scripts)]
    return {'schemaVersion':3,'kind':'review-only-region-cluster-profile','clusterId':manifest.get('clusterId'),'donorId':manifest.get('donorId'),'selection':{'mapPrefixes':manifest.get('mapPrefixes',[]),'mapIds':manifest.get('mapIds',[]),'mobPrefixes':manifest.get('mobPrefixes',[]),'mobIds':manifest.get('mobIds',[]),'itemIds':item_ids},'counts':{'maps':len(map_ids),'mapReferencedMobs':len(mobs),'reviveDependencyMobsAdded':len(revive_added),'mapReferencedNpcs':len(npcs),'questReferencedNpcs':sum(r['questReferenced'] for r in npc_scripts),'missingQuestNpcScripts':len(missing_quest_npc),'mapReferencedReactors':len(reactors),'portalTargets':len(targets),'portalScripts':len(scripts),'questNodes':len(quests),'selectedItems':len(item_ids),'changedCollisions':len(collisions)},'maps':map_rows,'mobs':mob_rows,'npcs':npc_rows,'reactors':reactor_rows,'mobDependencies':mob_deps,'reviveDependencyMobsAdded':revive_added,'changedCollisions':collisions,'npcScripts':npc_scripts,'portalTargets':target_rows,'portalScripts':portal_rows,'questReferences':quests,'items':item_ids,'perMapDependencies':per_map,'blockingReview':{'missingPortalScripts':[r['script'] for r in portal_rows if not r['baselineScriptExists']],'missingQuestNpcScripts':missing_quest_npc,'unresolvedPortalTargets':[r['mapId'] for r in target_rows if r['unresolved']],'changedContentCollisions':[r['contentId'] for r in collisions]},'approved':False,'importAllowed':False,'automaticImport':False,'note':'This report scopes dependencies only; proposed dormant collision replacements are evidence flags, never approval.'}
def main():
    p=argparse.ArgumentParser();p.add_argument('manifest',type=Path);p.add_argument('--donor',type=Path,required=True);p.add_argument('--baseline',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();r=build_report(json.loads(a.manifest.read_text()),a.donor,a.baseline);a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(r,indent=2,ensure_ascii=False)+'\n');print(json.dumps(r['counts'],sort_keys=True));print('blocking:',json.dumps(r['blockingReview'],sort_keys=True));print('approved=false / importAllowed=false / automaticImport=false');return 0
if __name__=='__main__':raise SystemExit(main())
