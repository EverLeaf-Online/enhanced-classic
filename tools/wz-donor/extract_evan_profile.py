#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, re, xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path

EVAN_JOB_IDS={"2001","2200","2210","2211","2212","2213","2214","2215","2216","2217","2218"}
TEXT_TERMS=("evan","mir","dragon master","onyx dragon")
NUM_RE=re.compile(r"(?<!\d)(\d{3,10})(?!\d)")
NUMERIC_RE=re.compile(r"^\d+$")
FILE_ID_RE=re.compile(r"^(\d+)\.img\.xml$")
QUEST_ID_MIN=100
FAMILIES=("Npc.wz","Map.wz","Mob.wz","Item.wz")

def family_base(root:Path,family:str)->Path:
    direct=root/family
    return direct if direct.exists() else root/'wz'/family

def iter_xml(root:Path):
    if not root.exists(): return
    for p in root.rglob('*.xml'):
        if p.is_file(): yield p

def read_xml(path:Path):
    try:return ET.parse(path).getroot()
    except (ET.ParseError,OSError):return None

def read_text(path:Path)->str:
    try:return path.read_text(encoding='utf-8',errors='ignore')
    except OSError:return ''

def local_text(node:ET.Element)->str:
    return ' '.join((node.attrib.get('name',''),node.attrib.get('value',''),node.text or ''))

def term_hits(text:str):
    low=text.lower(); hits=[]
    for term in TEXT_TERMS:
        if term=='mir':
            if re.search(r'(?<![a-z])mir(?![a-z])',low): hits.append(term)
        elif term in low: hits.append(term)
    return sorted(set(hits))

def anchor_pattern(anchors:set[str]):
    if not anchors:return None
    return re.compile(r"(?<!\d)(?:"+'|'.join(re.escape(x) for x in sorted(anchors,key=len,reverse=True))+r")(?!\d)")

def skill_evidence(core:Path):
    base=family_base(core,'Skill.wz'); rows=[]; skill_ids=set(); job_files=set()
    for path in iter_xml(base):
        stem=path.name.removesuffix('.img.xml')
        if stem not in EVAN_JOB_IDS: continue
        root=read_xml(path)
        if root is None: continue
        job_files.add(stem); ids=set()
        for node in root.iter():
            name=node.attrib.get('name','')
            if name.isdigit() and len(name)>=7: ids.add(name)
        skill_ids.update(ids)
        rows.append({'path':str(path.relative_to(core)),'jobId':stem,'skillIds':sorted(ids,key=int)})
    rows.sort(key=lambda r:int(r['jobId']))
    return rows,skill_ids,job_files

def string_evidence(string_root:Path,target_ids:set[str]):
    rows=[]; discovered=set()
    for path in iter_xml(string_root):
        root=read_xml(path)
        if root is None: continue
        records=defaultdict(lambda:{'texts':[],'terms':set()})
        def walk(node,current=None):
            name=node.attrib.get('name','')
            if NUMERIC_RE.fullmatch(name) and len(name)>=4: current=name
            local=local_text(node)
            if current:
                rec=records[current]; rec['texts'].append(local); rec['terms'].update(term_hits(local))
            for child in list(node): walk(child,current)
        walk(root)
        for cid,rec in records.items():
            if cid not in target_ids and not rec['terms']: continue
            text=' '.join(x for x in rec['texts'] if x).strip()
            discovered.add(cid)
            rows.append({'path':str(path.relative_to(string_root)),'contentId':cid,'terms':sorted(rec['terms']),'text':text[:1600]})
    rows.sort(key=lambda r:(r['path'],int(r['contentId']) if r['contentId'].isdigit() else 10**12))
    return rows,discovered

def quest_evidence(core:Path,anchors:set[str]):
    base=family_base(core,'Quest.wz'); pat=anchor_pattern(anchors); records={}
    if pat is None:return []
    for path in iter_xml(base):
        root=read_xml(path)
        if root is None: continue
        def walk(node,quest_id=None):
            name=node.attrib.get('name',''); q=quest_id
            if q is None and name.isdigit() and int(name)>=QUEST_ID_MIN: q=name
            local=local_text(node)
            if q:
                rec=records.setdefault(q,{'questId':q,'paths':set(),'anchorRefs':set(),'ids':set(),'matched':False})
                rec['paths'].add(str(path.relative_to(core))); rec['ids'].update(NUM_RE.findall(local))
                found=set(pat.findall(local))
                if found: rec['matched']=True; rec['anchorRefs'].update(found)
            for child in list(node): walk(child,q)
        walk(root)
    out=[]
    for q,rec in sorted(records.items(),key=lambda kv:int(kv[0])):
        if not rec['matched']:continue
        out.append({'questId':q,'paths':sorted(rec['paths']),'anchorRefs':sorted(rec['anchorRefs'],key=lambda x:(len(x),x)),'ids':sorted(rec['ids'],key=lambda x:(len(x),int(x)))})
    return out

def standalone_family_evidence(core:Path,family:str,anchors:set[str]):
    base=family_base(core,family); pat=anchor_pattern(anchors); rows=[]; discovered=set()
    if pat is None:return rows,discovered
    for path in iter_xml(base):
        m=FILE_ID_RE.match(path.name)
        if not m:continue
        cid=m.group(1); text=read_text(path); refs=sorted(set(pat.findall(text)),key=lambda x:(len(x),x)); hits=term_hits(text)
        if not refs and not hits:continue
        ids=set(NUM_RE.findall(text)); ids.add(cid); discovered.update(ids)
        rows.append({'path':str(path.relative_to(core)),'fileId':cid,'contentId':cid,'anchorRefs':refs,'termHits':hits,'ids':sorted(ids,key=lambda x:(len(x),int(x)))})
    rows.sort(key=lambda r:int(r['contentId']))
    return rows,discovered

