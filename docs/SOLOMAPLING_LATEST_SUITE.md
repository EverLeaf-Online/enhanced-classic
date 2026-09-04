# SoloMapling Latest Disposable QA Suite

Verified UTC: 2026-09-04T05:33:06Z

- Source commit: `5c2a4c1ec3ee97490b85d294e9b676259bdba994`
- Branch: `feature/solomapling-disposable-suite-20260904`
- Disposable QA DB/stack isolation: enforced
- Ambient production bot spawning: disabled
- Full suite result: **FAIL**
- Terminal suite line: `qa-game-1  | 05:33:02.346 [TimerManager-Worker-1] ERROR ArtificialPlayer.DisposableQaSuiteRunner - SOLOMAPLING_QA_SUITE_RESULT FAIL phase=failed passed=8 failed=1 skipped=0 elapsedMs=41505 reason=hunt:bot=900000100;tick-exception-threshold:NullPointerException@server.StatEffect.loadFromData:241;huntDiag=#1{id=900000100;map=100000102;pos=-43:42;phase=stopped;exp=0;monsters=0},#2{id=900000101;map=100000102;pos=29:70;phase=shopping;exp=0;monsters=0},#3{id=900000102;map=100000102;pos=-43:41;phase=shopping;exp=0;monsters=0} stages=party=PASS|trade=PASS|trade-cancel=PASS|cross-map-storage-travel=PASS|storage=PASS|cross-map-shop-travel=PASS|npc-shop=PASS|multi-bot-cross-map-travel=PASS|hunt=FAIL`
