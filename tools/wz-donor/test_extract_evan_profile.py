#!/usr/bin/env python3
from __future__ import annotations
import tempfile
from pathlib import Path
from extract_evan_profile import build

def write(path:Path,text:str):
    path.parent.mkdir(parents=True,exist_ok=True); path.write_text(text,encoding='utf-8')

def main()->int:
    with tempfile.TemporaryDirectory() as td:
        root=Path(td); core=root/'core'; strings=root/'strings'/'String.wz'; baseline=root/'baseline'
        write(core/'Skill.wz'/'2210.img.xml','<imgdir name="2210.img"><imgdir name="skill"><imgdir name="22101001"><int name="x" value="1"/></imgdir></imgdir></imgdir>')
        write(strings/'Skill.img.xml','<imgdir name="Skill.img"><imgdir name="22101001"><string name="name" value="Dragon Soul"/><string name="desc" value="Evan and Mir grow stronger."/></imgdir></imgdir>')
        write(strings/'Npc.img.xml','<imgdir name="Npc.img"><imgdir name="1013000"><string name="name" value="Mir"/></imgdir></imgdir>')
        write(core/'Quest.wz'/'Check.img.xml','<imgdir name="Check.img"><imgdir name="0"><imgdir name="22000"><int name="job" value="2210"/><int name="npc" value="1013000"/></imgdir></imgdir></imgdir>')
        write(core/'Npc.wz'/'1013000.img.xml','<imgdir name="1013000.img"><int name="quest" value="22000"/></imgdir>')
        write(core/'Map.wz'/'Map1'/'100000000.img.xml','<imgdir name="100000000.img"><imgdir name="life"><imgdir name="0"><string name="type" value="n"/><string name="id" value="1013000"/></imgdir></imgdir></imgdir>')
        write(core/'Item.wz'/'Consume'/'0200.img.xml','<imgdir name="0200.img"><imgdir name="02001234"><int name="quest" value="22000"/></imgdir></imgdir>')
        write(baseline/'scripts'/'npc'/'1013000.js','// Evan / Mir quest 22000')
        r=build(core,strings,baseline)
    assert r['schemaVersion']==2
    assert '2210' in r['skillJobIds']
    assert '22101001' in r['skillIds']
    assert r['counts']['skillJobFiles']>=1
    assert r['counts']['quests']>=1
    assert r['counts']['npcNodes']>=1
    assert r['counts']['mapNodes']>=1
    assert r['counts']['itemNodes']>=1
    assert r['counts']['baselineFiles']>=1
    assert r['approved'] is False and r['importAllowed'] is False and r['automaticImport'] is False
    assert any(row['contentId']=='1013000' for row in r['strings'])
    assert any(row['questId']=='22000' for row in r['quests'])
    print('Evan profile extractor regression: PASS')
    return 0
if __name__=='__main__': raise SystemExit(main())
