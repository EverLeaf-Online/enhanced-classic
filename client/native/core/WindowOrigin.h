#pragma once

// Disabled diagnostic shim for the phase-18 debug branch.
// Runtime validation proved phase 9/10's global CWndMan origin migration is not
// compatible with EverLeaf's existing fixed-address HD/UI patches yet: visual
// windows are double-shifted and mouse hit testing remains in the legacy space.
namespace WindowOrigin {
inline bool ApplyCurrent() { return true; }
inline bool Install() { return true; }
inline void Shutdown() {}
}
