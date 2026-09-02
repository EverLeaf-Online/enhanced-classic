#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, re, xml.etree.ElementTree as ET
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

def node_blob(node:ET.Element)->str:
    parts=[]
    for child in node.iter():
        parts.extend((child.attrib.get('name',''),child.attrib.get('value',''),child.text or ''))
    return ' '.join(parts)

def term_hits(text:str):
    low=text.lower(); hits=[]
    for term in TEXT_TERMS:
        if term=='mir':
            if re.search(r'(?<![a-z])mir(?![a-z])',low): hits.append(term)
        elif term in low: hits.append(term)
    return sorted(set(hits))

def numeric_node_matches(root:ET.Element,predicate,initial_numeric:str|None=None,min_digits:int=1):
    # Standalone WZ files (Map/Npc/Mob etc.) are one content record: scan the root once.
    if initial_numeric is not None:
        blob=node_blob(root)
        return {initial_numeric:blob} if predicate(blob) else {}
    # Grouped files (String/Item containers): scan numeric content entries only, not every descendant.
    out={}
    for node in root.iter():
        name=node.attrib.get('name','')
        if not NUMERIC_RE.fullmatch(name) or len(name)<min_digits: continue
        blob=node_blob(node)
        if predicate(blob): out[name]=blob
    return out

def string_evidence(string_root:Path):
    rows=[]; ids=set()
    for path in iter_xml(string_root):
        root=read_xml(path)
        if root is None: continue
        matches=numeric_node_matches(root,lambda b: bool(term_hits(b)),min_digits=4)
        for cid,blob in matches.items():
            hits=term_hits(blob)
            if not hits: continue
            ids.add(cid)
            rows.append({'path':str(path.relative_to(string_root)),'contentId':cid,'terms':hits,'text':blob[:1200]})
    rows.sort(key=lambda r:(r['path'],int(r['contentId']) if r['contentId'].isdigit() else 10**12))
    return rows,ids

def skill_evidence(core:Path):
    base=family_base(core,'Skill.wz'); rows=[]; skill_ids=set(); job_files=set()
    for path in iter_xml(base):
        stem=path.name.removesuffix('.img.xml')
        if stem not in EVAN_JOB_IDS: continue
        root=read_xml(path)
        if root is None: continue
        job_files.add(stem)
        ids=set()
        for node in root.iter():
            name=node.attrib.get('name','')
            if name.isdigit() and (name.startswith(stem) or len(name)>=7): ids.add(name)
        skill_ids.update(ids)
        rows.append({'path':str(path.relative_to(core)),'jobId':stem,'skillIds':sorted(ids,key=int)})
    rows.sort(key=lambda r:int(r['jobId']))
    return rows,skill_ids,job_files

def quest_evidence(core:Path,anchors:set[str]):
    base=family_base(core,'Quest.wz'); rows={}
    if not anchors:return []
    pat=re.compile(r"(?<!\d)(?:"+'|'.join(re.escape(x) for x in sorted(anchors,key=len,reverse=True))+r")(?!\d)")
    for path in iter_xml(base):
        root=read_xml(path)
        if root is None: continue
        def walk(node,quest_id=None):
            name=node.attrib.get('name',''); q=quest_id
            if q is None and name.isdigit() and int(name)>=QUEST_ID_MIN: q=name
            local=' '.join((node.attrib.get('value',''),node.text or ''))
            found=set(pat.findall(local))
            if found and q:
                row=rows.setdefault(q,{'questId':q,'paths':set(),'anchorRefs':set(),'ids':set()})
                row['paths'].add(str(path.relative_to(core))); row['anchorRefs'].update(found); row['ids'].update(NUM_RE.findall(node_blob(node)))
            for child in list(node): walk(child,q)
        walk(root)
    result=[]
    for q,row in sorted(rows.items(),key=lambda kv:int(kv[0])):
        result.append({'questId':q,'paths':sorted(row['paths']),'anchorRefs':sorted(row['anchorRefs'],key=lambda x:(len(x),x)),'ids':sorted(row['ids'],key=lambda x:(len(x),int(x)))})
    return result

def family_evidence(core:Path,family:str,anchors:set[str]):
    base=family_base(core,family); rows=[]; discovered=set()
    if not anchors:return rows,discovered
    pat=re.compile(r"(?<!\d)(?:"+'|'.join(re.escape(x) for x in sorted(anchors,key=len,reverse=True))+r")(?!\d)")
    for path in iter_xml(base):
        root=read_xml(path)
        if root is None: continue
        file_id=None; m=FILE_ID_RE.match(path.name)
        if m:file_id=m.group(1)
        min_digits=4 if family=='Item.wz' and file_id is None else 1
        matches=numeric_node_matches(root,lambda b: bool(pat.search(b)) or bool(term_hits(b)),file_id,min_digits=min_digits)
        for cid,blob in matches.items():
            refs=sorted(set(pat.findall(blob)),key=lambda x:(len(x),x)); hits=term_hits(blob)
            if not refs and not hits:continue
            local=set(NUM_RE.findall(blob)); discovered.update(local); discovered.add(cid)
            rows.append({'path':str(path.relative_to(core)),'fileId':file_id,'contentId':cid,'anchorRefs':refs,'termHits':hits,'ids':sorted(local,key=lambda x:(len(x),int(x)))})
    rows.sort(key=lambda r:(r['path'],int(r['contentId']) if r['contentId'].isdigit() else 10**12))
    return rows,discovered

def baseline_evidence(baseline:Path,anchors:set[str]):
    rows=[]
    if not anchors:return rows
    pat=re.compile(r"(?<!\d)(?:"+'|'.join(re.escape(x) for x in sorted(anchors,key=len,reverse=True))+r")(?!\d)")
    for p in baseline.rglob('*'):
        if not p.is_file() or p.suffix.lower() not in {'.xml','.js','.java','.sql','.txt','.json','.py'}:continue
        try:text=p.read_text(encoding='utf-8',errors='ignore')
        except OSError:continue
        refs=sorted(set(pat.findall(text)),key=lambda x:(len(x),x)); hits=term_hits(text)
        if refs or hits:rows.append({'path':str(p.relative_to(baseline)),'anchorRefs':refs,'termHits':hits})
    return rows

def build(core:Path,string_root:Path,baseline:Path|None):
    strings,string_ids=string_evidence(string_root)
    skills,skill_ids,job_files=skill_evidence(core)
    primary=set(EVAN_JOB_IDS)|skill_ids|string_ids
    quests=quest_evidence(core,primary)
    quest_ids={r['questId'] for r in quests}
    linked=set(primary)|quest_ids
    families={}; discovered=set(linked)
    for fam in FAMILIES:
        rows,ids=family_evidence(core,fam,linked); families[fam]=rows; discovered.update(ids)
    baseline_rows=baseline_evidence(baseline,primary|quest_ids) if baseline else []
    counts={'stringNodes':len(strings),'skillJobFiles':len(job_files),'skillIds':len(skill_ids),'quests':len(quests),
            'npcNodes':len(families['Npc.wz']),'mapNodes':len(families['Map.wz']),'mobNodes':len(families['Mob.wz']),
            'itemNodes':len(families['Item.wz']),'baselineFiles':len(baseline_rows),'discoveredNumericIds':len(discovered)}
    return {'schemaVersion':2,'kind':'gms-v95-evan-comprehensive-review-profile','donorId':'gms-v95.4',
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
