# EverLeaf Native Client Engineering

EverLeaf maintains isolated, reviewable native layers on top of the stable MapleStory v83 client rather than replacing the game with an opaque third-party client fork.

Current status is tracked in [`../EVERLEAF_MASTER_CHECKLIST.md`](../EVERLEAF_MASTER_CHECKLIST.md). Historical selector/Yuna/copycat reverse-engineering is retained under `../archive/client-research/`.

## Architecture

The maintained client work separates:

- network/bootstrap configuration;
- launcher-managed update/repair;
- launcher-only/single-client launch enforcement;
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
- launcher-only one-time handoff enforcement in the managed native bootstrap;
- one-client-at-a-time enforcement through launcher checks plus a machine-wide native client mutex;
- exclusive single-use launch-ticket consumption;
- widescreen/runtime corrections;
- windowed/borderless/Alt+Enter support separated from game logic;
- presentation-only frame limiting;
- No Whack / combat client work;
- attack while moving;
- No Breath;
- optional/opt-in WASD input;
- local crash/freeze diagnostics without automatic telemetry upload;
- EverLeaf-native Discord Rich Presence through local Discord IPC;
- source support for richer character/level/job/map Discord activity using pinned v83 getters;
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

The maintained implementation is EverLeaf-owned, uses local Discord named-pipe IPC, has no bot token/OAuth secret, and does not require the Discord Game SDK or Yuna runtime binaries.

Richer gameplay activity is now implemented on canonical `master` using GMS v83.1 contracts recovered from the project-supplied `Angel.idb` and independently cross-checked against other v83 native-client work. The pinned contracts are:

- `CWvsContext` singleton: `0x00BE7918`;
- `CUserLocal` singleton: `0x00BEBF98`;
- `get_field()`: `0x00437A0C`;
- `CWvsContext::GetCharacterName()`: `0x004AC308`;
- `CUserLocal::Update()`: `0x0094A144`;
- `CUserLocal::GetCharacterLevel()`: `0x00949B15`;
- `CUserLocal::GetJobCode()`: `0x0095FFC3`;
- `CUserLocal::GetFieldID()`: `0x009613E0`;
- `CWvsContext::GetCurFieldID()`: `0x00A1238B`.

These addresses are specific to the pinned EverLeaf GMS v83 client image. They must be re-derived/re-verified before use with another MapleStory client version or binary baseline.

The gameplay sampler runs from the hooked `CUserLocal::Update()` path on Maple's game thread. The background Discord IPC worker only reads the already-copied activity strings; it does not call Maple getters or walk Maple objects itself.

Before richer activity is published, the sampler requires:

- the active `CUserLocal` object to match the v83 singleton;
- a valid `CWvsContext`;
- a live field returned by `get_field()`;
- a bounded non-empty character name;
- a nonzero character level;
- exact agreement between `CUserLocal::GetFieldID()` and `CWvsContext::GetCurFieldID()`.

Any access fault, transition, missing object, or field-ID disagreement fails closed to the existing generic EverLeaf presence. Supported job labels are derived from EverLeaf's maintained v83 `client.Job` IDs; external post-v83 job tables are not imported into the client.

Source regression coverage protects job labels, gameplay formatting, Discord IPC framing/acknowledgement behavior, the pinned address markers, and the field-ID cross-check. Managed-client build/publication and runtime verification are still pending the planned batched client rollout.

## Launcher boundary

The launcher owns managed update/repair and launch policy. EverLeaf's intended player contract is:

- launch through `EverLeafLauncher.exe` only;
- do not run `EverLeaf.exe` directly;
- only one EverLeaf game client may run on a machine at a time.

The managed native bootstrap requires the launcher's transient `.everleaf-launch` handoff. Ticket consumption is exclusive/single-use, and the stock client exits when the handoff is missing or invalid.

For multi-client prevention, the launcher checks both the `EverLeaf` process and `Global\EverLeafMS.Client.SingleInstance` immediately before Play. The native bootstrap acquires the same machine-wide mutex and retains its handle for the lifetime of the game, so a second stock client fails closed even if two launcher windows race.

These are client/launcher enforcement layers, not a claim that software under the player's local administrative control is cryptographically tamper-proof. If the project later requires server-backed proof that each login came from an authorized, unmodified launcher session, that must be implemented as an explicit server-validated launch-session protocol.

The native runtime should not reinvent an unsigned copy-over patcher, global registry hacks, or opaque third-party loader chain.

## Deferred Phase 2 UI work

The broader login/world/character-select visual overhaul remains intentionally deferred until the Kaentake review is complete. This includes connected panorama work, broader branding/UI replacement, and direct modern class-card/Evan creation.

The existing Beginner → NPC → Evan path remains the accepted flow while that work is paused.

## Reverse-engineering policy

Donor clients/WZs may be used as research/reference after provenance and compatibility review. Do not ship opaque donor DLLs, anti-debug/process-scanning code, kill switches, global Accessibility registry modifications, antivirus-exclusion instructions, or donor endpoint dependencies.

Prefer EverLeaf-owned source implementations and selective WZ backports with matching server data and real-client validation.
