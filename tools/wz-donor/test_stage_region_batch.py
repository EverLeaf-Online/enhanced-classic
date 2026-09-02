#!/usr/bin/env python3
from __future__ import annotations
import json,tempfile
from pathlib import Path
from stage_region_batch import stage,semantic_hash,tree_digest

def write(p:Path,s:str):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s,encoding='utf-8')
def main():
    with tempfile.TemporaryDirectory() as t:
        r=Path(t);donor=r/'donor';string=r/'string';canonical=r/'canonical';staging=r/'staging';contract=r/'contract.json'
        write(donor/'Map.wz'/'Map8'/'800040000.img.xml','<imgdir name="800040000.img"><int name="x" value="1"/></imgdir>')
        write(donor/'Mob.wz'/'9400408.img.xml','<imgdir name="9400408.img"><imgdir name="info"><imgdir name="revive"><int name="0" value="9400409"/></imgdir></imgdir></imgdir>')
        write(donor/'Mob.wz'/'9400409.img.xml','<imgdir name="9400409.img"/>')
        write(donor/'Npc.wz'/'9110100.img.xml','<imgdir name="9110100.img"><string name="new" value="castle"/></imgdir>')
        write(donor/'Item.wz'/'Etc'/'0400.img.xml','<imgdir name="0400.img"><imgdir name="04000337"><imgdir name="info"><int name="price" value="1"/></imgdir></imgdir></imgdir>')
        for f in ('Check.img.xml','Act.img.xml','QuestInfo.img.xml'):write(donor/'Quest.wz'/f,f'<imgdir name="{f[:-4]}"><imgdir name="0"><imgdir name="8163"><int name="x" value="1"/></imgdir></imgdir></imgdir>')
        write(string/'String.wz'/'Etc.img.xml','<imgdir name="Etc.img"><imgdir name="4000337"><string name="name" value="Genin Doll"/></imgdir></imgdir>')
        write(string/'String.wz'/'Map.img.xml','<imgdir name="Map.img"><imgdir name="Japan"><imgdir name="800040000"><string name="mapName" value="Castle"/></imgdir></imgdir></imgdir>')
        write(string/'String.wz'/'Mob.img.xml','<imgdir name="Mob.img"><imgdir name="9400408"><string name="name" value="Mob A"/></imgdir><imgdir name="9400409"><string name="name" value="Mob B"/></imgdir></imgdir>')
        write(string/'String.wz'/'Npc.img.xml','<imgdir name="Npc.img"><imgdir name="9110100"><string name="name" value="Castle NPC"/></imgdir></imgdir>')
        # Deliberately omit String.wz/Quest.img.xml: the real v95 String donor has no quest string family.
        write(canonical/'Npc.wz'/'9110100.img.xml','<imgdir name="9110100.img"><string name="old" value="charity"/></imgdir>');write(canonical/'Item.wz'/'Etc'/'0400.img.xml','<imgdir name="0400.img"/>')
        for f in ('Check.img.xml','Act.img.xml','QuestInfo.img.xml'):write(canonical/'Quest.wz'/f,f'<imgdir name="{f[:-4]}"><imgdir name="0"/></imgdir>')
        write(canonical/'String.wz'/'Etc.img.xml','<imgdir name="Etc.img"/>');write(canonical/'String.wz'/'Map.img.xml','<imgdir name="Map.img"/>');write(canonical/'String.wz'/'Mob.img.xml','<imgdir name="Mob.img"/>');write(canonical/'String.wz'/'Npc.img.xml','<imgdir name="Npc.img"><imgdir name="9110100"><string name="name" value="Charity Box"/></imgdir></imgdir>')
        baseline_fp=semantic_hash(canonical/'Npc.wz'/'9110100.img.xml');donor_fp=semantic_hash(donor/'Npc.wz'/'9110100.img.xml');c={'batchId':'fixture','approved':False,'importAllowed':False,'automaticImport':False,'productionApplyAllowed':False,'maps':['800040000'],'mobs':['9400408','9400409'],'castleNpcs':['9110100'],'items':['4000337'],'questIds':['8163'],'deliberateReplacementCollisions':[{'contentId':'9110100','baselineFingerprint':baseline_fp,'donorFingerprint':donor_fp}]};contract.write_text(json.dumps(c),encoding='utf-8')
        before=tree_digest(canonical);report=stage(contract,donor,string,canonical,staging)
        assert report['canonicalMutated'] is False and tree_digest(canonical)==before
        assert [x['contentId'] for x in report['fullFileChanges']]==['800040000','9400408','9400409','9110100'];assert report['fullFileChanges'][-1]['action']=='replace'
        assert len(report['itemNodes'])==1 and report['itemNodes'][0]['contentId']=='4000337' and report['itemNodes'][0]['sourceNodeName']=='04000337'
        assert {x['contentId'] for x in report['questNodes']}=={'8163'}
        assert {x['contentId'] for x in report['stringNodes']}=={'4000337','800040000','9400408','9400409','9110100'}
        assert semantic_hash(staging/'Npc.wz'/'9110100.img.xml')==donor_fp;assert report['productionApplyAllowed'] is False and report['approved'] is False
    print('regional staging regression: PASS');return 0
if __name__=='__main__':raise SystemExit(main())
