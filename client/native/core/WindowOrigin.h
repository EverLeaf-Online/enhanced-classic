#pragma once

// Diagnostic branch only: phase 9/10 origin migration disabled after runtime
// testing showed double-shifted UI and desynchronized click regions at 1280x720.
namespace WindowOrigin {
inline bool ApplyCurrent() { return true; }
inline bool Install() { return true; }
inline void Shutdown() {}
}
