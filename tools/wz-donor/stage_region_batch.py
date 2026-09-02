#!/usr/bin/env python3
"""Stage a frozen regional donor batch into a disposable server WZ XML copy only."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import xml.etree.ElementTree as ET
from pathlib import Path


def sha256(path: Path) -> str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''): h.update(chunk)
    return h.hexdigest()


def tree_digest(root: Path) -> str:
    h=hashlib.sha256()
    for p in sorted(x for x in root.rglob('*') if x.is_file()):
        rel=p.relative_to(root).as_posix().encode(); h.update(len(rel).to_bytes(4,'big')); h.update(rel); h.update(bytes.fromhex(sha256(p)))
    return h.hexdigest()


def family_index(root: Path, family: str):
    base=root/family; out={}
    if not base.exists(): return out
    for p in base.rglob('*.img.xml'):
        stem=p.name[:-8]
        if stem.isdigit(): out[str(int(stem))]=p
    return out


def semantic_hash(path: Path) -> str:
    def enc(n): return [n.tag,sorted(n.attrib.items()),[enc(c) for c in list(n)]]
    return hashlib.sha256(json.dumps(enc(ET.parse(path).getroot()),separators=(',',':')).encode()).hexdigest()


def copy_full_ids(donor:Path, staging:Path, family:str, ids:list[str], replace:set[str]|None=None):
    replace=replace or set(); di=family_index(donor,family); si=family_index(staging,family); rows=[]
    for cid in ids:
        if cid not in di: raise ValueError(f'{family} donor missing {cid}')
        src=di[cid]
        if cid in si:
            if cid not in replace: raise ValueError(f'{family} unexpected collision {cid}')
            dst=si[cid]; action='replace'
        else:
            rel=src.relative_to(donor/family); dst=staging/family/rel; dst.parent.mkdir(parents=True,exist_ok=True); action='add'
        shutil.copy2(src,dst)
        if semantic_hash(dst)!=semantic_hash(src): raise RuntimeError(f'{family} staged hash mismatch {cid}')
        rows.append({'family':family,'contentId':cid,'action':action,'path':dst.relative_to(staging).as_posix(),'sha256':sha256(dst)})
    return rows


def find_named_node(root:Path, cid:str):
    hits=[]
    for p in root.rglob('*.xml'):
        try: tree=ET.parse(p)
        except (ET.ParseError,OSError): continue
        for n in tree.getroot().iter():
            if n.attrib.get('name')==cid: hits.append((p,tree,n))
    return hits


def append_named_nodes(donor_root:Path, staging_root:Path, ids:list[str], label:str):
    rows=[]
    donor_hits={cid:find_named_node(donor_root,cid) for cid in ids}
    for cid,hits in donor_hits.items():
        if len(hits)!=1: raise ValueError(f'{label} donor expected one node {cid}, got {len(hits)}')
        src_path,_,src_node=hits[0]
        rel=src_path.relative_to(donor_root); dst_path=staging_root/rel
        if not dst_path.is_file(): raise ValueError(f'{label} staging target missing {rel}')
        dst_tree=ET.parse(dst_path); dst_root=dst_tree.getroot()
        existing=[n for n in dst_root.iter() if n.attrib.get('name')==cid]
        if existing: raise ValueError(f'{label} refusing existing staged node {cid} in {rel}')
        parent_rel=None
        src_tree=ET.parse(src_path); src_root=src_tree.getroot()
        def locate_parent(node,target,path=()):
            for child in list(node):
                if child is target:return path
                got=locate_parent(child,target,path+(child.attrib.get('name',''),))
                if got is not None:return got
            return None
        parent_path=locate_parent(src_root,src_node)
        parent=dst_root
        if parent_path:
            # path identifies ancestors below source root, excluding target itself.
            for name in parent_path:
                candidates=[x for x in list(parent) if x.attrib.get('name')==name]
                if not candidates: raise ValueError(f'{label} staging parent path missing {rel}:{name}')
                parent=candidates[0]
        parent.append(ET.fromstring(ET.tostring(src_node,encoding='unicode')))
        ET.indent(dst_tree,space='  '); dst_tree.write(dst_path,encoding='utf-8',xml_declaration=True)
        rows.append({'kind':label,'contentId':cid,'path':rel.as_posix()})
    return rows


def merge_quest_nodes(donor_quest:Path, staging_quest:Path, quest_ids:list[str]):
    rows=[]
    for rel in ('Check.img.xml','Act.img.xml','QuestInfo.img.xml'):
        src=donor_quest/rel
        if not src.is_file(): continue
        dst=staging_quest/rel
        if not dst.is_file(): raise ValueError(f'Quest staging target missing {rel}')
        st=ET.parse(src); dt=ET.parse(dst); sr=st.getroot(); dr=dt.getroot(); changed=[]
        for phase in list(sr):
            phase_name=phase.attrib.get('name')
            dst_phase=next((x for x in list(dr) if x.attrib.get('name')==phase_name),None)
            if dst_phase is None:
                dst_phase=ET.SubElement(dr,phase.tag,dict(phase.attrib))
            for q in list(phase):
                qid=q.attrib.get('name')
                if qid not in quest_ids: continue
                if any(x.attrib.get('name')==qid for x in list(dst_phase)): raise ValueError(f'Quest collision {qid} in {rel}')
                dst_phase.append(ET.fromstring(ET.tostring(q,encoding='unicode'))); changed.append(qid)
        if changed:
            ET.indent(dt,space='  '); dt.write(dst,encoding='utf-8',xml_declaration=True); rows.append({'path':f'Quest.wz/{rel}','questIds':sorted(set(changed),key=int)})
    return rows


def stage(contract_path:Path,donor:Path,canonical:Path,staging:Path):
    c=json.loads(contract_path.read_text(encoding='utf-8'))
    for key in ('approved','importAllowed','automaticImport','productionApplyAllowed'):
        if c.get(key) is not False: raise ValueError(f'{key} must remain false')
    before=tree_digest(canonical)
    if staging.exists(): shutil.rmtree(staging)
    shutil.copytree(canonical,staging)

    collision=c['deliberateReplacementCollisions'][0]
    base_npc=family_index(canonical,'Npc.wz').get(collision['contentId'])
    if not base_npc or semantic_hash(base_npc)!=collision['baselineFingerprint']: raise ValueError('9110100 baseline fingerprint drifted before staging')

    full=[]
    full+=copy_full_ids(donor,staging,'Map.wz',c['maps'])
    full+=copy_full_ids(donor,staging,'Mob.wz',c['mobs'])
    full+=copy_full_ids(donor,staging,'Npc.wz',c['castleNpcs'],replace={collision['contentId']})

    # Item.wz Etc data and corresponding String.wz Etc names are grouped containers.
    item_rows=append_named_nodes(donor/'Item.wz'/'Etc',staging/'Item.wz'/'Etc',c['items'],'item')
    string_item_rows=append_named_nodes(donor.parent/'string'/'String.wz'/'Etc.img.xml'.rsplit('/',1)[0] if False else donor/'__unused__',staging,'noop') if False else []

    quest_rows=merge_quest_nodes(donor/'Quest.wz',staging/'Quest.wz',c['questIds'])

    after=tree_digest(canonical)
    if after!=before: raise RuntimeError('canonical WZ tree changed during regional staging')
    report={'schemaVersion':1,'mode':'temporary-regional-staging-copy','batchId':c['batchId'],'canonicalMutated':False,'productionApplyAllowed':False,'approved':False,'canonicalTreeSha256Before':before,'canonicalTreeSha256After':after,'stagingTreeSha256':tree_digest(staging),'fullFileChanges':full,'itemNodes':item_rows,'questChanges':quest_rows,'deliberateReplacementIds':[collision['contentId']]}
    (staging/'REGIONAL_STAGING_REPORT.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    return report


def main():
    p=argparse.ArgumentParser();p.add_argument('--contract',type=Path,required=True);p.add_argument('--donor',type=Path,required=True);p.add_argument('--canonical',type=Path,required=True);p.add_argument('--staging',type=Path,required=True);a=p.parse_args()
    r=stage(a.contract,a.donor,a.canonical,a.staging);print(f"maps/mobs/npcs staged: {len(r['fullFileChanges'])}");print(f"item nodes staged: {len(r['itemNodes'])}");print('canonicalMutated=false / approved=false / productionApplyAllowed=false');return 0
if __name__=='__main__':raise SystemExit(main())
