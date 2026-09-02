# EverLeaf class/skill + boss/PQ validation

This release track adds static guards for two high-risk areas that are only partially covered by ordinary Java unit tests.

## Classes and skills

- `AssignSPProcessor` rejects unknown skills before dereferencing them.
- Invalid SP-book indexes are rejected before indexing the character SP array.
- Beginner-skill and Aran hidden-skill mirrors are null-safe.
- `tools/audit_class_skills.py` validates:
  - duplicate `Job` IDs;
  - declared server skill constants against `wz/Skill.wz`;
  - literal scripted job changes against the `Job` enum;
  - continued presence of defensive SP-assignment guards.

## Bosses and party quests

- `tools/audit_event_manager_links.py` resolves every literal `getEventManager("Name")` reference in release scripts against `scripts/event/Name.js`.
- Missing managers, filename-case mismatches, and empty referenced event scripts fail CI.
- Empress-development paths are intentionally excluded from EverLeaf release validation.

These checks are static release gates. They do not replace final in-client runs for boss kills, PQ stage progression, disconnect/rejoin behavior, reward delivery, or simultaneous-channel execution.
