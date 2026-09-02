#!/usr/bin/env python3
"""Profile a donor region as a complete review-only dependency cluster."""
from __future__ import annotations
import argparse, json, re, xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path
ID_FILE_RE=re.compile(r"^(\d+)\.img\.xml$"); NUMERIC_RE=re.compile(r"^\d+$")

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
        def walk(node,stack):
            name=node.attrib.get('name'); next_stack=stack+[name] if name and NUMERIC_RE.fullmatch(name) else stack
            matched=set(pat.findall(' '.join([node.attrib.get('value',''),node.text or ''])))
            if matched: refs[next_stack[-1] if next_stack else path.stem].update(matched)
            for child in list(node): walk(child,next_stack)
        walk(tree,[])
    return {q:sorted(v,key=int) for q,v in sorted(refs.items(),key=lambda kv:int(kv[0]) if kv[0].isdigit() else 10**12)}

def baseline_script_exists(root, script):
    return any(p.is_file() for p in (root/'scripts'/'portal'/f'{script}.js',root/'scripts'/'portal'/script))

def build_report(manifest, donor_root, baseline_root):
    map_ids,selected_mobs,item_ids=resolve_cluster(manifest,donor_root)
    dm=index_family(donor_root,'Map.wz'); dmo=index_family(donor_root,'Mob.wz'); dn=index_family(donor_root,'Npc.wz'); dr=index_family(donor_root,'Reactor.wz')
    bm=index_family(baseline_root,'Map.wz'); bmo=index_family(baseline_root,'Mob.wz'); bn=index_family(baseline_root,'Npc.wz'); br=index_family(baseline_root,'Reactor.wz')
    mobs=set(selected_mobs); npcs=set(); reactors=set(); targets=set(); scripts=set(); per_map={}
    for mid in map_ids:
        deps=parse_map_dependencies(dm[mid]); per_map[mid]=deps; mobs.update(deps['mobs']); npcs.update(deps['npcs']); reactors.update(deps['reactors']); targets.update(deps['portalTargets']); scripts.update(deps['portalScripts'])
    quests=quest_references(family_base(donor_root,'Quest.wz'),set(map_ids)|mobs|set(item_ids))
    def classify(ids,di,bi): return [{'contentId':x,'inDonor':x in di,'inBaseline':x in bi,'needsBackport':x in di and x not in bi} for x in sorted(set(ids),key=int)]
    map_set=set(map_ids); target_rows=[{'mapId':x,'insideCluster':x in map_set,'inDonor':x in dm,'inBaseline':x in bm,'unresolved':x not in dm and x not in bm} for x in sorted(targets,key=int)]
    script_rows=[{'script':s,'baselineScriptExists':baseline_script_exists(baseline_root,s)} for s in sorted(scripts)]
    return {'schemaVersion':1,'kind':'review-only-region-cluster-profile','clusterId':manifest.get('clusterId'),'donorId':manifest.get('donorId'),'selection':{'mapPrefixes':manifest.get('mapPrefixes',[]),'mapIds':manifest.get('mapIds',[]),'mobPrefixes':manifest.get('mobPrefixes',[]),'mobIds':manifest.get('mobIds',[]),'itemIds':item_ids},'counts':{'maps':len(map_ids),'mapReferencedMobs':len(mobs),'mapReferencedNpcs':len(npcs),'mapReferencedReactors':len(reactors),'portalTargets':len(targets),'portalScripts':len(scripts),'questNodes':len(quests),'selectedItems':len(item_ids)},'maps':classify(map_ids,dm,bm),'mobs':classify(mobs,dmo,bmo),'npcs':classify(npcs,dn,bn),'reactors':classify(reactors,dr,br),'portalTargets':target_rows,'portalScripts':script_rows,'questReferences':quests,'items':item_ids,'perMapDependencies':per_map,'blockingReview':{'missingPortalScripts':[r['script'] for r in script_rows if not r['baselineScriptExists']],'unresolvedPortalTargets':[r['mapId'] for r in target_rows if r['unresolved']]},'approved':False,'importAllowed':False,'automaticImport':False,'note':'This report only scopes dependencies. It does not establish gameplay correctness, script compatibility, client parity, drop tables, or import safety.'}

def main():
    p=argparse.ArgumentParser(); p.add_argument('manifest',type=Path); p.add_argument('--donor',type=Path,required=True); p.add_argument('--baseline',type=Path,required=True); p.add_argument('--output',type=Path,required=True); a=p.parse_args()
    r=build_report(json.loads(a.manifest.read_text(encoding='utf-8')),a.donor,a.baseline); a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(json.dumps(r,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps(r['counts'],sort_keys=True)); print('missing portal scripts:',len(r['blockingReview']['missingPortalScripts'])); print('unresolved portal targets:',len(r['blockingReview']['unresolvedPortalTargets'])); print('approved=false / importAllowed=false / automaticImport=false'); return 0
if __name__=='__main__': raise SystemExit(main())
