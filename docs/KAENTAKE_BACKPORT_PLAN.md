# Kaentake -> EverLeaf Client Backport Plan

Source reference: `iw2d/kaentake` (GMS v83 resizable HD client).

This is a selective backport. EverLeaf keeps its launcher, branding, server protocol, production packaging, diagnostics, and existing client hardening. Kaentake is used as the reference for v83-native display/UI/resource behavior where it is cleaner or more complete.

## Status legend

- **PORT**: bring the Kaentake behavior into EverLeaf, adapted to EverLeaf's architecture.
- **KEEP**: EverLeaf's current implementation is preferable; only borrow small ideas if useful.
- **REWRITE**: use Kaentake as the behavioral reference, but do not copy its implementation wholesale.
- **SKIP**: not needed or conflicts with EverLeaf.

## P0 - Display / fullscreen

### Alt+Enter borderless fullscreen - REWRITE - IN PROGRESS

EverLeaf's previous toggle removed the frame but only sized the window to `Client::m_nGameWidth` x `Client::m_nGameHeight`. It filled the monitor only when the configured render size exactly matched the desktop.

Phase-1 fix:
- Alt+Enter uses the active monitor's full rectangle for the borderless window.
- The pre-toggle framed style, extended style, size, position, and monitor placement are preserved for restore.
- Maple remains in its safer windowed renderer path; this is borderless fullscreen, not exclusive D3D fullscreen.

Runtime gate before merge:
- windowed -> fullscreen -> windowed
- 1280x720, 1366x768, 1600x900, 1920x1080
- mouse/input alignment
- login/world/character select
- in-field UI interaction
- multi-monitor placement
- minimize/restore and Alt-Tab

## P0 - Live resolution stack

### System Options resolution selector - PORT/EXTEND

EverLeaf already uses Kaentake's native v83 `CCtrlComboBox` placement and adds 1280x720. Current EverLeaf behavior only saves the preference for the next launch.

Backport the complete runtime path from Kaentake instead of only the selector UI:

1. `CWzGr2D::ScreenResolution`-style runtime screen-mode reset using the v83 Gr2D mode structure and `FindScreenMode` resolution.
2. Apply the selected resolution immediately from System Options after Maple applies its normal video options.
3. Keep EverLeaf's supported list:
   - 800x600
   - 1024x768
   - 1280x720
   - 1366x768
   - 1600x900
   - 1920x1080
4. Update EverLeaf's runtime width/height state only after the Gr2D resolution change succeeds.
5. Reapply EverLeaf widescreen operands after a successful runtime change.
6. Persist the selected resolution only after the runtime apply succeeds.

Do not reintroduce the old partial renderer reset that caused Alt+Enter/runtime crashes.

## P0 - Resolution-dependent UI/input corrections

### Cursor coordinate handling - PORT

Port Kaentake's screen-size-aware cursor vector and cursor-position handling so mouse coordinates remain correct after runtime resolution changes and borderless fullscreen transitions.

### UI origins - PORT

Port/adapt Kaentake's extended origin model for:
- center/top/right anchored UI
- status bar
- screen messages
- quick slot

This replaces scattered hard-coded 800x600 assumptions with resolution-aware anchors.

### Saved UI window positions - PORT

Clamp stored UI positions to the active resolution and restore sane defaults when a saved position is outside the screen.

### Movable UI bounds/snapping - PORT

Bring over Kaentake's resolution-aware window bounds and snapping where compatible with EverLeaf's current UI behavior.

### Tooltip/context-menu bounds - PORT

Keep tooltips, right-click menus, dialogs, and similar UI inside the active resolution.

### Status/buff/screen-message positioning - PORT

Adapt Kaentake's status bar, quick-slot, temporary-stat, screen-message, and related positioning fixes to EverLeaf's existing widened client.

### Field/view-range corrections - PORT CAREFULLY

Backport the resolution-aware field view range, grid/background reload, weather/effect bounds, limited-view handling, boss HP positioning, and other world-render corrections that are still missing from EverLeaf.

Reuse EverLeaf's already-verified `WidescreenCorrections` where equivalent; do not duplicate patches to the same addresses.

## P1 - Custom WZ override namespace

### Kaentake `Custom.wz` resource override model - PORT/REWRITE

Kaentake mounts a separate `Custom.wz` namespace, enumerates override paths, falls back to the custom namespace when the base lookup misses, and merges custom property children during property serialization.

EverLeaf target:
- use a dedicated EverLeaf custom asset package instead of stuffing donor/custom changes into stock WZ files;
- keep the clean v83 base WZ set intact;
- define explicit override/import rules;
- preserve EverLeaf branding and UI naming;
- do not copy Kaentake's sample `Custom.wz` content wholesale.

Preferred package name: `EverLeaf_Custom.wz` unless the packaging/launcher audit shows a better canonical name.

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

## P2 - Visual/UI polish

After the resolution foundation is stable, audit Kaentake's remaining UI presentation improvements and port only the ones that are compatible with EverLeaf's branded UI and current WZ package.

Candidates include:
- resolution-aware dialog placement
- movable-window behavior
- tooltip placement
- status bar/quick slot placement
- boss HP tag positioning
- screen messages/notices
- map effect bounds

## Explicitly do not wholesale-copy

- Kaentake launcher identity/branding
- Kaentake server host configuration
- Kaentake Custom.wz assets as EverLeaf content
- Kaentake mutex policy without reviewing EverLeaf's launcher/single-client policy
- Kaentake full Win32/Winsock hook stack over EverLeaf's newer hardening
- any patch address already owned by an EverLeaf correction without reconciling the two implementations

## Backport order

1. Fix Alt+Enter monitor-sized borderless fullscreen.
2. Port the complete Kaentake live-resolution/Gr2D path.
3. Port cursor + UI-origin + bounds corrections required by live resolution.
4. Reconcile remaining field/render widescreen fixes with EverLeaf's existing corrections.
5. Runtime-test display stack across all supported resolutions and multi-monitor scenarios.
6. Port the Custom.wz-style override namespace as `EverLeaf_Custom.wz`.
7. Review smaller UI/system improvements individually.

Nothing in this plan deploys to production automatically. Each phase should land through a reviewable branch/PR and runtime-test gate first.
