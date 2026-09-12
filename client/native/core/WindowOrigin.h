#pragma once

#include "Client.h"
#include "Memory.h"
#include "CrashDiagnostics.h"

#include <windows.h>
#include <oleauto.h>
#include <cstddef>
#include <iostream>

// Kaentake-inspired CWndMan origin infrastructure for EverLeaf's pinned v83
// client. Phase 9 corrected the stock m_pOrgWindow. Phase 10 adds the owned
// extended origin vectors and their lifecycle, but deliberately does not route
// individual windows/callers onto those vectors yet.
namespace WindowOrigin {
namespace detail {

constexpr DWORD kWndManInstanceAddress = 0x00BEC20C;
constexpr DWORD kWndManConstructorAddress = 0x009E2C42;
constexpr DWORD kWndManDestructorAddress = 0x009E3026;
constexpr size_t kOrgWindowOffset = 0xDC;
constexpr DWORD kGr2DHolderAddress = 0x00BF14EC;
constexpr DWORD kPcomApiTableAddress = 0x00BF0CC0;
constexpr int kOriginCount = 9;

// Runtime origin rewrite is intentionally disabled while EverLeaf still uses
// its legacy fixed-address HD/UI positioning patches. Applying both systems at
// once double-shifts rendered windows and desynchronizes hit testing. Phase 8
// remains the validated UI baseline; the complete Kaentake routing/input stack
// must replace the legacy positioning as one coordinated migration.
inline bool ApplyCurrent() {
    return true;
}

inline bool Install() {
    CrashDiagnostics::LogEvent("CWndMan origin rewrite deferred; legacy EverLeaf UI coordinates retained");
    std::cout << "EverLeaf Client v2: CWndMan origin rewrite deferred" << std::endl;
    return true;
}

inline void Shutdown() {
}

} // namespace detail

inline bool ApplyCurrent() {
    return detail::ApplyCurrent();
}

inline bool Install() {
    return detail::Install();
}

inline void Shutdown() {
    detail::Shutdown();
}

} // namespace WindowOrigin
