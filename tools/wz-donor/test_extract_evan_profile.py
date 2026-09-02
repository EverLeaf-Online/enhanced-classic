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
        write(core/'Quest.wz'/'Check.img.xml','<imgdir name="Check.img"><imgdir name="22000"><int name="job" value="2210"/><int name="npc" value="1013000"/></imgdir></imgdir>')
        write(core/'Npc.wz'/'1013000.img.xml','<imgdir name="1013000.img"><int name="quest" value="22000"/></imgdir>')
        write(core/'Map.wz'/'Map1'/'100000000.img.xml','<imgdir name="100000000.img"><int name="npc" value="1013000"/></imgdir>')
        write(core/'Item.wz'/'Consume'/'0200.img.xml','<imgdir name="0200.img"><imgdir name="02001234"><int name="quest" value="22000"/></imgdir></imgdir>')
        write(baseline/'scripts'/'npc'/'1013000.js','// Evan / Mir quest 22000')
        r=build(core,strings,baseline)
    assert '2210' in r['skillJobIds']
    assert r['counts']['skillFiles']>=1
    assert r['counts']['questFiles']>=1
    assert r['counts']['npcFiles']>=1
    assert r['counts']['mapFiles']>=1
    assert r['counts']['itemFiles']>=1
    assert r['counts']['baselineFiles']>=1
    assert r['approved'] is False and r['importAllowed'] is False and r['automaticImport'] is False
    assert any('1013000' in row['ids'] for row in r['stringMatches'])
    print('Evan profile extractor regression: PASS')
    return 0
if __name__=='__main__': raise SystemExit(main())
