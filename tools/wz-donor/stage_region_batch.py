#!/usr/bin/env python3
"""Stage a frozen regional donor batch into a disposable server WZ XML copy only."""
from __future__ import annotations
import argparse, hashlib, json, shutil, xml.etree.ElementTree as ET
from pathlib import Path

def sha256(path:Path)->str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''): h.update(chunk)
    return h.hexdigest()
def tree_digest(root:Path)->str:
    h=hashlib.sha256()
    for p in sorted(x for x in root.rglob('*') if x.is_file()):
        rel=p.relative_to(root).as_posix().encode();h.update(len(rel).to_bytes(4,'big'));h.update(rel);h.update(bytes.fromhex(sha256(p)))
    return h.hexdigest()
def semantic_hash(path:Path)->str:
    def enc(n):return [n.tag,sorted(n.attrib.items()),[enc(c) for c in list(n)]]
    return hashlib.sha256(json.dumps(enc(ET.parse(path).getroot()),separators=(',',':')).encode()).hexdigest()
def family_index(root:Path,family:str):
    out={};base=root/family
    if not base.exists():return out
    for p in base.rglob('*.img.xml'):
        stem=p.name[:-8]
        if stem.isdigit():out[str(int(stem))]=p
    return out
def copy_full_ids(donor:Path,staging:Path,family:str,ids:list[str],replace:set[str]|None=None):
    replace=replace or set();di=family_index(donor,family);si=family_index(staging,family);rows=[]
    for cid in ids:
        if cid not in di:raise ValueError(f'{family} donor missing {cid}')
        src=di[cid]
        if cid in si:
            if cid not in replace:raise ValueError(f'{family} unexpected collision {cid}')
            dst=si[cid];action='replace'
        else:
            rel=src.relative_to(donor/family);dst=staging/family/rel;dst.parent.mkdir(parents=True,exist_ok=True);action='add'
        shutil.copy2(src,dst)
        if semantic_hash(src)!=semantic_hash(dst):raise RuntimeError(f'{family} staged semantic mismatch {cid}')
        rows.append({'family':family,'contentId':cid,'action':action,'path':dst.relative_to(staging).as_posix(),'sha256':sha256(dst)})
    return rows
def clone(node):return ET.fromstring(ET.tostring(node,encoding='unicode'))
def find_parent(root,target):
    for parent in root.iter():
        for child in list(parent):
            if child is target:return parent
    return None
def node_path(root,target):
    def walk(node,path):
        if node is target:return path
        for child in list(node):
            got=walk(child,path+[(child.tag,child.attrib.get('name'))])
            if got is not None:return got
        return None
    result=walk(root,[])
    if result is None:raise ValueError('node not under root')
    return result[:-1]
def ensure_parent(dst_root,src_root,src_target):
    parent=dst_root;src_parent=src_root
    for tag,name in node_path(src_root,src_target):
        src_next=next((x for x in list(src_parent) if x.tag==tag and x.attrib.get('name')==name),None)
        if src_next is None:raise ValueError(f'source parent path lost at {name}')
        dst_next=next((x for x in list(parent) if x.tag==tag and x.attrib.get('name')==name),None)
        if dst_next is None:
            dst_next=ET.Element(src_next.tag,dict(src_next.attrib));parent.append(dst_next)
        parent=dst_next;src_parent=src_next
    return parent
def same_content_id(name,cid):
    if name==cid:return True
    return bool(name and name.isdigit() and cid.isdigit() and int(name)==int(cid))
def matching_nodes(root,cid):return [n for n in root.iter() if same_content_id(n.attrib.get('name'),cid)]
def merge_named_nodes_file(src:Path,dst:Path,ids:list[str],label:str,replace:set[str]|None=None,require_all:bool=True):
    replace=replace or set();st=ET.parse(src);dt=ET.parse(dst);sr=st.getroot();dr=dt.getroot();rows=[]
    for cid in ids:
        src_hits=matching_nodes(sr,cid)
        if len(src_hits)!=1:
            if not src_hits and not require_all:continue
            raise ValueError(f'{label} source expected one node {cid}, got {len(src_hits)} in {src}')
        src_node=src_hits[0];dst_hits=matching_nodes(dr,cid)
        if dst_hits:
            if cid not in replace:raise ValueError(f'{label} refusing existing node {cid} in {dst}')
            if len(dst_hits)!=1:raise ValueError(f'{label} destination duplicate {cid}')
            old=dst_hits[0];parent=find_parent(dr,old)
            if parent is None:raise ValueError(f'{label} cannot replace root node {cid}')
            idx=list(parent).index(old);parent.remove(old);parent.insert(idx,clone(src_node));action='replace'
        else:
            parent=ensure_parent(dr,sr,src_node);parent.append(clone(src_node));action='add'
        rows.append({'kind':label,'contentId':cid,'action':action,'path':dst.as_posix(),'sourceNodeName':src_node.attrib.get('name')})
    ET.indent(dt,space='  ');dt.write(dst,encoding='utf-8',xml_declaration=True)
    return rows
