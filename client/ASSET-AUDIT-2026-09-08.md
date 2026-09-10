# EverLeaf Client Asset Audit — 2026-09-08

## Status

This document records the repository/provenance pass of the EverLeaf client asset audit.

- **Audit baseline:** `release/client-ui-live-approved-20260906`
- **Audit working branch:** `audit/client-assets-20260908`
- **Production/live patch manifests:** untouched
- **Managed client baseline:** untouched
- **WZ binaries:** untouched
- **Native client code:** untouched

The baseline branch is intentionally used instead of `master` because the live-approved client branch contains client work that is not yet represented by `master`.

## Scope

The target inventory is:

- login
- world select
- character select
- shared UI
- buttons and controls
- backgrounds
- sprites
- effects
- fonts
- WZ-backed imagery

This pass can prove repository structure, provenance, build/patch boundaries, and naming contracts. Pixel-level duplicate detection, alpha-fringe inspection, anchor/padding measurements, deterministic render comparison, and performance telemetry still require the local client plus the Game Development Studio tooling.

## Findings

### 1. EverLeaf-owned branding is currently login-centric

`client/branding/` currently has a canonical `login/` area, but there are no equivalent source-of-truth areas for world select, character select, or shared UI.

Current login source assets include:

- `client/branding/login/source/everleaf-logo.webp`
- `client/branding/login/source/hero-forest.webp`
- `client/branding/login/source/panorama-extended.png`
- `client/branding/login/source/panorama-extended.md`

This means the repository does not yet provide the same provenance and source-art discipline for the rest of the visible client UI.

**Action:** expand the branding contract to `shared`, `world-select`, and `character-select` before further visual replacement work.

### 2. The panorama metadata is the current best provenance example

`panorama-extended.md` records:

- 1320×3240
- RGB
- Lanczos resampling
- WZ target: `Map.wz/Back/Login.img/back/11`
- origin: `(596,2880)`
- recorded live archive SHA-256: `b30a4225c20d7a6f3bc09f880f6fa284e97092473c6159f5d4f554a80e752079`
- explicit note that native-game visual validation remains required

Every canonical EverLeaf visual asset should eventually have equivalent provenance data.

### 3. There are multiple generations of login tooling

`client/branding/login/generate_art.py` is an older 800×600-oriented generator, while the current panorama path is widescreen/panorama-oriented and is connected to `replace-panorama.cpp` plus native login-layout work.

These should not be treated as one authoritative pipeline until the source/output contract is documented.

**Action:** mark generators as `legacy`, `current`, or `experimental`; do not let two scripts silently generate different canonical assets for the same role.

### 4. `polish_login_controls.py` has a source-name contract risk

The script expects inputs named:

- `logo.png`
- `panorama-extended-source.png`

The tracked canonical login source directory instead contains:

- `everleaf-logo.webp`
- `panorama-extended.png`

This may be intentional if the script is called with a prepared staging directory, but the contract is not recorded next to the script.

**Action:** document the expected input directory or update the script in a dedicated tested change. Do not silently rename tracked source files on the live-approved branch.

### 5. `client/ezorsia/` is intentional upstream provenance

The Ezorsia tree is a full upstream/source snapshot, not a few accidental branding leftovers. Existing EverLeaf client documentation identifies it as upstream material.

The problem is organizational clarity: upstream/vendor material and EverLeaf-owned branding are adjacent under `client/`, which can make ownership unclear.

**Action:** preserve it. Do not delete it. Long-term, move it to an explicit `client/upstream/ezorsia/` or `client/vendor/ezorsia/` boundary only in a dedicated refactor that updates and tests every build/path reference.

### 6. `EverLeaf_UI.wz` should be the canonical custom-UI boundary

`client/managed-client-baseline.json` already distinguishes stock/general `UI.wz` from `EverLeaf_UI.wz`. The managed baseline maps `EverLeaf_UI.wz` to the current upstream-derived source path `client/ezorsia/ezorsia/EzorsiaV2_UI.wz`.

That separation is useful and should be formalized:

- `UI.wz` — base/stock-compatible UI data
- `EverLeaf_UI.wz` — EverLeaf custom UI extension package

The old `EzorsiaV2_UI.wz` source name should be treated as provenance, not as a reason to delete or casually rename the file. Any rename must update native/resource lookup and packaging references together.

### 7. Existing checksum/baseline distribution model should remain authoritative

The managed client already has a package/baseline contract. The asset manifest introduced by this audit is complementary metadata for source art and WZ destinations; it is **not** a second launcher/patch distribution system.

## Kaentake comparison

