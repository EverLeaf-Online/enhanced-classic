# Kaentake -> EverLeaf Client Backport Plan

Source reference: `iw2d/kaentake` (GMS v83 resizable HD client).

This is a selective backport. EverLeaf keeps its launcher, branding, server protocol, production packaging, diagnostics, and existing client hardening. Kaentake is used as the reference for v83-native display/UI/resource behavior where it is cleaner or more complete.

## Status legend

- **PORT**: bring the Kaentake behavior into EverLeaf, adapted to EverLeaf's architecture.
- **KEEP**: EverLeaf's current implementation is preferable; only borrow small ideas if useful.
- **REWRITE**: use Kaentake as the behavioral reference, but do not copy its implementation wholesale.
- **IMPLEMENTED / RUNTIME GATE**: code and CI build are present on a backport branch; native gameplay testing is still required before merge.
- **SKIP**: not needed or conflicts with EverLeaf.

## P0 - Display / fullscreen

### Alt+Enter borderless fullscreen - REWRITE - IMPLEMENTED / RUNTIME GATE

EverLeaf's previous toggle removed the frame but only sized the window to `Client::m_nGameWidth` x `Client::m_nGameHeight`. It filled the monitor only when the configured render size exactly matched the desktop.

Backport implementation:
- Alt+Enter uses the active monitor's full rectangle for the borderless window.
- The pre-toggle framed style, extended style, size, position, and monitor placement are preserved for restore.
- Phase 2 also preserves the framed render resolution.
- If the active monitor exactly matches one of EverLeaf's supported renderer modes, Alt+Enter temporarily changes Gr2D to the monitor resolution and restores the previous renderer resolution on exit.
- Unsupported desktop modes still get a monitor-sized borderless window without injecting an untested render resolution.
- Maple remains in its safer windowed renderer path; this is borderless fullscreen, not exclusive D3D fullscreen.
- `MatchMonitorResolutionOnFullscreen` can disable the renderer-match behavior independently.

Runtime gate before merge:
- windowed -> fullscreen -> windowed
- 1280x720, 1366x768, 1600x900, 1920x1080
- repeated toggles
- mouse/input alignment
- login/world/character select
- in-field UI interaction
- multi-monitor placement
- minimize/restore and Alt-Tab

## P0 - Live resolution stack

### System Options resolution selector - PORT/EXTEND - IMPLEMENTED / RUNTIME GATE

EverLeaf already used Kaentake's native v83 `CCtrlComboBox` placement and added 1280x720. The old EverLeaf behavior only saved the preference for the next launch.

Implemented phase-2 path:

1. `CWzGr2D::ScreenResolution`-style runtime screen-mode reset using the v83 Gr2D mode structure and Kaentake's `FindScreenMode` signature.
2. Apply the selected resolution immediately from System Options after Maple applies its normal video options.
3. Strictly allow only EverLeaf's supported list:
   - 800x600
   - 1024x768
   - 1280x720
   - 1366x768
   - 1600x900
   - 1920x1080
4. Update EverLeaf's runtime width/height state only after Gr2D accepts the requested mode.
5. Re-run EverLeaf's existing HD/UI correction pass and then its verified widescreen-axis corrections.
6. Refresh the active field view range and reload its background after a live change.
7. Refresh screen-message and tooltip runtime bounds that were previously startup-only.
8. Persist the selected resolution only after runtime apply succeeds.
9. Attempt a real Gr2D rollback if a later correction fails; keep EverLeaf bookkeeping aligned with the renderer even if rollback itself fails.
10. Retain `LiveResolution=false` as a safe save-and-restart fallback.

Do not reintroduce the old partial renderer reset that caused Alt+Enter/runtime crashes.

## P0 - Resolution-dependent UI/input corrections

### Cursor coordinate handling - RECONCILE - PARTIAL / RUNTIME GATE

EverLeaf's existing `Client::UpdateResolution()` already rewrites the v83 cursor center and bounds for the active dimensions. Phase 2 reruns that correction after every successful runtime resolution change.

Runtime testing must prove mouse/click alignment across all supported modes before deciding whether Kaentake's deeper `CInputSystem` method hooks are still necessary.

### UI origins - PORT - PENDING

Port/adapt Kaentake's extended vector-origin model only where EverLeaf's existing resolution patches are insufficient, especially for:
- center/top/right anchored UI
- status bar
- screen messages
- quick slot

Do not stack duplicate hooks over EverLeaf addresses that are already corrected successfully.

### Saved UI window positions - PORT - IMPLEMENTED / RUNTIME GATE

Kaentake-style handling is now adapted to EverLeaf's pinned v83 `CConfig` layout:
- validate all 34 saved UI X/Y position slots;
- restore Kaentake's sane per-window defaults when a saved position falls outside the active resolution;
- revalidate loaded positions when changing from a larger to a smaller runtime resolution;
- keep the resolution selector usable even if the optional position hooks fail to attach.

### Movable UI bounds/snapping - PORT - PENDING

Bring over Kaentake's resolution-aware window bounds and snapping only if runtime testing shows EverLeaf still allows movable windows off-screen after the saved-position fix.

### Tooltip/context-menu bounds - RECONCILE - PARTIAL

EverLeaf already patches tooltip limits as part of its HD path and phase 2 reapplies the vertical tooltip bound after a live resolution change. Kaentake's broader context-menu/dialog bounds remain a follow-up if runtime testing finds gaps.

