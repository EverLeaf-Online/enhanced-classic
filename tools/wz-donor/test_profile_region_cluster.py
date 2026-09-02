#!/usr/bin/env python3
from __future__ import annotations
import tempfile
from pathlib import Path
from profile_region_cluster import build_report

def write(path:Path,text:str)->None:path.parent.mkdir(parents=True,exist_ok=True);path.write_text(text,encoding='utf-8')
def main()->int:
    manifest={'clusterId':'fixture','donorId':'fixture-donor','mapPrefixes':['800040'],'mobPrefixes':['94004'],'itemIds':[4000337],'approved':False}
    map_xml='''<imgdir name="800040000.img"><imgdir name="life"><imgdir name="0"><string name="type" value="m"/><string name="id" value="9400400"/></imgdir><imgdir name="1"><string name="type" value="n"/><string name="id" value="9000000"/></imgdir></imgdir><imgdir name="reactor"><imgdir name="0"><string name="id" value="2001000"/></imgdir></imgdir><imgdir name="portal"><imgdir name="0"><int name="tm" value="800040100"/><string name="script" value="ninja_enter"/></imgdir><imgdir name="1"><int name="tm" value="100000000"/></imgdir></imgdir></imgdir>'''
    quest_xml='''<imgdir name="Check.img"><imgdir name="0"><imgdir name="8165"><imgdir name="0"><int name="item" value="4000337"/><int name="npc" value="9000000"/></imgdir><imgdir name="1"><int name="mob" value="9400400"/></imgdir></imgdir></imgdir></imgdir>'''
    mob_xml='''<imgdir name="9400400.img"><imgdir name="info"><imgdir name="revive"><int name="0" value="9500000"/></imgdir><string name="link" value="9400399"/></imgdir></imgdir>'''
    with tempfile.TemporaryDirectory() as temp:
        root=Path(temp);donor=root/'donor';baseline=root/'baseline'
        write(donor/'Map.wz'/'Map8'/'800040000.img.xml',map_xml);write(donor/'Map.wz'/'Map8'/'800040100.img.xml','<imgdir name="800040100.img"/>');write(donor/'Mob.wz'/'9400400.img.xml',mob_xml);write(donor/'Mob.wz'/'9500000.img.xml','<imgdir name="9500000.img"><imgdir name="info"/></imgdir>');write(donor/'Npc.wz'/'9000000.img.xml','<imgdir name="9000000.img"><imgdir name="new"/></imgdir>');write(donor/'Reactor.wz'/'2001000.img.xml','<imgdir name="2001000.img"/>');write(donor/'Quest.wz'/'Check.img.xml',quest_xml)
        write(baseline/'wz'/'Map.wz'/'Map1'/'100000000.img.xml','<imgdir name="100000000.img"/>');write(baseline/'wz'/'Npc.wz'/'9000000.img.xml','<imgdir name="9000000.img"><imgdir name="old"/></imgdir>');write(baseline/'wz'/'Etc.wz'/'NpcLocation.img.xml','<imgdir name="NpcLocation.img"><imgdir name="9000000"><int name="0" value="-1"/></imgdir></imgdir>');write(baseline/'scripts'/'portal'/'ninja_enter.js','function enter(pi) {}')
        report=build_report(manifest,donor,baseline)
    assert report['schemaVersion']==3;assert report['counts']['maps']==2;assert report['counts']['mapReferencedMobs']==2;assert report['counts']['reviveDependencyMobsAdded']==1;assert report['reviveDependencyMobsAdded']==['9500000'];assert report['mobDependencies']['9400400']['reviveMobs']==['9500000'];assert report['mobDependencies']['9400400']['linkedMobs']==['9400399']
    assert report['counts']['mapReferencedNpcs']==1;assert report['counts']['questReferencedNpcs']==1;assert report['counts']['missingQuestNpcScripts']==1;assert report['npcScripts']==[{'npcId':'9000000','baselineScriptExists':False,'questReferences':['8165'],'questReferenced':True}];assert report['blockingReview']['missingQuestNpcScripts']==['9000000']
    assert report['counts']['mapReferencedReactors']==1;assert report['counts']['portalTargets']==2;assert report['counts']['portalScripts']==1;assert report['counts']['questNodes']==1;assert report['questReferences']=={'8165':['4000337','9000000','9400400']}
    assert report['counts']['changedCollisions']==1;collision=report['changedCollisions'][0];assert collision['contentId']=='9000000' and collision['family']=='Npc.wz' and collision['sameContent'] is False;assert collision['donorFingerprint']!=collision['baselineFingerprint'];assert collision['baselineReferences']['referenceCount']==1;assert collision['baselineReferences']['fileCount']==1;assert collision['proposedDormantReplacementCandidate'] is True;assert collision['replacementApproved'] is False
    assert report['blockingReview']['changedContentCollisions']==['9000000'];assert report['blockingReview']['missingPortalScripts']==[];assert report['blockingReview']['unresolvedPortalTargets']==[]
    targets={r['mapId']:r for r in report['portalTargets']};assert targets['800040100']['insideCluster'] is True;assert targets['100000000']['inBaseline'] is True;assert report['approved'] is False and report['importAllowed'] is False and report['automaticImport'] is False
    print('region cluster profiler regression: PASS');return 0
if __name__=='__main__':raise SystemExit(main())
