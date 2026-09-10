# EverLeaf Native Client Engineering

EverLeaf maintains isolated, reviewable native layers on top of the stable MapleStory v83 client rather than replacing the game with an opaque third-party client fork.

Current status is tracked in [`../EVERLEAF_MASTER_CHECKLIST.md`](../EVERLEAF_MASTER_CHECKLIST.md). Historical selector/Yuna/copycat reverse-engineering is retained under `../archive/client-research/`.

## Architecture

The maintained client work separates:

- network/bootstrap configuration;
- launcher-managed update/repair;
- source-built Win32 bootstrap/runtime extensions;
- display/windowing modernization;
- presentation-only frame limiting;
- optional input improvements such as WASD;
- local diagnostics;
- native Discord Rich Presence;
- managed WZ/client overlays.

The v83 server protocol remains authoritative. Client convenience must not weaken server-side state, transaction, movement, combat, or economy validation.

## Current maintained features

The current release line includes or has validated source support for:

- 1280×720 gameplay/client configuration;
- Win32 startup/bootstrap hardening;
- race-safe dinput8 proxy/bootstrap behavior;
- widescreen/runtime corrections;
- windowed/borderless/Alt+Enter support separated from game logic;
- presentation-only frame limiting;
- No Whack / combat client work;
- attack while moving;
- No Breath;
- optional/opt-in WASD input;
- local crash/freeze diagnostics without automatic telemetry upload;
- EverLeaf-native Discord Rich Presence through local Discord IPC;
- source-built Windows client validation in GitHub CI;
- managed overlay publication through the launcher/patch system.

## Frame timing

The frame limiter controls presentation cadence only; it does not change the stock v83 fixed game-logic update step.

Default documented behavior:

- foreground presentation cap: 60 FPS;
- background presentation cap: 15 FPS;
- background limiting enabled;
- foreground `0` means no added EverLeaf foreground cap;
- nonzero foreground values are bounded to a safe configured range;
- background values are likewise bounded.

Monitor refresh rate or foreground/background presentation policy must never change movement, combat, quest, cooldown, or server timing semantics.

Runtime testing should cover multiple foreground caps, uncapped presentation, background limiting, minimize/restore, Alt-Tab, login/world/character/PIC/game transitions, maps, combat, and long-session timer drift.

## Local diagnostics

Client diagnostics are intentionally local-only and privacy-minimal.

Possible local files beside the executable include:

- `EverLeafClient.log` — bootstrap/runtime phases and bounded crash context;
- `EverLeafCrash.dmp` — bounded local minidump on unhandled crash;
- `EverLeafFreeze.txt` — bounded responsiveness watchdog output.

They are not uploaded automatically.

Diagnostics must not intentionally collect account credentials, passwords, PIC values, launcher tickets, session tokens, chat text, packet payloads, inventory/account contents, or remote telemetry identifiers.

Crash dumps can contain ordinary process/thread debugging context and should still be treated as sensitive local diagnostic artifacts when a player submits one manually.

## Discord Rich Presence

The maintained implementation is EverLeaf-owned, uses local Discord named-pipe IPC, has no bot token/OAuth secret, and does not require the Discord Game SDK or Yuna runtime binaries. Character/map/job activity hooks remain gated on verified v83 memory contracts before enabling richer runtime activity.

## Launcher boundary

The launcher owns managed update/repair and launch policy. The native runtime should not reinvent an unsigned copy-over patcher, global registry hacks, or opaque third-party loader chain.

Player-facing guidance is launcher-first. Raw EXE launches are not the supported normal path because they can bypass update/repair and launcher-ticket assumptions.

## Deferred Phase 2 UI work

The broader login/world/character-select visual overhaul remains intentionally deferred until the Kaentake review is complete. This includes connected panorama work, broader branding/UI replacement, and direct modern class-card/Evan creation.

The existing Beginner → NPC → Evan path remains the accepted flow while that work is paused.

## Reverse-engineering policy

Donor clients/WZs may be used as research/reference after provenance and compatibility review. Do not ship opaque donor DLLs, anti-debug/process-scanning code, kill switches, global Accessibility registry modifications, antivirus-exclusion instructions, or donor endpoint dependencies.

Prefer EverLeaf-owned source implementations and selective WZ backports with matching server data and real-client validation.
