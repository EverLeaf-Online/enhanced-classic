#!/usr/bin/env python3
"""Extract review-only quest/NPC evidence from donor Quest.wz + String.wz XML."""
from __future__ import annotations
import argparse, json, xml.etree.ElementTree as ET
from collections import deque
from pathlib import Path

QUEST_ID_MIN=100


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


def index_quest_nodes(quest_root: Path):
    """Index plausible quest-id nodes across Quest.wz by quest id and source file."""
    result={}
    if not quest_root.exists(): return result
    for path in quest_root.rglob('*.xml'):
        try: tree=ET.parse(path).getroot()
        except (ET.ParseError,OSError): continue
        rel=path.relative_to(quest_root).as_posix()
        for node in tree.iter():
            name=node.attrib.get('name')
            if not name or not name.isdigit() or int(name)<QUEST_ID_MIN: continue
            result.setdefault(name,{}).setdefault(rel,[]).append(node)
    return result


def quest_condition_refs(node):
    """Return quest ids referenced inside Quest.wz `quest` condition containers."""
    refs=set()
    for container in node.iter():
        if container.attrib.get('name')!='quest': continue
        for row in list(container):
            values={c.attrib.get('name'):c.attrib.get('value') for c in list(row)}
            qid=values.get('id')
            if qid and qid.isdigit() and int(qid)>=QUEST_ID_MIN: refs.add(qid)
    return refs


def quest_npcs(check_nodes):
    npcs=set()
    for node in check_nodes:
        for child in node.iter():
            if child.attrib.get('name')=='npc':
                value=child.attrib.get('value')
                if value and value.isdigit(): npcs.add(value)
    return npcs


def expand_quest_closure(quest_index, seed_ids:set[str]):
    quests=set(seed_ids); queue=deque(sorted(quests,key=int)); edges={}
    while queue:
        qid=queue.popleft(); refs=set()
        for node in quest_index.get(qid,{}).get('Check.img.xml',[]): refs.update(quest_condition_refs(node))
        existing=sorted((x for x in refs if x in quest_index),key=int)
        edges[qid]=existing
        for dep in existing:
            if dep not in quests:
                quests.add(dep); queue.append(dep)
    return quests,{k:v for k,v in sorted(edges.items(),key=lambda kv:int(kv[0])) if v}


def quest_components_from_index(quest_index,quest_ids:set[str]):
    result={qid:{} for qid in quest_ids}
    for qid in quest_ids:
        for rel,nodes in quest_index.get(qid,{}).items():
            result[qid][rel]=[semantic(node) for node in nodes]
    return result


def build_report(quest_root:Path,string_root:Path,quest_ids:list[str],npc_ids:list[str]|None=None):
    seeds={str(x) for x in quest_ids}; quest_index=index_quest_nodes(quest_root)
    quests,prereq_edges=expand_quest_closure(quest_index,seeds)
    npcs={str(x) for x in (npc_ids or [])}
    for qid in quests: npcs.update(quest_npcs(quest_index.get(qid,{}).get('Check.img.xml',[])))
    added_quests=quests-seeds
    return {
        "schemaVersion":2,
        "kind":"review-only-region-quest-evidence",
        "seedQuestIds":sorted(seeds,key=int),
        "questIds":sorted(quests,key=int),
        "prerequisiteQuestIds":sorted(added_quests,key=int),
        "prerequisiteEdges":prereq_edges,
        "npcIds":sorted(npcs,key=int),
        "questComponents":quest_components_from_index(quest_index,quests),
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
    p.add_argument('--npc-ids',nargs='*',default=[])
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    r=build_report(a.quest_root,a.string_root,a.quest_ids,a.npc_ids)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(r,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print('seed quests:',len(r['seedQuestIds']))
    print('quest closure:',len(r['questIds']))
    print('prerequisite quests added:',len(r['prerequisiteQuestIds']))
    print('quest components:',sum(bool(v) for v in r['questComponents'].values()))
    print('NPC closure:',len(r['npcIds']))
    print('quest string hits:',sum(len(v) for v in r['questStringHits'].values()))
    print('npc string hits:',sum(len(v) for v in r['npcStringHits'].values()))
    print('approved=false / importAllowed=false / automaticImport=false')
    return 0

if __name__=='__main__': raise SystemExit(main())