def merge_item_nodes(donor:Path,staging:Path,ids:list[str]):
    rows=[]
    for cid in ids:
        hits=[]
        for src in (donor/'Item.wz'/'Etc').rglob('*.xml'):
            try:r=ET.parse(src).getroot()
            except ET.ParseError:continue
            if len(matching_nodes(r,cid))==1:hits.append(src)
        if len(hits)!=1:raise ValueError(f'Item donor expected one container for {cid}, got {len(hits)}')
        src=hits[0];rel=src.relative_to(donor/'Item.wz'/'Etc');dst=staging/'Item.wz'/'Etc'/rel
        if not dst.is_file():raise ValueError(f'Item staging target missing {rel}')
        rows+=merge_named_nodes_file(src,dst,[cid],'Item.wz Etc item')
    return rows
def merge_string_file(string_donor:Path,staging:Path,filename:str,ids:list[str],replace:set[str]|None=None,require_all:bool=True):
    src=string_donor/'String.wz'/filename;dst=staging/'String.wz'/filename
    if not src.is_file() or not dst.is_file():
        if not require_all:return []
        raise ValueError(f'String file missing {filename}')
    return merge_named_nodes_file(src,dst,ids,f'String.wz/{filename}',replace,require_all)
def merge_quests(donor:Path,staging:Path,ids:list[str]):
    rows=[]
    for filename in ('Check.img.xml','Act.img.xml','QuestInfo.img.xml'):
        src=donor/'Quest.wz'/filename;dst=staging/'Quest.wz'/filename
        if src.is_file() and dst.is_file():rows+=merge_named_nodes_file(src,dst,ids,f'Quest.wz/{filename}',require_all=False)
    found={r['contentId'] for r in rows};missing=sorted(set(ids)-found,key=int)
    if missing:raise ValueError(f'Quest IDs absent from all staged Quest files: {missing}')
    return rows
def stage(contract_path:Path,donor:Path,string_donor:Path,canonical:Path,staging:Path):
    c=json.loads(contract_path.read_text(encoding='utf-8'))
    for key in ('approved','importAllowed','automaticImport','productionApplyAllowed'):
        if c.get(key) is not False:raise ValueError(f'{key} must remain false')
    before=tree_digest(canonical)
    if staging.exists():shutil.rmtree(staging)
    shutil.copytree(canonical,staging)
    collision=c['deliberateReplacementCollisions'][0];cid=collision['contentId'];base_npc=family_index(canonical,'Npc.wz').get(cid)
    if not base_npc or semantic_hash(base_npc)!=collision['baselineFingerprint']:raise ValueError(f'{cid} baseline fingerprint drifted before staging')
    full=[];full+=copy_full_ids(donor,staging,'Map.wz',c['maps']);full+=copy_full_ids(donor,staging,'Mob.wz',c['mobs']);full+=copy_full_ids(donor,staging,'Npc.wz',c['castleNpcs'],replace={cid})
    if semantic_hash(family_index(staging,'Npc.wz')[cid])!=collision['donorFingerprint']:raise ValueError(f'{cid} staged donor fingerprint mismatch')
    item_rows=merge_item_nodes(donor,staging,c['items']);quest_rows=merge_quests(donor,staging,c['questIds']);string_rows=[]
    string_rows+=merge_string_file(string_donor,staging,'Etc.img.xml',c['items']);string_rows+=merge_string_file(string_donor,staging,'Map.img.xml',c['maps'],require_all=False);string_rows+=merge_string_file(string_donor,staging,'Mob.img.xml',c['mobs'],require_all=False);string_rows+=merge_string_file(string_donor,staging,'Npc.img.xml',c['castleNpcs'],replace={cid},require_all=False);string_rows+=merge_string_file(string_donor,staging,'Quest.img.xml',c['questIds'],require_all=False)
    after=tree_digest(canonical)
    if after!=before:raise RuntimeError('canonical WZ tree changed during regional staging')
    report={'schemaVersion':2,'mode':'temporary-regional-staging-copy','batchId':c['batchId'],'canonicalMutated':False,'productionApplyAllowed':False,'approved':False,'canonicalTreeSha256Before':before,'canonicalTreeSha256After':after,'stagingTreeSha256':tree_digest(staging),'fullFileChanges':full,'itemNodes':item_rows,'questNodes':quest_rows,'stringNodes':string_rows,'deliberateReplacementIds':[cid]}
    (staging/'REGIONAL_STAGING_REPORT.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');return report
def main():
    p=argparse.ArgumentParser();p.add_argument('--contract',type=Path,required=True);p.add_argument('--donor',type=Path,required=True);p.add_argument('--string-donor',type=Path,required=True);p.add_argument('--canonical',type=Path,required=True);p.add_argument('--staging',type=Path,required=True);a=p.parse_args();r=stage(a.contract,a.donor,a.string_donor,a.canonical,a.staging);print('full files staged:',len(r['fullFileChanges']));print('item nodes staged:',len(r['itemNodes']));print('quest nodes staged:',len(r['questNodes']));print('string nodes staged:',len(r['stringNodes']));print('canonicalMutated=false / approved=false / productionApplyAllowed=false');return 0
if __name__=='__main__':raise SystemExit(main())
