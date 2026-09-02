#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, re, xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path

EVAN_JOB_IDS={"2001","2200","2210","2211","2212","2213","2214","2215","2216","2217","2218"}
EVAN_SKILL_PREFIXES=tuple(sorted(EVAN_JOB_IDS))
TEXT_TERMS=("evan","mir","dragon master","onyx dragon","dragon rider")
NUM_RE=re.compile(r"(?<!\d)(\d{3,10})(?!\d)")
FILE_ID_RE=re.compile(r"^(\d+)\.img\.xml$")

FAMILIES=("Skill.wz","Quest.wz","Npc.wz","Map.wz","Mob.wz","Item.wz")

def family_base(root:Path,family:str)->Path:
    direct=root/family
    return direct if direct.exists() else root/'wz'/family

def iter_xml(root:Path):
    for p in root.rglob('*.xml'):
        if p.is_file(): yield p

def text_of(path:Path)->str:
    try:return path.read_text(encoding='utf-8',errors='ignore')
    except OSError:return ''

def add_refs(text:str, bucket:set[str]):
    bucket.update(NUM_RE.findall(text))

def string_matches(string_root:Path):
    matches=[]; ids=set()
    for p in iter_xml(string_root):
        text=text_of(p); low=text.lower()
        if not any(t in low for t in TEXT_TERMS): continue
        hit_terms=sorted({t for t in TEXT_TERMS if t in low})
        local_ids=set(NUM_RE.findall(text)); ids.update(local_ids)
        matches.append({'path':str(p.relative_to(string_root.parent)),'terms':hit_terms,'ids':sorted(local_ids,key=lambda x:(len(x),x))})
    return matches,ids

def skill_matches(skill_root:Path):
    rows=[]; ids=set(); jobs=set()
    for p in iter_xml(skill_root):
        stem=p.name.removesuffix('.img.xml')
        text=text_of(p); low=text.lower()
        job_match=stem in EVAN_JOB_IDS or any(stem.startswith(pref) for pref in EVAN_SKILL_PREFIXES)
        term_match=any(t in low for t in TEXT_TERMS)
        if not(job_match or term_match): continue
        local=set(NUM_RE.findall(text)); ids.update(local)
        if stem.isdigit(): jobs.add(stem)
        rows.append({'path':str(p.relative_to(skill_root.parent)),'jobOrFileId':stem,'termMatch':term_match,'ids':sorted(local,key=lambda x:(len(x),x))})
    return rows,ids,jobs

def family_refs(root:Path, family:str, anchors:set[str]):
    base=family_base(root,family); rows=[]; found_ids=set()
    if not base.exists(): return rows,found_ids
    if not anchors:return rows,found_ids
    pat=re.compile(r"(?<!\d)(?:"+'|'.join(re.escape(x) for x in sorted(anchors,key=len,reverse=True))+r")(?!\d)")
    for p in iter_xml(base):
        text=text_of(p); low=text.lower()
        refs=sorted(set(pat.findall(text)),key=lambda x:(len(x),x))
        term_hits=sorted({t for t in TEXT_TERMS if t in low})
        if not refs and not term_hits: continue
        file_id=None; m=FILE_ID_RE.match(p.name)
        if m:file_id=m.group(1); found_ids.add(file_id)
        local=set(NUM_RE.findall(text)); found_ids.update(local)
        rows.append({'path':str(p.relative_to(root)),'fileId':file_id,'anchorRefs':refs,'termHits':term_hits,'ids':sorted(local,key=lambda x:(len(x),x))})
    return rows,found_ids

def compact_ids(ids:set[str]):
    return sorted(ids,key=lambda x:(len(x),int(x) if x.isdigit() else x))

def build(core:Path,string_root:Path,baseline:Path|None):
    srows,sids=string_matches(string_root)
    skill_root=family_base(core,'Skill.wz')
    skill_rows,skill_ids,skill_jobs=skill_matches(skill_root)
    anchors=set(EVAN_JOB_IDS)|sids|skill_ids
    family_data={}; discovered=set(anchors)
    # Two passes to pull direct and then linked references without exploding to the entire donor.
    for _ in range(2):
        before=len(discovered)
        for fam in FAMILIES:
            if fam=='Skill.wz': continue
            rows,ids=family_refs(core,fam,discovered)
            family_data[fam]=rows; discovered.update(ids)
        if len(discovered)==before: break
    baseline_hits=[]
    if baseline:
        needles=set(EVAN_JOB_IDS)|sids|skill_ids
        if needles:
            pat=re.compile(r"(?<!\d)(?:"+'|'.join(re.escape(x) for x in sorted(needles,key=len,reverse=True))+r")(?!\d)")
            for p in baseline.rglob('*'):
                if not p.is_file() or p.suffix.lower() not in {'.xml','.js','.java','.sql','.txt','.json','.py'}: continue
                text=text_of(p); low=text.lower(); refs=sorted(set(pat.findall(text)),key=lambda x:(len(x),x)); terms=sorted({t for t in TEXT_TERMS if t in low})
                if refs or terms: baseline_hits.append({'path':str(p.relative_to(baseline)),'anchorRefs':refs,'termHits':terms})
    counts={
        'stringFiles':len(srows),'skillFiles':len(skill_rows),'skillJobFiles':len(skill_jobs),
        'questFiles':len(family_data.get('Quest.wz',[])),'npcFiles':len(family_data.get('Npc.wz',[])),
        'mapFiles':len(family_data.get('Map.wz',[])),'mobFiles':len(family_data.get('Mob.wz',[])),
        'itemFiles':len(family_data.get('Item.wz',[])),'baselineFiles':len(baseline_hits),
        'discoveredNumericIds':len(discovered)
    }
    return {
        'schemaVersion':1,'kind':'gms-v95-evan-comprehensive-review-profile','donorId':'gms-v95.4',
        'search':{'jobIds':sorted(EVAN_JOB_IDS,key=int),'textTerms':list(TEXT_TERMS),'passes':2},
        'counts':counts,'skillJobIds':sorted(skill_jobs,key=lambda x:int(x) if x.isdigit() else 10**9),
        'stringMatches':srows,'skillMatches':skill_rows,'families':family_data,
        'baselineMatches':baseline_hits,'discoveredNumericIds':compact_ids(discovered),
        'limitations':[
            'Character.wz is not included because the SourceForge v95.4 Character archive remains unparsable by the current MapleLib pipeline.',
            'This is a review/extraction report, not an import manifest and not proof of runtime compatibility.',
            'Textual Mir/dragon matches may include non-Evan content; linked IDs are retained for manual review rather than auto-approved.'
        ],
        'approved':False,'importAllowed':False,'automaticImport':False
    }

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--core',type=Path,required=True); ap.add_argument('--strings',type=Path,required=True); ap.add_argument('--baseline',type=Path); ap.add_argument('--output',type=Path,required=True); a=ap.parse_args()
    report=build(a.core,a.strings,a.baseline)
    a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps(report['counts'],sort_keys=True)); print('skill jobs:',','.join(report['skillJobIds'])); print('approved=false / importAllowed=false / automaticImport=false')
    return 0
if __name__=='__main__': raise SystemExit(main())
