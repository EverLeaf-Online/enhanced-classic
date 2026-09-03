# EverLeaf Live Evan Skill Equivalence Audit — 2026-09-03

This report records a direct scan of the current live Community-exported `Skill.wz` XML on the Oracle server against the 43 Evan skill IDs expected by EverLeaf's server implementation.

## Result

The live Community `Skill.wz` XML contains **0 of the 43 expected Evan skill IDs**.

The preserved pre-wholesale EverLeaf baseline contains **all 43 of 43** expected IDs.

The audit also scanned the live `Skill.wz` for alternate IDs using the same Evan job-like prefixes (`2001`, `2200`, `2210`–`2218`) and found **no candidate alternate IDs** that could explain the missing records as a simple renumbering/re-grouping.

Therefore this is a confirmed live wholesale parity regression, not merely a filename-grouping false positive.

## Expected Evan skill IDs

`20010012`, `20011000`, `20011001`, `20011002`, `20011003`, `20011004`, `20011005`, `20011006`, `20011007`, `20011009`, `20011010`, `20011011`, `22000000`, `22001001`, `22101000`, `22101001`, `22111000`, `22111001`, `22121000`, `22121001`, `22131000`, `22131001`, `22140000`, `22141001`, `22141002`, `22141003`, `22150000`, `22151001`, `22151002`, `22151003`, `22160000`, `22161001`, `22161002`, `22161003`, `22170001`, `22171000`, `22171002`, `22171003`, `22171004`, `22181000`, `22181001`, `22181002`, `22181003`.

## Provenance

- Audit workflow: `.github/workflows/audit-live-evan-skill-equivalence.yml`
- Workflow run: `33709793980`
- Workflow commit: `5a4f9e190d73debab1ef96846014cd0ce4600290`
- Artifact: `everleaf-live-evan-skill-equivalence-33709793980`
- Artifact ID: `9876507328`
- Artifact ZIP SHA256: `b7d07afac61c0e26ffd0a48467f91130a3a3a9c9e829d0b7432da90a88049539`

## Recommended remediation

Do not replace the Community WZ wholesale. Merge the preserved EverLeaf Evan skill groups/records back into the Community-based `Skill.wz` and regenerate the corresponding server XML, then run the Evan release audit and real-client skill tests. The Community donor remains the base for the rest of the content.
