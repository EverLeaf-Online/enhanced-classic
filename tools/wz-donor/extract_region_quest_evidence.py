#!/usr/bin/env python3
"""Extract review-only quest/NPC evidence from donor Quest.wz + String.wz XML."""
from __future__ import annotations
import argparse, json, xml.etree.ElementTree as ET
from pathlib import Path


def semantic(node):
    return {
        "tag": node.tag,
        "attributes": dict(sorted(node.attrib.items())),
        "children": [semantic(c) for c in list(node)],
    }


def find_named_nodes(root: Path, ids: set[str]):
    found={x:[] for x in ids}
    if not root.exists(): return found
    for path in root.rglob('*.xml'):
        try: tree=ET.parse(path).getroot()
        except (ET.ParseError,OSError): continue
        for node in tree.iter():
            name=node.attrib.get('name')
            if name in ids:
                found[name].append({"path":path.relative_to(root).as_posix(),"node":semantic(node)})
    return found


def quest_components(quest_root: Path, quest_ids: set[str]):
    result={qid:{} for qid in quest_ids}
    if not quest_root.exists(): return result
    for path in quest_root.rglob('*.xml'):
        try: tree=ET.parse(path).getroot()
        except (ET.ParseError,OSError): continue
        for node in tree.iter():
            qid=node.attrib.get('name')
            if qid in quest_ids:
                rel=path.relative_to(quest_root).as_posix()
                result[qid].setdefault(rel,[]).append(semantic(node))
    return result


def build_report(quest_root:Path,string_root:Path,quest_ids:list[str],npc_ids:list[str]):
    quests={str(x) for x in quest_ids}; npcs={str(x) for x in npc_ids}
    return {
        "schemaVersion":1,
        "kind":"review-only-region-quest-evidence",
        "questIds":sorted(quests,key=int),
        "npcIds":sorted(npcs,key=int),
        "questComponents":quest_components(quest_root,quests),
        "questStringHits":find_named_nodes(string_root,quests),
        "npcStringHits":find_named_nodes(string_root,npcs),
        "approved":False,
        "importAllowed":False,
        "automaticImport":False,
        "note":"Evidence extraction only. Does not synthesize or install NPC/quest scripts."
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--quest-root',type=Path,required=True)
    p.add_argument('--string-root',type=Path,required=True)
    p.add_argument('--quest-ids',nargs='+',required=True)
    p.add_argument('--npc-ids',nargs='+',required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    r=build_report(a.quest_root,a.string_root,a.quest_ids,a.npc_ids)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(r,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print('quests:',len(r['questIds']))
    print('quest components:',sum(bool(v) for v in r['questComponents'].values()))
    print('quest string hits:',sum(len(v) for v in r['questStringHits'].values()))
    print('npc string hits:',sum(len(v) for v in r['npcStringHits'].values()))
    print('approved=false / importAllowed=false / automaticImport=false')
    return 0

if __name__=='__main__': raise SystemExit(main())
