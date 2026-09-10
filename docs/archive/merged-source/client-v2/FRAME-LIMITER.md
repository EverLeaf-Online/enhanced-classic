# EverLeaf Client v2 frame timing

The frame limiter controls presentation cadence only. It does not alter MapleStory v83's fixed 30 ms game-logic update step.

## Defaults

- foreground presentation cap: 60 FPS
- background presentation cap: 15 FPS
- background limiting: enabled

`ForegroundFPSCap=0` disables the added foreground cap and leaves presentation timing to the stock client/render path. Nonzero foreground values are clamped to 30-240 FPS. Background values are clamped to 5-60 FPS.

## Implementation boundary

Client v2 detours the v83 `IWzGr2D::RenderFrame` owner and waits for the configured presentation slot before invoking the original function. The existing `CWvsApp::CallUpdate` 30 ms update step remains unchanged.

This separation is intentional: monitor refresh rate and foreground/background power policy must not change movement, combat, quest, cooldown, or server timing semantics.

## Runtime validation

Before promotion, test 60/120/144 foreground caps, uncapped foreground, 15 FPS background, minimize/restore, alt-tab, login/world/character/PIC/game transitions, map transitions, combat, and long-session timer drift.