def item_evidence(core:Path,anchors:set[str]):
    base=family_base(core,'Item.wz'); pat=anchor_pattern(anchors); rows=[]; discovered=set()
    if pat is None:return rows,discovered
    for path in iter_xml(base):
        m=FILE_ID_RE.match(path.name); file_id=m.group(1) if m else None
        # Pet/single-item files have a real 7-8 digit item id in the filename.
        if file_id and len(file_id)>=7:
            text=read_text(path); refs=sorted(set(pat.findall(text)),key=lambda x:(len(x),x)); hits=term_hits(text)
            if refs or hits:
                ids=set(NUM_RE.findall(text)); ids.add(file_id); discovered.update(ids)
                rows.append({'path':str(path.relative_to(core)),'fileId':file_id,'contentId':file_id,'anchorRefs':refs,'termHits':hits,'ids':sorted(ids,key=lambda x:(len(x),int(x)))})
            continue
        root=read_xml(path)
        if root is None:continue
        records=defaultdict(lambda:{'refs':set(),'terms':set(),'ids':set()})
        def walk(node,current=None):
            name=node.attrib.get('name','')
            if NUMERIC_RE.fullmatch(name) and len(name)>=7: current=name
            local=local_text(node)
            if current:
                rec=records[current]; rec['ids'].update(NUM_RE.findall(local)); rec['refs'].update(pat.findall(local)); rec['terms'].update(term_hits(local))
            for child in list(node): walk(child,current)
        walk(root)
        for cid,rec in records.items():
            if not rec['refs'] and not rec['terms']:continue
            rec['ids'].add(cid); discovered.update(rec['ids'])
            rows.append({'path':str(path.relative_to(core)),'fileId':file_id,'contentId':cid,'anchorRefs':sorted(rec['refs'],key=lambda x:(len(x),x)),'termHits':sorted(rec['terms']),'ids':sorted(rec['ids'],key=lambda x:(len(x),int(x)))})
    rows.sort(key=lambda r:(r['path'],int(r['contentId'])))
    return rows,discovered

def family_evidence(core:Path,family:str,anchors:set[str]):
    return item_evidence(core,anchors) if family=='Item.wz' else standalone_family_evidence(core,family,anchors)

def baseline_evidence(baseline:Path,anchors:set[str]):
    rows=[]; pat=anchor_pattern(anchors)
    if pat is None:return rows
    for p in baseline.rglob('*'):
        if not p.is_file() or p.suffix.lower() not in {'.xml','.js','.java','.sql','.txt','.json','.py'}:continue
        text=read_text(p); refs=sorted(set(pat.findall(text)),key=lambda x:(len(x),x)); hits=term_hits(text)
        if refs or hits:rows.append({'path':str(p.relative_to(baseline)),'anchorRefs':refs,'termHits':hits})
    return rows

def build(core:Path,string_root:Path,baseline:Path|None):
    skills,skill_ids,job_files=skill_evidence(core)
    strings,string_ids=string_evidence(string_root,set(EVAN_JOB_IDS)|skill_ids)
    primary=set(EVAN_JOB_IDS)|skill_ids|string_ids
    quests=quest_evidence(core,primary); quest_ids={r['questId'] for r in quests}; linked=primary|quest_ids
    families={}; discovered=set(linked)
    for fam in FAMILIES:
        rows,ids=family_evidence(core,fam,linked); families[fam]=rows; discovered.update(ids)
    baseline_rows=baseline_evidence(baseline,primary|quest_ids) if baseline else []
    counts={'stringNodes':len(strings),'skillJobFiles':len(job_files),'skillIds':len(skill_ids),'quests':len(quests),
            'npcNodes':len(families['Npc.wz']),'mapNodes':len(families['Map.wz']),'mobNodes':len(families['Mob.wz']),
            'itemNodes':len(families['Item.wz']),'baselineFiles':len(baseline_rows),'discoveredNumericIds':len(discovered)}
    return {'schemaVersion':3,'kind':'gms-v95-evan-comprehensive-review-profile','donorId':'gms-v95.4',
            'search':{'jobIds':sorted(EVAN_JOB_IDS,key=int),'textTerms':list(TEXT_TERMS)},'counts':counts,
            'skillJobIds':sorted(job_files,key=int),'skillIds':sorted(skill_ids,key=int),'strings':strings,'quests':quests,
            'families':families,'baselineMatches':baseline_rows,'discoveredNumericIds':sorted(discovered,key=lambda x:(len(x),int(x))),
            'limitations':['Character.wz is excluded because the SourceForge v95.4 Character archive remains unparsable by the current MapleLib pipeline.',
                           'This extraction captures donor XML relationships and text, not runtime correctness or client protocol behavior.',
                           'Generic dragon-related text can still require manual review; nothing is auto-approved.'],
            'approved':False,'importAllowed':False,'automaticImport':False}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--core',type=Path,required=True); ap.add_argument('--strings',type=Path,required=True); ap.add_argument('--baseline',type=Path); ap.add_argument('--output',type=Path,required=True); a=ap.parse_args()
    r=build(a.core,a.strings,a.baseline); a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(json.dumps(r,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps(r['counts'],sort_keys=True)); print('skill jobs:',','.join(r['skillJobIds'])); print('approved=false / importAllowed=false / automaticImport=false'); return 0
if __name__=='__main__': raise SystemExit(main())
