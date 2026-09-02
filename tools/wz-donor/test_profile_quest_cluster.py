#!/usr/bin/env python3
from __future__ import annotations
import tempfile
from pathlib import Path
from profile_quest_cluster import build_report

def write(path:Path,text:str):path.parent.mkdir(parents=True,exist_ok=True);path.write_text(text,encoding='utf-8')
def main()->int:
    manifest={'clusterId':'fixture','donorId':'fixture-donor','questIds':[8165,8166]}
    with tempfile.TemporaryDirectory() as temp:
        root=Path(temp);donor=root/'donor';baseline=root/'baseline'
        write(donor/'Quest.wz'/'Check.img.xml','''<imgdir name="Check.img"><imgdir name="0"><imgdir name="8165"><int name="start" value="9110113"/><int name="lvmin" value="50"/><imgdir name="item"><imgdir name="0"><int name="id" value="4000337"/><int name="count" value="1"/></imgdir></imgdir></imgdir><imgdir name="8166"><int name="end" value="9110112"/><imgdir name="mob"><imgdir name="0"><int name="id" value="9400401"/><int name="count" value="100"/></imgdir></imgdir></imgdir></imgdir></imgdir>''')
        write(donor/'Quest.wz'/'Act.img.xml','''<imgdir name="Act.img"><imgdir name="1"><imgdir name="8165"><imgdir name="item"><imgdir name="0"><int name="id" value="2000005"/><int name="count" value="5"/></imgdir></imgdir></imgdir></imgdir></imgdir>''')
        write(baseline/'wz'/'Quest.wz'/'Check.img.xml','<imgdir name="Check.img"/>')
        write(baseline/'scripts'/'quest'/'8166.js','function start(mode,type,selection) {}')
        r=build_report(manifest,donor,baseline)
    assert r['questCount']==2 and r['questsFoundInDonor']==2 and r['questsAlreadyInBaseline']==0 and r['baselineQuestScripts']==1
    q={x['questId']:x for x in r['quests']}
    assert q['8165']['donorOccurrenceCount']==2 and q['8165']['needsBackport'] is True and q['8165']['baselineQuestScriptExists'] is False
    assert q['8166']['donorOccurrenceCount']==1 and q['8166']['baselineQuestScriptExists'] is True
    assert any(o['file']=='Check.img.xml' for o in q['8165']['donorOccurrences']) and any(o['file']=='Act.img.xml' for o in q['8165']['donorOccurrences'])
    assert q['8165']['referenceSummary']['levelValues']==['50']
    assert r['approved'] is False and r['automaticImport'] is False and all(x['approved'] is False and x['importAllowed'] is False for x in r['quests'])
    print('quest cluster profiler regression: PASS');return 0
if __name__=='__main__':raise SystemExit(main())
