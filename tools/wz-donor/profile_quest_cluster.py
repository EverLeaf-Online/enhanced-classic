#!/usr/bin/env python3
"""Extract review-only Quest.wz evidence for a pinned content cluster."""
from __future__ import annotations
import argparse, json, xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path


def family_base(root: Path, family: str) -> Path:
    direct = root / family
    return direct if direct.exists() else root / 'wz' / family


def flatten(node: ET.Element, prefix: tuple[str, ...] = ()) -> list[dict]:
    name = node.attrib.get('name')
    path = prefix + ((name,) if name is not None else ())
    rows = []
    value = node.attrib.get('value')
    if value is not None:
        rows.append({'path': '/'.join(path), 'tag': node.tag, 'name': name, 'value': value})
    for child in list(node):
        rows.extend(flatten(child, path))
    return rows


def find_quest_nodes(quest_root: Path, quest_ids: set[str]) -> dict[str, list[dict]]:
    found = defaultdict(list)
    for file in sorted(quest_root.rglob('*.xml')):
        try:
            root = ET.parse(file).getroot()
        except (OSError, ET.ParseError):
            continue
        def walk(node: ET.Element, ancestors: tuple[str, ...]) -> None:
            name = node.attrib.get('name')
            next_anc = ancestors + ((name,) if name is not None else ())
            if name in quest_ids:
                found[name].append({
                    'file': file.relative_to(quest_root).as_posix(),
                    'ancestorPath': '/'.join(ancestors),
                    'properties': flatten(node),
                })
                return
            for child in list(node):
                walk(child, next_anc)
        walk(root, ())
    return {qid: found.get(qid, []) for qid in sorted(quest_ids, key=int)}


def classify_refs(nodes: list[dict]) -> dict:
    refs = defaultdict(set)
    for occurrence in nodes:
        for row in occurrence['properties']:
            value = row['value']
            name = (row.get('name') or '').lower()
            if not value.lstrip('-').isdigit():
                continue
            n = int(value)
            if 'npc' in name or name in {'start', 'end'} and 1_000_000 <= n < 10_000_000:
                refs['npcIds'].add(value)
            if 'mob' in name or name in {'id'} and 1_000_000 <= n < 10_000_000:
                refs['mobOrNpcIds'].add(value)
            if 'item' in name or name in {'id'} and 1_000_000 <= n < 10_000_000:
                refs['itemOrEntityIds'].add(value)
            if 'map' in name or name in {'field'}:
                refs['mapIds'].add(value)
            if name in {'job', 'jobid'}:
                refs['jobIds'].add(value)
            if name in {'lvmin', 'lvmax', 'levelmin', 'levelmax'}:
                refs['levelValues'].add(value)
    return {k: sorted(v, key=lambda x: int(x)) for k, v in sorted(refs.items())}


def build_report(manifest: dict, donor_root: Path, baseline_root: Path) -> dict:
    quest_ids = {str(q) for q in manifest.get('questIds', [])}
    donor_quest = family_base(donor_root, 'Quest.wz')
    baseline_quest = family_base(baseline_root, 'Quest.wz')
    donor_nodes = find_quest_nodes(donor_quest, quest_ids)
    baseline_nodes = find_quest_nodes(baseline_quest, quest_ids)
    rows = []
    for qid in sorted(quest_ids, key=int):
        donor = donor_nodes[qid]
        baseline = baseline_nodes[qid]
        rows.append({
            'questId': qid,
            'donorOccurrences': donor,
            'donorOccurrenceCount': len(donor),
            'baselineOccurrenceCount': len(baseline),
            'needsBackport': bool(donor) and not bool(baseline),
            'baselineQuestScriptExists': (baseline_root / 'scripts' / 'quest' / f'{qid}.js').is_file(),
            'referenceSummary': classify_refs(donor),
            'approved': False,
            'importAllowed': False,
        })
    return {
        'schemaVersion': 1,
        'kind': 'review-only-quest-cluster-profile',
        'clusterId': manifest.get('clusterId'),
        'donorId': manifest.get('donorId'),
        'questCount': len(rows),
        'questsFoundInDonor': sum(bool(r['donorOccurrenceCount']) for r in rows),
        'questsAlreadyInBaseline': sum(bool(r['baselineOccurrenceCount']) for r in rows),
        'baselineQuestScripts': sum(r['baselineQuestScriptExists'] for r in rows),
        'quests': rows,
        'approved': False,
        'automaticImport': False,
        'note': 'Raw flattened Quest.wz subtree evidence for manual review; field classification is advisory and never authorizes import.',
    }


def main() -> int:
    p=argparse.ArgumentParser(); p.add_argument('manifest',type=Path); p.add_argument('--donor',type=Path,required=True); p.add_argument('--baseline',type=Path,required=True); p.add_argument('--output',type=Path,required=True); a=p.parse_args()
    r=build_report(json.loads(a.manifest.read_text(encoding='utf-8')),a.donor,a.baseline); a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(json.dumps(r,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(f"quests={r['questCount']} donor={r['questsFoundInDonor']} baseline={r['questsAlreadyInBaseline']} scripts={r['baselineQuestScripts']}")
    for q in r['quests']: print(q['questId'], q['donorOccurrenceCount'], q['baselineOccurrenceCount'], q['baselineQuestScriptExists'])
    print('approved=false / automaticImport=false'); return 0
if __name__=='__main__': raise SystemExit(main())