The most useful idea to carry over from Kaentake is package-boundary discipline: custom client UI should have an explicit extension/package boundary instead of becoming an undocumented collection of modified assets.

For EverLeaf, the equivalent is to formalize `EverLeaf_UI.wz` and source manifests rather than copy Kaentake art or blindly mirror its directory tree.

## Canonical EverLeaf asset package

### Ownership classes

Every source asset must be one of:

- `everleaf` — produced for EverLeaf or explicitly owned by the project
- `upstream` — inherited from the base client/source
- `vendor` — third-party package with recorded provenance/license
- `generated` — derived from a recorded source by a reproducible tool

### Naming

Use lowercase kebab-case for new source assets and role-based names rather than screen coordinates.

Examples:

- `everleaf-logo.webp`
- `login-panorama.png`
- `world-select-panel.png`
- `character-select-slot-frame.png`
- `button-login-normal.png`
- `button-login-hover.png`
- `button-login-pressed.png`
- `button-login-disabled.png`

Do not encode temporary version numbers, donor project branding, or unexplained numeric suffixes into new EverLeaf-owned asset names.

### Target source layout

Do not move existing runtime/upstream paths yet. New owned assets should converge on:

```text
client/branding/
  README.md
  assets.manifest.json
  shared/
    source/
    generated/
  login/
    source/
    generated/
  world-select/
    source/
    generated/
  character-select/
    source/
    generated/
```

`client/ezorsia/` remains in place until a separately tested upstream/vendor-path refactor.

### Required manifest fields

For each canonical asset, record when known:

- stable asset ID
- owner/provenance class
- source path
- source/blob/SHA-256 identity
- generator/tool
- dimensions
- color mode
- alpha mode
- padding policy
- anchor/origin
- runtime role
- WZ package
- WZ target node/path
- native-layout dependency
- validation status
- baseline/live association

## Replacement/change classification

### Safe source/repository changes — no native client change by themselves

- documentation and provenance manifests
- canonical naming rules
- adding owned source-art folders
- source-art normalization before packaging
- replacing an asset while retaining the exact runtime node, expected geometry, origin, and lookup behavior

These changes still need WZ packaging if the runtime consumes the asset from a WZ file.

### WZ-only candidates

These can generally remain native-code-free **only when geometry/lookup assumptions stay compatible**:

- replacing the login panorama at `Map.wz/Back/Login.img/back/11`
- replacing existing button/background imagery at an existing WZ node
- replacing textures/sprites without changing their expected origin, animation semantics, hitbox/layout assumptions, or resource path

### Native client + WZ candidates

Native changes are expected when changing:

- login/world/character-select element positions
- widescreen viewport/crop behavior
- clickable hitboxes
- custom control dimensions that drive layout
- new UI components or new resource lookup paths
- package lookup/loading behavior
- rendering behavior that cannot be expressed by existing WZ nodes

`EverLeafLoginLayout.cpp` is an example of the native layout boundary for the login screen.

## Local Game Development Studio validation still required

The following items are **not claimed complete** by this repository-only pass:

- exact and perceptual duplicate-image scan
- bad scaling / resampling artifacts
- alpha fringe / accidental opaque-corner inspection
- transparent padding consistency
- sprite anchor/origin consistency
- animation-frame bounding-box consistency
- in-client login/world-select/character-select screenshot capture
- deterministic baseline-vs-candidate raster comparison
- GPU/frame-time/performance telemetry

Run these against a local copy of the approved client before normalizing or replacing binary/runtime assets.

## Priority backlog

1. Build the complete source/WZ inventory for world select, character select, shared UI, effects, fonts, and sprites.
2. Give each live EverLeaf-owned asset a manifest entry equivalent to the panorama record.
3. Resolve the login generator/input naming contract and declare one current pipeline.
4. Extract/package source references for `EverLeaf_UI.wz` without changing the live binary.
5. Run local duplicate/alpha/anchor/animation-frame validation.
6. Capture approved baseline screenshots for login, world select, and character select.
7. Normalize only assets that fail measurable checks.
8. Apply runtime changes in small, reviewable WZ/native-client batches.
9. Update managed-client checksums only as part of an explicitly approved release/deployment step.

## Guardrails

- Never overwrite the live-approved branch during asset exploration.
- Never update live patch manifests as part of an audit.
- Never delete upstream/vendor source solely because it contains old branding.
- Never infer visual correctness from file names or dimensions alone.
- Never change anchors/origins as a cosmetic cleanup without validating runtime placement.
- Keep source/provenance hashes separate from launcher/runtime package hashes.
