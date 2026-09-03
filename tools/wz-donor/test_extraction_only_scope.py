#!/usr/bin/env python3
from pathlib import Path

workflow = Path('.github/workflows/export-gms-v95-donor.yml').read_text(encoding='utf-8')

required = [
    'Character.wz', 'Etc.wz', 'Item.wz', 'Map.wz', 'Mob.wz',
    'Npc.wz', 'Quest.wz', 'Reactor.wz', 'Skill.wz', 'String.wz',
    'gms-v95-extracted.zip', 'EXTRACTION_STATUS.json',
    'comparisonPerformed = $false',
]
for token in required:
    assert token in workflow, f'missing extraction-only token: {token}'

for forbidden in (
    'wz_diff.py',
    'build_import_manifest.py',
    'render_review_report.py',
    'wz-gms-v95-core7-diff.json',
    'wz-gms-v95-core7-import-manifest.json',
):
    assert forbidden not in workflow, f'comparison/import logic still present: {forbidden}'

print('v95 extraction-only workflow regression: PASS')
