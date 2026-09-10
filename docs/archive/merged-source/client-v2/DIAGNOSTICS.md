# EverLeaf Client v2 local diagnostics

This layer is intentionally local-only and privacy-minimal.

## Outputs

The files below are created beside the game executable. None is uploaded or transmitted automatically.

### `EverLeafClient.log`

Recreated for each launch. It may contain:

- timestamped bootstrap/runtime phase names
- process/thread IDs
- configured client resolution and windowed-state flag
- an unhandled exception code and address
- the executable-relative crash offset
- x86 EIP/ESP/EBP values when available
- coarse crash/freeze subsystem status

### `EverLeafCrash.dmp`

On an unhandled crash, Client v2 may overwrite one local minidump. It resolves `MiniDumpWriteDump` from the absolute Windows System32 `dbghelp.dll` path so a stale/wrong-architecture `dbghelp.dll` beside the game cannot be selected through DLL search order.

The dump type is deliberately bounded to `MiniDumpNormal | MiniDumpWithThreadInfo`. Full-memory dump flags are forbidden. A new crash overwrites the previous dump rather than accumulating an unbounded crash archive.

### `EverLeafFreeze.txt`

Client v2 starts a lightweight window-responsiveness watchdog after diagnostics initialization. It finds only the current process's `MapleStoryClass` top-level window and sends a bounded `WM_NULL` probe every five seconds. A freeze report is written only after three consecutive 1.5-second `ERROR_TIMEOUT` results. The report is overwritten on the next detected freeze and the watchdog resets after responsiveness returns.

The freeze watchdog does not enumerate other processes, inspect threads in other processes, scan tools/debuggers, or collect packet/game-state contents.

## Privacy boundary

The diagnostics layer must not intentionally collect:

- account names or email addresses
- character names or IDs
- passwords, PIC values, launcher tickets, session tokens, or IP credentials
- chat text
- packet payloads
- inventory/account data
- remote telemetry identifiers

The bounded crash minidump can contain ordinary crash/thread context produced by Windows debugging APIs, so it should still be treated as a local diagnostic artifact. EverLeaf does not automatically transmit it.

## Crash-handler compatibility

Client v2 installs an observing unhandled-exception filter and preserves/chains the previously installed filter. It must not swallow the exception or attempt to continue execution after an unhandled access violation.

## Copycat audit rationale

The 2026-09-05 full copycat/Yuna audit showed a richer local crash/freeze reporting layer, but it also showed process/thread scanning, tool detection, registry machine flags and other behavior that EverLeaf intentionally does not reproduce. It also exposed a wrong-architecture local `dbghelp.dll` hazard in that folder. Client v2 takes only the useful diagnostic concept while keeping a much narrower privacy and loader boundary.

## Purpose

The diagnostics layer exists to make FPS, input, display, WZ and native-hook testing debuggable without adding server-side telemetry or collecting player data.
