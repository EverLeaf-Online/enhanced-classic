#pragma once

// Phase 9/10 CWndMan origin rewrite is intentionally disabled for the debug branch.
// Runtime testing on 2026-09-12 showed that combining Kaentake's base-origin shift
// with EverLeaf's existing HD/UI fixed-address patches double-shifts rendered UI
// and leaves hit-test coordinates behind. The coordinated origin/input migration
// will be rebuilt after phase 8 is reconfirmed as the visual/input baseline.
namespace WindowOrigin {
inline bool ApplyCurrent() { return true; }
inline bool Install() { return true; }
inline void Shutdown() {}
}
