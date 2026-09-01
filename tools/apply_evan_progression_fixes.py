#!/usr/bin/env python3
"""Apply deterministic Evan progression fixes to Character.java.

Restores and protects the v83 Evan growth model:
- Evan mastery stages automatically advance at 10/20/30/40/50/60/80/100/120/160.
- Advancement is catch-up safe: an Evan above a missed threshold advances through every
  mastery stage their current level qualifies for.
- Evan growth stages receive magician-style HP/MP growth on level-up.
- Automatic Evan mastery changes reuse the canonical Character.changeJob path
  without also receiving the generic manual job-change SP grant.
- Mastery advancement occurs before the normal level-up SP grant so the one
  level-up grant lands in the newly unlocked Evan SP book.

Manual/scripted job changes still use the existing SP behavior through the
public changeJob(Job) wrapper.
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

    old_change_job = """    public synchronized void changeJob(Job newJob) {
        if (newJob == null) {
"""
    new_change_job = """    public synchronized void changeJob(Job newJob) {
        changeJob(newJob, true);
    }

    private synchronized void changeJob(Job newJob, boolean grantJobChangeSp) {
        if (newJob == null) {
"""
    text, did = replace_known(text, old_change_job, new_change_job, "Evan no-extra-SP changeJob overload")
    changed |= did

    old_sp = """        int spGain = 1;
        if (GameConstants.hasSPTable(newJob)) {
            spGain += 2;
        } else {
            if (newJob.getId() % 10 == 2) {
                spGain += 2;
            }

            if (YamlConfig.config.server.USE_ENFORCE_JOB_SP_RANGE) {
                spGain = getChangedJobSp(newJob);
            }
        }

        if (spGain > 0) {
            gainSp(spGain, GameConstants.getSkillBook(newJob.getId()), true);
        }
"""
    new_sp = """        int spGain = 0;
        if (grantJobChangeSp) {
            spGain = 1;
            if (GameConstants.hasSPTable(newJob)) {
                spGain += 2;
            } else {
                if (newJob.getId() % 10 == 2) {
                    spGain += 2;
                }

                if (YamlConfig.config.server.USE_ENFORCE_JOB_SP_RANGE) {
                    spGain = getChangedJobSp(newJob);
                }
            }
        }

        if (spGain > 0) {
            gainSp(spGain, GameConstants.getSkillBook(newJob.getId()), true);
        }
"""
    text, did = replace_known(text, old_sp, new_sp, "Evan automatic mastery skips generic job-change SP")
    changed |= did

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
        while (true) {
            Job nextJob = null;
            if (level >= 10 && job == Job.EVAN) {
                nextJob = Job.EVAN1;
            } else if (level >= 20 && job == Job.EVAN1) {
                nextJob = Job.EVAN2;
            } else if (level >= 30 && job == Job.EVAN2) {
                nextJob = Job.EVAN3;
            } else if (level >= 40 && job == Job.EVAN3) {
                nextJob = Job.EVAN4;
            } else if (level >= 50 && job == Job.EVAN4) {
                nextJob = Job.EVAN5;
            } else if (level >= 60 && job == Job.EVAN5) {
                nextJob = Job.EVAN6;
            } else if (level >= 80 && job == Job.EVAN6) {
                nextJob = Job.EVAN7;
            } else if (level >= 100 && job == Job.EVAN7) {
                nextJob = Job.EVAN8;
            } else if (level >= 120 && job == Job.EVAN8) {
                nextJob = Job.EVAN9;
            } else if (level >= 160 && job == Job.EVAN9) {
                nextJob = Job.EVAN10;
            }

            if (nextJob == null) {
                return;
            }

            changeJob(nextJob, false);
            yellowMessage("Your bond with Mir has deepened. Evan mastery automatically advanced to " + GameConstants.getJobName(nextJob.getId()) + ".");
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
    intermediate_call = """        levelUpGainSp();
        advanceEvanGrowthStage();

        effLock.lock();
"""
    new_call = """        advanceEvanGrowthStage();
        levelUpGainSp();

        effLock.lock();
"""
    if new_call in text:
        print("OK already fixed: Evan mastery-before-SP ordering")
    elif intermediate_call in text:
        text = text.replace(intermediate_call, new_call, 1)
        changed = True
        print("FIXED: Evan mastery-before-SP ordering")
    elif old_call in text:
        text = text.replace(old_call, new_call, 1)
        changed = True
        print("FIXED: Evan automatic mastery advancement + SP ordering")
    else:
        raise SystemExit("ERROR expected Evan level-up SP/mastery snippet not found")

    if changed:
        CHARACTER.write_text(text, encoding="utf-8")

    required = (
        "changeJob(newJob, true);",
        "private synchronized void changeJob(Job newJob, boolean grantJobChangeSp)",
        "if (grantJobChangeSp)",
        "private boolean isEvanGrowthJob()",
        "while (true)",
        "level >= 10 && job == Job.EVAN",
        "level >= 160 && job == Job.EVAN9",
        "nextJob = Job.EVAN10;",
        "changeJob(nextJob, false);",
        "advanceEvanGrowthStage();\n        levelUpGainSp();",
        "job.isA(Job.BLAZEWIZARD1) || isEvanGrowthJob()",
        "Your bond with Mir has deepened.",
    )
    final = CHARACTER.read_text(encoding="utf-8")
    for fragment in required:
        if fragment not in final:
            raise SystemExit(f"ERROR Evan progression invariant missing after transform: {fragment}")

    forbidden = (
        "levelUpGainSp();\n        advanceEvanGrowthStage();",
        "changeJob(nextJob);",
        "level == 10 && job == Job.EVAN",
        "level == 160 && job == Job.EVAN9",
    )
    for fragment in forbidden:
        if fragment in final:
            raise SystemExit(f"ERROR stale Evan progression path remains: {fragment}")

    print("EverLeaf Evan progression fixes: PASS")
    print("  milestone mastery change: catch-up safe and before normal level-up SP")
    print("  automatic Evan changeJob: generic job-change SP disabled")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
