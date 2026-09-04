# EverLeaf Client v2 local diagnostics

This layer is intentionally local-only and privacy-minimal.

## Output

`EverLeafClient.log` is created beside the game executable for each launch.

The log may contain:
- timestamped bootstrap/runtime phase names
- process/thread IDs
- configured client resolution and windowed-state flag
- an unhandled exception code and address
- the executable-relative crash offset
- x86 EIP/ESP/EBP values when available

The log must not contain:
- account names or email addresses
- character names or IDs
- passwords, PIC values, launcher tickets, session tokens, or IP credentials
- chat text
- packet payloads
- inventory/account data
- remote telemetry identifiers

Nothing in this layer uploads or transmits the log.

## Crash-handler compatibility

Client v2 installs an observing unhandled-exception filter and preserves/chains the previously installed filter. It must not swallow the exception or attempt to continue execution after an unhandled access violation.

## Purpose

The diagnostics layer exists to make later FPS, input, display, and native-hook testing debuggable without adding server-side telemetry or collecting player data.
