#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv,json,re,xml.etree.ElementTree as ET
from pathlib import Path

ID_RE=re.compile(r'(?<!\d)(\d{7,8})(?!\d)')
REF_KEYS={'buffitemid','statechangeitem','item','create','mob','npc','script','id'}

def build_string_index(root:Path):
    out={}
    for f in root.glob('*.xml'):
        try:r=ET.parse(f).getroot()
        except ET.ParseError: continue
        for e in r.iter('imgdir'):
            n=e.get('name','')
            if not (n.isdigit() and len(n)>=5): continue
            vals={}
            for c in e:
                if c.tag.lower()=='string': vals[(c.get('name') or '').lower()]=c.get('value','')
            if vals.get('name'):
                out[int(n)]={'name':vals.get('name',''),'desc':vals.get('desc',''),'stringFile':f.name}
    return out

def build_item_nodes(root:Path,wanted:set[int]):
    out={}
    for f in root.rglob('*.xml'):
        try:r=ET.parse(f).getroot()
        except ET.ParseError: continue
        for e in r.iter('imgdir'):
            n=e.get('name','')
            if n.isdigit() and int(n) in wanted: out[int(n)]=(f,e)
    return out

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--review-csv',required=True)
    ap.add_argument('--item-root',required=True)
    ap.add_argument('--string-root',required=True)
    ap.add_argument('--output-json',required=True)
    ap.add_argument('--output-csv',required=True)
    args=ap.parse_args()
    rows=list(csv.DictReader(open(args.review_csv,encoding='utf-8')))
    wanted={int(r['ID']) for r in rows}
    strings=build_string_index(Path(args.string_root)); nodes=build_item_nodes(Path(args.item_root),wanted)
    enriched=[]; report=[]; positive=0
    for row in rows:
        iid=int(row['ID']); refs=[]
        if iid in nodes:
            _,e=nodes[iid]
            for x in e.iter():
                key=(x.get('name') or ''); val=x.get('value')
                if not val: continue
                for m in ID_RE.finditer(val):
                    rid=int(m.group(1))
                    if rid==iid: continue
                    s=strings.get(rid)
                    refs.append({'via':key,'refId':rid,'refName':s['name'] if s else '','refDesc':s['desc'] if s else '','raw':val})
                if key.lower() in REF_KEYS and val.isdigit():
                    rid=int(val); s=strings.get(rid)
                    refs.append({'via':key,'refId':rid,'refName':s['name'] if s else '','refDesc':s['desc'] if s else '','raw':val})
        seen=set(); ded=[]
        for q in refs:
            k=(q['via'],q['refId'],q['raw'])
            if k not in seen: seen.add(k); ded.append(q)
        named=[q for q in ded if q['refName']]
        if named: positive+=1
        row2=dict(row)
        row2['NamedReferenceCount']=str(len(named))
        row2['NamedReferences']=' | '.join(f"{q['via']}:{q['refId']}={q['refName']}" for q in named)
        row2['ReferenceResolutionStatus']='HAS_NAMED_REFERENCE' if named else 'NO_NAMED_REFERENCE'
        enriched.append(row2)
        report.append({'ID':iid,'Category':row.get('Category',''),'NamedReferences':named,'AllReferences':ded})
    fields=list(rows[0].keys())+['NamedReferenceCount','NamedReferences','ReferenceResolutionStatus']
    with open(args.output_csv,'w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(enriched)
    summary={'reviewCount':len(rows),'idsWithNamedReferences':positive,'noNamedReferences':len(rows)-positive,'productionApplyAllowed':False,'items':report}
    Path(args.output_json).write_text(json.dumps(summary,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in summary.items() if k!='items'},indent=2))
if __name__=='__main__': main()
