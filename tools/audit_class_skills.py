#!/usr/bin/env python3
"""Static release audit for EverLeaf job/skill integrity.

This intentionally checks invariants that should remain true regardless of balance:
- release-supported numeric skill constants exist in Skill.wz;
- Evan's full ten-stage job chain remains declared exactly as expected;
- literal scripted job advancements only target jobs declared in client.Job;
- duplicate job IDs are rejected;
- SP assignment keeps defensive guards that prevent invalid skill packets from
  turning into null dereferences or invalid SP-book indexing.

Evan is release-supported and therefore fails this audit if any declared Evan
skill disappears from Skill.wz. GM helper constants remain review-only because
they are server/admin conveniences rather than normal player progression.

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
REVIEW_ONLY_CONSTANT_FILES = {"GM.java"}
EVAN_JOB_CHAIN = (
    ("EVAN", 2001),
    ("EVAN1", 2200),
    ("EVAN2", 2210),
    ("EVAN3", 2211),
    ("EVAN4", 2212),
    ("EVAN5", 2213),
    ("EVAN6", 2214),
    ("EVAN7", 2215),
    ("EVAN8", 2216),
    ("EVAN9", 2217),
    ("EVAN10", 2218),
)


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


def audit_evan_job_chain(jobs: dict[int, str]) -> None:
    missing = []
    mismatched = []
    for expected_name, job_id in EVAN_JOB_CHAIN:
        actual_name = jobs.get(job_id)
        if actual_name is None:
            missing.append((expected_name, job_id))
        elif actual_name != expected_name:
            mismatched.append((expected_name, job_id, actual_name))

    if missing or mismatched:
        for expected_name, job_id in missing:
            print(f"ERROR missing Evan job stage {expected_name} ({job_id})")
        for expected_name, job_id, actual_name in mismatched:
            print(
                f"ERROR Evan job id {job_id} expected {expected_name} but is declared as {actual_name}"
            )
        raise SystemExit(1)


def collect_wz_skill_ids() -> set[int]:
    ids: set[int] = set()
    for xml in SKILL_WZ.rglob("*.xml"):
        for value in WZ_SKILL_RE.findall(read(xml)):
            ids.add(int(value))
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


def audit_skill_constants() -> tuple[int, int, int]:
    declared = collect_declared_skill_ids()
    wz_ids = collect_wz_skill_ids()
    hard_missing: dict[int, list[str]] = {}
    review_missing: dict[int, list[str]] = {}

    for skill_id, files in declared.items():
        if skill_id in wz_ids:
            continue
        if all(name in REVIEW_ONLY_CONSTANT_FILES for name in files):
            review_missing[skill_id] = files
        else:
            hard_missing[skill_id] = files

    if review_missing:
        by_file: dict[str, list[int]] = {}
        for skill_id, files in review_missing.items():
            for name in files:
                by_file.setdefault(name, []).append(skill_id)
        for name, ids in sorted(by_file.items()):
            print(f"REVIEW {name}: {len(ids)} declared skill constants are absent from v83 Skill.wz")

    if hard_missing:
        print("ERROR release-supported skill constants missing from Skill.wz:")
        for skill_id, files in sorted(hard_missing.items()):
            print(f"  {skill_id}: {', '.join(files)}")
        raise SystemExit(1)

    return len(declared), len(wz_ids), len(review_missing)


def iter_script_files():
    for base in (ROOT / "scripts", ROOT / "src/main/resources"):
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in {".js", ".java"}:
                continue
            if "empress" in str(path).lower():
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
    audit_evan_job_chain(jobs)
    declared_count, wz_count, review_count = audit_skill_constants()
    literal_changes = audit_literal_job_changes(jobs)
    audit_sp_guards()

    print("EverLeaf class/skill integrity audit: PASS")
    print(f"  Job enum IDs: {len(jobs)}")
    print(f"  Evan job stages: {len(EVAN_JOB_CHAIN)}")
    print(f"  Declared skill constants: {declared_count}")
    print(f"  Skill.wz numeric skill nodes indexed: {wz_count}")
    print(f"  Review-only missing constants (GM): {review_count}")
    print(f"  Literal scripted job advancements checked: {literal_changes}")
    print("  Evan skill constants: hard release gate")
    print("  SP assignment invalid-skill / invalid-book guards: present")
    return 0


if __name__ == "__main__":
    sys.exit(main())
