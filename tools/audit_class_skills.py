#!/usr/bin/env python3
"""Static release audit for EverLeaf job/skill integrity.

This intentionally checks invariants that should remain true regardless of balance:
- every numeric skill constant declared by the server exists in Skill.wz;
- literal scripted job advancements only target jobs declared in client.Job;
- duplicate job IDs are rejected;
- SP assignment keeps the defensive guards that prevent invalid skill packets from
  turning into null dereferences or invalid SP-book indexing.

Empress-development content is excluded from scripted advancement scanning.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JOB_FILE = ROOT / "src/main/java/client/Job.java"
SKILL_CONSTANTS = ROOT / "src/main/java/constants/skills"
SKILL_WZ = ROOT / "wz/Skill.wz"
ASSIGN_SP = ROOT / "src/main/java/client/processor/stat/AssignSPProcessor.java"

JOB_RE = re.compile(r"\b([A-Z][A-Z0-9_]*)\((\d+)\)")
CONST_RE = re.compile(r"\b(?:public\s+)?static\s+final\s+int\s+[A-Z0-9_]+\s*=\s*(\d+)\s*;")
WZ_SKILL_RE = re.compile(r'name="(\d{7,8})"')
CHANGE_JOB_RE = re.compile(r"\b(?:changeJob|changeJobById)\s*\(\s*(\d+)\s*\)")


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def collect_jobs() -> dict[int, str]:
    text = read(JOB_FILE)
    jobs: dict[int, str] = {}
    duplicates: list[tuple[int, str, str]] = []
    for name, raw_id in JOB_RE.findall(text):
        job_id = int(raw_id)
        if job_id in jobs:
            duplicates.append((job_id, jobs[job_id], name))
        else:
            jobs[job_id] = name
    if duplicates:
        for job_id, first, second in duplicates:
            print(f"ERROR duplicate Job id {job_id}: {first} / {second}")
        raise SystemExit(1)
    return jobs


def collect_wz_skill_ids() -> set[int]:
    ids: set[int] = set()
    for xml in SKILL_WZ.rglob("*.xml"):
        for value in WZ_SKILL_RE.findall(read(xml)):
            skill_id = int(value)
            # Skill IDs are seven/eight digit numbers. Other numeric WZ node names
            # can appear in these files, but accepting them only makes this audit
            # conservative; a missing declared skill still cannot pass.
            ids.add(skill_id)
    return ids


def collect_declared_skill_ids() -> dict[int, list[str]]:
    declared: dict[int, list[str]] = {}
    for java in sorted(SKILL_CONSTANTS.glob("*.java")):
        for raw_id in CONST_RE.findall(read(java)):
            skill_id = int(raw_id)
            if skill_id < 1_000_000:
                continue
            declared.setdefault(skill_id, []).append(java.name)
    return declared


def audit_skill_constants() -> tuple[int, int]:
    declared = collect_declared_skill_ids()
    wz_ids = collect_wz_skill_ids()
    missing = {skill_id: files for skill_id, files in declared.items() if skill_id not in wz_ids}
    if missing:
        print("ERROR skill constants missing from Skill.wz:")
        for skill_id, files in sorted(missing.items()):
            print(f"  {skill_id}: {', '.join(files)}")
        raise SystemExit(1)
    return len(declared), len(wz_ids)


def iter_script_files():
    for base in (ROOT / "scripts", ROOT / "src/main/resources"):
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in {".js", ".java"}:
                continue
            lowered = str(path).lower()
            if "empress" in lowered:
                continue
            yield path


def audit_literal_job_changes(jobs: dict[int, str]) -> int:
    checked = 0
    bad: list[tuple[Path, int]] = []
    for path in iter_script_files():
        text = read(path)
        for raw_id in CHANGE_JOB_RE.findall(text):
            checked += 1
            job_id = int(raw_id)
            if job_id not in jobs:
                bad.append((path.relative_to(ROOT), job_id))
    if bad:
        print("ERROR scripted job changes target unknown Job IDs:")
        for path, job_id in bad:
            print(f"  {path}: {job_id}")
        raise SystemExit(1)
    return checked


def audit_sp_guards() -> None:
    text = read(ASSIGN_SP)
    required = (
        "Skill skill = SkillFactory.getSkill(skillid);",
        "if (skill == null)",
        "skillBook < 0 || skillBook >= remainingSps.length",
        "beginnerSkill != null",
    )
    missing = [fragment for fragment in required if fragment not in text]
    if missing:
        print("ERROR AssignSPProcessor lost required defensive validation:")
        for fragment in missing:
            print(f"  {fragment}")
        raise SystemExit(1)


def main() -> int:
    jobs = collect_jobs()
    declared_count, wz_count = audit_skill_constants()
    literal_changes = audit_literal_job_changes(jobs)
    audit_sp_guards()

    print("EverLeaf class/skill integrity audit: PASS")
    print(f"  Job enum IDs: {len(jobs)}")
    print(f"  Declared skill constants: {declared_count}")
    print(f"  Skill.wz numeric skill nodes indexed: {wz_count}")
    print(f"  Literal scripted job advancements checked: {literal_changes}")
    print("  SP assignment invalid-skill / invalid-book guards: present")
    return 0


if __name__ == "__main__":
    sys.exit(main())
