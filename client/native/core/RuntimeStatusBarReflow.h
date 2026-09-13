#pragma once

#include "Client.h"
#include "CrashDiagnostics.h"

#include <windows.h>

// Live-resolution status-bar reflow for EverLeaf's existing v83 HD patch set.
//
// EverLeaf already patches CUIStatusBar creation to use height - 578. Those
// creation-time patches are correct on a fresh launch, but an already-created
// status bar does not automatically consume the new Y coordinate when Gr2D is
// resized in place. Reposition the existing CUIStatusBar through the stock
// CWnd::OnMoveWnd path instead of replacing its origin, which would double-apply
// EverLeaf's existing status-bar offsets.
namespace RuntimeStatusBarReflow {
namespace detail {

constexpr DWORD kStatusBarInstanceAddress = 0x00BEC208;
constexpr DWORD kCWndOnMoveWndAddress = 0x009DEB57;
using OnMoveWndFn = void(__thiscall*)(void*, int, int);

inline bool Apply() {
    __try {
        void* statusBar = *reinterpret_cast<void**>(kStatusBarInstanceAddress);
        if (!statusBar) {
            // Login/world/character select legitimately have no status bar.
            return true;
        }

        const int x = 0;
        const int y = Client::m_nGameHeight - 578;
        reinterpret_cast<OnMoveWndFn>(kCWndOnMoveWndAddress)(statusBar, x, y);
        CrashDiagnostics::LogEvent("status bar moved after live resolution");
        return true;
    }
    __except (EXCEPTION_EXECUTE_HANDLER) {
        CrashDiagnostics::LogEvent("status bar live reflow raised an exception");
        return false;
    }
}

} // namespace detail

inline bool ApplyCurrent() {
    return detail::Apply();
}

} // namespace RuntimeStatusBarReflow
