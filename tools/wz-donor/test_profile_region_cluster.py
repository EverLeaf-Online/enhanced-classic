#!/usr/bin/env python3
from __future__ import annotations
import tempfile
from pathlib import Path
from profile_region_cluster import build_report


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def main() -> int:
    manifest={"clusterId":"fixture","donorId":"fixture-donor","mapPrefixes":["800040"],"mobPrefixes":["94004"],"itemIds":[4000337],"approved":False}
    map_xml='''<imgdir name="800040000.img"><imgdir name="life"><imgdir name="0"><string name="type" value="m"/><string name="id" value="9400400"/></imgdir><imgdir name="1"><string name="type" value="n"/><string name="id" value="9000000"/></imgdir></imgdir><imgdir name="reactor"><imgdir name="0"><string name="id" value="2001000"/></imgdir></imgdir><imgdir name="portal"><imgdir name="0"><int name="tm" value="800040100"/><string name="script" value="ninja_enter"/></imgdir><imgdir name="1"><int name="tm" value="100000000"/></imgdir></imgdir></imgdir>'''
    with tempfile.TemporaryDirectory() as temp:
        root=Path(temp); donor=root/'donor'; baseline=root/'baseline'
        write(donor/'Map.wz'/'Map8'/'800040000.img.xml',map_xml)
        write(donor/'Map.wz'/'Map8'/'800040100.img.xml','<imgdir name="800040100.img"/>')
        write(donor/'Mob.wz'/'9400400.img.xml','<imgdir name="9400400.img"/>')
        write(donor/'Npc.wz'/'9000000.img.xml','<imgdir name="9000000.img"/>')
        write(donor/'Reactor.wz'/'2001000.img.xml','<imgdir name="2001000.img"/>')
        write(donor/'Quest.wz'/'Check.img.xml','<imgdir name="Check.img"><imgdir name="8165"><int name="item" value="4000337"/><int name="mob" value="9400400"/></imgdir></imgdir>')
        write(baseline/'Map.wz'/'Map1'/'100000000.img.xml','<imgdir name="100000000.img"/>')
        write(baseline/'scripts'/'portal'/'ninja_enter.js','function enter(pi) {}')
        report=build_report(manifest, donor, baseline)
    assert report['counts']['maps']==2
    assert report['counts']['mapReferencedMobs']==1
    assert report['counts']['mapReferencedNpcs']==1
    assert report['counts']['mapReferencedReactors']==1
    assert report['counts']['portalTargets']==2
    assert report['counts']['portalScripts']==1
    assert report['questReferences']['8165']==['4000337','9400400']
    assert report['blockingReview']['missingPortalScripts']==[]
    assert report['blockingReview']['unresolvedPortalTargets']==[]
    targets={r['mapId']:r for r in report['portalTargets']}
    assert targets['800040100']['insideCluster'] is True
    assert targets['100000000']['inBaseline'] is True
    assert report['approved'] is False and report['importAllowed'] is False and report['automaticImport'] is False
    print('region cluster profiler regression: PASS')
    return 0

if __name__=='__main__': raise SystemExit(main())
