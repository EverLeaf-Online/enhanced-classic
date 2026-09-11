#pragma once

#include <windows.h>

namespace CrashDiagnostics {
inline void LogEvent(const char* message) {
    if (!message) return;
    OutputDebugStringA("EverLeaf Discord: ");
    OutputDebugStringA(message);
    OutputDebugStringA("\n");
}
}
