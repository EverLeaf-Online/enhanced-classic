#!/usr/bin/env python3
"""Apply deterministic Evan progression fixes to Character.java.

Restores two pieces required by the v83 Evan backport:
- Evan mastery stages automatically advance at 10/20/30/40/50/60/80/100/120/160.
- Evan growth stages receive magician-style HP/MP growth on level-up.

The advancement deliberately uses Character.changeJob so the existing SP-table,
job packet, dragon recreation, guild/family update, and persistence paths remain
canonical. The transition is exact-stage only, preventing skipped or repeated
advancements if a character is edited or already past a milestone.
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHARACTER = ROOT / "src/main/java/client/Character.java"


def replace_known(text: str, broken: str, fixed: str, label: str) -> tuple[str, bool]:
    if fixed in text:
        print(f"OK already fixed: {label}")
        return text, False
    if broken not in text:
        raise SystemExit(f"ERROR expected Evan progression snippet not found: {label}")
    print(f"FIXED: {label}")
    return text.replace(broken, fixed, 1), True


def main() -> int:
    text = CHARACTER.read_text(encoding="utf-8")
    changed = False

    old_mage = """        } else if (job.isA(Job.MAGICIAN) || job.isA(Job.BLAZEWIZARD1)) {
            improvingMaxMP = isCygnus() ? SkillFactory.getSkill(BlazeWizard.INCREASING_MAX_MP) : SkillFactory.getSkill(Magician.IMPROVED_MAX_MP_INCREASE);
"""
    new_mage = """        } else if (job.isA(Job.MAGICIAN) || job.isA(Job.BLAZEWIZARD1) || isEvanGrowthJob()) {
            improvingMaxMP = isCygnus() ? SkillFactory.getSkill(BlazeWizard.INCREASING_MAX_MP) : SkillFactory.getSkill(Magician.IMPROVED_MAX_MP_INCREASE);
"""
    text, did = replace_known(text, old_mage, new_mage, "Evan magician-style level-up HP/MP")
    changed |= did

    old_method = """    private void levelUpGainSp() {
        if (GameConstants.getJobBranch(job) == 0) {
"""
    new_method = """    private boolean isEvanGrowthJob() {
        int jobId = job.getId();
        return jobId >= Job.EVAN1.getId() && jobId <= Job.EVAN10.getId();
    }

    private void advanceEvanGrowthStage() {
        Job nextJob = null;
        if (level == 10 && job == Job.EVAN) {
            nextJob = Job.EVAN1;
        } else if (level == 20 && job == Job.EVAN1) {
            nextJob = Job.EVAN2;
        } else if (level == 30 && job == Job.EVAN2) {
            nextJob = Job.EVAN3;
        } else if (level == 40 && job == Job.EVAN3) {
            nextJob = Job.EVAN4;
        } else if (level == 50 && job == Job.EVAN4) {
            nextJob = Job.EVAN5;
        } else if (level == 60 && job == Job.EVAN5) {
            nextJob = Job.EVAN6;
        } else if (level == 80 && job == Job.EVAN6) {
            nextJob = Job.EVAN7;
        } else if (level == 100 && job == Job.EVAN7) {
            nextJob = Job.EVAN8;
        } else if (level == 120 && job == Job.EVAN8) {
            nextJob = Job.EVAN9;
        } else if (level == 160 && job == Job.EVAN9) {
            nextJob = Job.EVAN10;
        }

        if (nextJob != null) {
            changeJob(nextJob);
        }
    }

    private void levelUpGainSp() {
        if (GameConstants.getJobBranch(job) == 0) {
"""
    text, did = replace_known(text, old_method, new_method, "Evan mastery growth helper")
    changed |= did

    old_call = """        levelUpGainSp();

        effLock.lock();
"""
    new_call = """        levelUpGainSp();
        advanceEvanGrowthStage();

        effLock.lock();
"""
    text, did = replace_known(text, old_call, new_call, "Evan automatic mastery advancement")
    changed |= did

    if changed:
        CHARACTER.write_text(text, encoding="utf-8")

    required = (
        "private boolean isEvanGrowthJob()",
        "level == 10 && job == Job.EVAN",
        "level == 160 && job == Job.EVAN9",
        "nextJob = Job.EVAN10;",
        "advanceEvanGrowthStage();",
        "job.isA(Job.BLAZEWIZARD1) || isEvanGrowthJob()",
    )
    final = CHARACTER.read_text(encoding="utf-8")
    for fragment in required:
        if fragment not in final:
            raise SystemExit(f"ERROR Evan progression invariant missing after transform: {fragment}")

    print("EverLeaf Evan progression fixes: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