### Status/buff/screen-message positioning - RECONCILE - PARTIAL / RUNTIME GATE

EverLeaf already owns many status bar, quick-slot, temporary-stat, and screen-message patches. Phase 2 reruns the existing set and explicitly refreshes the screen-message reset operands that were startup-only.

Port Kaentake's extra origin model only for surfaces that still fail runtime QA.

### Field/view-range corrections - PORT CAREFULLY - PARTIAL / RUNTIME GATE

Phase 2 now:
- reapplies EverLeaf's field/view-range operands for the new dimensions;
- calls the pinned v83 `CMapLoadable::RestoreViewRange` on the active field;
- calls `CMapLoadable::ReloadBack` so the visible background is rebuilt immediately.

Still pending only if runtime QA shows gaps:
- Kaentake's full dynamic RestoreViewRange hook;
- grid/background edge cases;
- weather/effect bounds;
- limited-view handling;
- any boss HP or special-field placement not already covered by EverLeaf.

Reuse EverLeaf's already-verified `WidescreenCorrections` where equivalent; do not duplicate patches to the same addresses.

## P1 - Custom WZ override namespace

### Kaentake `Custom.wz` resource override model - PORT/REWRITE - AUDITED / PENDING IMPLEMENTATION

Kaentake mounts a separate `Custom.wz` namespace, enumerates override paths, falls back to the custom namespace when the base lookup misses, and merges custom property children during property serialization.

EverLeaf already has a project-level package decision from the 2026-09-08 asset audit:
- `UI.wz` is the base/stock-compatible UI data boundary;
- `EverLeaf_UI.wz` is the canonical EverLeaf custom UI extension package;
- the launcher/managed-client baseline remains the authoritative distribution/checksum model.

Current `EverLeaf_UI.wz` is not yet a Kaentake-style path-mirroring override tree; the archived structure records only the upstream-derived `MapleEzorsiaV2wzfiles`, `smap`, `StandardPDD`, and `zmap` images. Therefore do **not** point Kaentake's merge hook at the current binary and assume overrides will work.

EverLeaf target:
1. Preserve `EverLeaf_UI.wz` as the canonical package name rather than create a redundant `EverLeaf_Custom.wz`.
2. Define and document a path-mirroring override layout inside that package (for example `UI/...` nodes matching their base lookup paths).
3. Repack the package in a reviewable asset-only change without changing live patch manifests.
4. Adapt Kaentake's custom namespace enumeration/fallback/property-merge behavior to `EverLeaf_UI.wz`.
5. Keep the clean base WZ set intact and stop adding new EverLeaf-owned visual overrides directly into donor/stock WZs.
6. Do not copy Kaentake's sample `Custom.wz` art/content wholesale.

## P1 - Native window/system hooks

### Win32/Winsock cleanup - KEEP + SELECTIVE PORT

EverLeaf already has newer hardening work around loader timing, dinput8 forwarding, process ownership, and server redirect handling. Do not replace it wholesale with Kaentake's `system.cpp`.

Review individual Kaentake behaviors only when EverLeaf lacks them:
- clean Maple top-level window subclass behavior
- non-client cursor behavior
- safe window movement handling
- specific WSP compatibility behavior

Avoid regressing EverLeaf's existing #351 hardening.

## P1 - Loader/startup

### Loader cleanup - KEEP

EverLeaf's current startup/loader work is intentionally more defensive than Kaentake's attach model. Keep EverLeaf's #358 direction. Use Kaentake only for small hook-order references when useful.

## P1 - Input

### WASD - KEEP EVERLEAF

EverLeaf already has its own optional WASD work. Kaentake is not the source of truth for this feature. Continue EverLeaf's #359 implementation and runtime testing separately.

## P2 - Optional Kaentake gameplay/UI polish

These are not display prerequisites and should remain independent opt-in reviews after the HD stack is proven:
- equipment tooltip/category/attack-speed rewrite;
- buff and cooldown numeric duration overlays;
- mob HP percentage overlay;
- item-icon/effect presentation changes;
- avatar presentation changes.

Do not silently bundle these into the display backport.

## Explicitly do not wholesale-copy

- Kaentake launcher identity/branding
- Kaentake server host configuration
- Kaentake Custom.wz sample assets as EverLeaf content
- Kaentake mutex policy without reviewing EverLeaf's launcher/single-client policy
- Kaentake full Win32/Winsock hook stack over EverLeaf's newer hardening
- any patch address already owned by an EverLeaf correction without reconciling the two implementations

## Current backport order

1. **IMPLEMENTED / RUNTIME GATE:** monitor-sized Alt+Enter and reversible renderer matching.
2. **IMPLEMENTED / RUNTIME GATE:** live Kaentake-style Gr2D resolution path.
3. **IMPLEMENTED / RUNTIME GATE:** active-field refresh and saved UI bounds; validate cursor/status/UI behavior before porting deeper origins.
4. **NEXT AFTER RUNTIME QA:** port only the missing Kaentake UI-origin/field corrections exposed by testing.
5. **PENDING:** repackage `EverLeaf_UI.wz` with a documented path-mirroring override layout and then port Kaentake's resource override/merge model.
6. Review smaller optional UI/system improvements individually.

Nothing in this plan deploys to production automatically. Each phase lands through a reviewable branch/PR and runtime-test gate first.
