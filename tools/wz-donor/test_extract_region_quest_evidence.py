#!/usr/bin/env python3
from __future__ import annotations
import tempfile
from pathlib import Path
from extract_region_quest_evidence import build_report


def write(path:Path,text:str):
    path.parent.mkdir(parents=True,exist_ok=True); path.write_text(text,encoding='utf-8')


def main():
    with tempfile.TemporaryDirectory() as temp:
        root=Path(temp); quest=root/'Quest.wz'; string=root/'String.wz'
        write(quest/'Check.img.xml','''<imgdir name="Check.img"><imgdir name="0"><imgdir name="8164"><imgdir name="0"><int name="npc" value="9110100"/></imgdir><imgdir name="1"><int name="npc" value="9110101"/></imgdir></imgdir><imgdir name="8165"><imgdir name="0"><int name="npc" value="9110113"/><imgdir name="quest"><imgdir name="0"><int name="id" value="8164"/><int name="state" value="2"/></imgdir></imgdir></imgdir><imgdir name="1"><int name="npc" value="9110113"/></imgdir></imgdir></imgdir></imgdir>''')
        write(quest/'Act.img.xml','<imgdir name="Act.img"><imgdir name="1"><imgdir name="8164"><imgdir name="0"><int name="exp" value="50"/></imgdir></imgdir><imgdir name="8165"><imgdir name="0"><int name="exp" value="123"/></imgdir></imgdir></imgdir></imgdir>')
        write(string/'Quest.img.xml','<imgdir name="Quest.img"><imgdir name="8164"><string name="name" value="Ninja Introduction"/></imgdir><imgdir name="8165"><string name="name" value="Ninja Test"/></imgdir></imgdir>')
        write(string/'Npc.img.xml','<imgdir name="Npc.img"><imgdir name="9110100"><string name="name" value="Sasuke"/></imgdir><imgdir name="9110101"><string name="name" value="Guide"/></imgdir><imgdir name="9110113"><string name="name" value="Shururu"/></imgdir></imgdir>')
        r=build_report(quest,string,['8165'],[])
    assert r['seedQuestIds']==['8165']
    assert r['questIds']==['8164','8165']
    assert r['prerequisiteQuestIds']==['8164']
    assert r['prerequisiteEdges']=={'8165':['8164']}
    assert r['npcIds']==['9110100','9110101','9110113']
    assert set(r['questComponents']['8165'])=={'Check.img.xml','Act.img.xml'}
    assert r['questStringHits']['8165'][0]['node']['children'][0]['attributes']['value']=='Ninja Test'
    assert r['npcStringHits']['9110113'][0]['node']['children'][0]['attributes']['value']=='Shururu'
    assert r['npcStringHits']['9110100'][0]['node']['children'][0]['attributes']['value']=='Sasuke'
    assert r['approved'] is False and r['importAllowed'] is False and r['automaticImport'] is False
    print('region quest evidence regression: PASS')
    return 0

if __name__=='__main__': raise SystemExit(main())
