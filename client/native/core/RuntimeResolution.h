#pragma once

#include "AutoTypes.h"
#include "Client.h"
#include "Memory.h"
#include "CrashDiagnostics.h"
#include "WidescreenCorrections.h"
#include "FieldRenderCorrections.h"
#include "RuntimeUiSync.h"
#include "RuntimeHudAnchors.h"
#include "AddyLocations.h"

#include <windows.h>
#include <cstddef>
#include <cstdint>
#include <cstring>
#include <iostream>

// Kaentake-inspired live resolution bridge for EverLeaf's pinned GMS v83 client.
//
// Kaentake proved that the v83 Gr2D object can change screen modes safely by
// resolving Gr2D_DX8!FindScreenMode, replacing CWzGr2D::m_screenMode, and marking
// the device D3DERR_DEVICENOTRESET. EverLeaf keeps its own HD/UI correction
// system and reapplies it only after the renderer accepts the requested mode.
namespace RuntimeResolution {
namespace detail {

constexpr uintptr_t kGr2DHolderAddress = 0x00BF14EC;
constexpr size_t kScreenModeOffset = 0x20;
constexpr size_t kInitializedOffset = 0x90;
constexpr size_t kErrorCodeOffset = 0x94;
constexpr int kDeviceNotReset = static_cast<int>(0x88760869u);

// Pinned GMS v83 field helpers used by Kaentake after a successful screen-mode
// change. EverLeaf's UpdateResolution() patches the RestoreViewRange operands for
// the new dimensions; invoking it here makes the already-loaded field consume
// those new values immediately, then ReloadBack rebuilds the visible background.
constexpr uintptr_t kGetFieldAddress = 0x00437A0C;
constexpr uintptr_t kRestoreViewRangeAddress = 0x00641EF1;
constexpr uintptr_t kReloadBackAddress = 0x00644491;

struct ScreenMode {
    int width;
    int height;
    unsigned char reserved[0x50];
    int fullScreen;
};
static_assert(sizeof(ScreenMode) == 0x5C, "v83 Gr2D screen mode layout changed");

using FindScreenModeFn = int(__thiscall*)(void*, ScreenMode*, int, int, int, int);
static FindScreenModeFn gFindScreenMode = nullptr;

inline bool IsSupportedSize(int width, int height) {
    return
        (width == 800 && height == 600) ||
        (width == 1024 && height == 768) ||
        (width == 1280 && height == 720) ||
        (width == 1366 && height == 768) ||
        (width == 1600 && height == 900) ||
        (width == 1920 && height == 1080);
}

inline uintptr_t FindScreenModePattern() {
    HMODULE module = GetModuleHandleA("Gr2D_DX8.dll");
    if (!module) {
        return 0;
    }

    auto base = reinterpret_cast<unsigned char*>(module);
    auto dos = reinterpret_cast<PIMAGE_DOS_HEADER>(base);
    if (!dos || dos->e_magic != IMAGE_DOS_SIGNATURE) {
        return 0;
    }

    auto nt = reinterpret_cast<PIMAGE_NT_HEADERS>(base + dos->e_lfanew);
    if (!nt || nt->Signature != IMAGE_NT_SIGNATURE) {
        return 0;
    }

    const size_t imageSize = nt->OptionalHeader.SizeOfImage;
    // Kaentake's v83 signature for CWzGr2D::FindScreenMode.
    const unsigned char pattern[] = {
        0xB8, 0x00, 0x00, 0x00, 0x00,
        0xE8, 0x00, 0x00, 0x00, 0x00,
        0x83, 0xEC, 0x68
    };
    const char mask[] = "x????x????xxx";
    constexpr size_t patternSize = sizeof(pattern);

    if (imageSize < patternSize) {
        return 0;
    }

    for (size_t i = 0; i <= imageSize - patternSize; ++i) {
        bool match = true;
        for (size_t j = 0; j < patternSize; ++j) {
            if (mask[j] == 'x' && base[i + j] != pattern[j]) {
                match = false;
                break;
            }
        }
        if (match) {
            return reinterpret_cast<uintptr_t>(base + i);
        }
    }
    return 0;
}

inline bool ResolveFindScreenMode() {
    if (gFindScreenMode) {
        return true;
    }

    const uintptr_t address = FindScreenModePattern();
    if (!address) {
        CrashDiagnostics::LogEvent("Gr2D FindScreenMode signature unavailable");
        return false;
    }

    gFindScreenMode = reinterpret_cast<FindScreenModeFn>(address);
    CrashDiagnostics::LogEvent("Gr2D FindScreenMode resolved");
    return true;
}

inline bool SetRendererMode(int width, int height) {
    if (!IsSupportedSize(width, height) || !ResolveFindScreenMode()) {
        return false;
    }

    __try {
        auto holder = reinterpret_cast<_com_ptr_t_com_IIID_IWzGr2D*>(kGr2DHolderAddress);
        if (!holder || !holder->m_pInterface) {
            CrashDiagnostics::LogEvent("Gr2D interface unavailable for live resolution");
            return false;
        }

        auto object = reinterpret_cast<unsigned char*>(holder->m_pInterface);
        auto current = reinterpret_cast<ScreenMode*>(object + kScreenModeOffset);
        const int initialized = *reinterpret_cast<int*>(object + kInitializedOffset);
        if (!initialized) {
            CrashDiagnostics::LogEvent("Gr2D not initialized for live resolution");
            return false;
        }

        if (current->width == width && current->height == height) {
            return true;
        }

        ScreenMode next = {};
        if (!gFindScreenMode(
                object,
                &next,
                current->fullScreen,
                width,
                height,
                0)) {
            CrashDiagnostics::LogEvent("Gr2D rejected live resolution mode");
            return false;
        }

        std::memcpy(current, &next, sizeof(next));
        *reinterpret_cast<int*>(object + kErrorCodeOffset) = kDeviceNotReset;
        return true;
    }
    __except (EXCEPTION_EXECUTE_HANDLER) {
        CrashDiagnostics::LogEvent("Gr2D live resolution raised an exception");
        return false;
    }
}

inline void RefreshActiveField() {
    __try {
        using GetFieldFn = void*(__cdecl*)();
        using FieldFn = void(__thiscall*)(void*);

        void* field = reinterpret_cast<GetFieldFn>(kGetFieldAddress)();
        if (!field) {
            return;
        }

        reinterpret_cast<FieldFn>(kRestoreViewRangeAddress)(field);
        reinterpret_cast<FieldFn>(kReloadBackAddress)(field);
        CrashDiagnostics::LogEvent("active field refreshed after live resolution");
    }
    __except (EXCEPTION_EXECUTE_HANDLER) {
        // A live resolution change should not terminate the client merely because
        // no compatible field is active (login/world/character select included).
        CrashDiagnostics::LogEvent("active field refresh unavailable after live resolution");
    }
}

inline void RefreshWindowGeometry(int width, int height) {
    HWND window = FindWindowA("MapleStoryClass", nullptr);
    if (!window) {
        return;
    }

    DWORD processId = 0;
    GetWindowThreadProcessId(window, &processId);
    if (processId != GetCurrentProcessId()) {
        return;
    }

    const LONG_PTR style = GetWindowLongPtrA(window, GWL_STYLE);
    // Phase 1 owns monitor-sized WS_POPUP borderless fullscreen. Do not shrink a
    // fullscreen window back to the render resolution when Gr2D changes size.
    if ((style & WS_POPUP) != 0 && (style & WS_CAPTION) == 0) {
        InvalidateRect(window, nullptr, FALSE);
        return;
    }

    const LONG_PTR exStyle = GetWindowLongPtrA(window, GWL_EXSTYLE);
    RECT outer = { 0, 0, width, height };
    if (!AdjustWindowRectEx(
            &outer,
            static_cast<DWORD>(style),
            FALSE,
            static_cast<DWORD>(exStyle))) {
        return;
    }

    const HMONITOR monitor = MonitorFromWindow(window, MONITOR_DEFAULTTONEAREST);
    MONITORINFO info = {};
    info.cbSize = sizeof(info);
    if (!monitor || !GetMonitorInfoW(monitor, &info)) {
        return;
    }

    const int outerWidth = outer.right - outer.left;
    const int outerHeight = outer.bottom - outer.top;
    const int workWidth = info.rcWork.right - info.rcWork.left;
    const int workHeight = info.rcWork.bottom - info.rcWork.top;
    const int x = info.rcWork.left + (workWidth - outerWidth) / 2;
    const int y = info.rcWork.top + (workHeight - outerHeight) / 2;

    SetWindowPos(
        window,
        nullptr,
        x,
        y,
        outerWidth,
        outerHeight,
        SWP_NOZORDER | SWP_NOOWNERZORDER | SWP_FRAMECHANGED | SWP_SHOWWINDOW
    );
    InvalidateRect(window, nullptr, FALSE);
}

inline void ApplyEverLeafRuntimeCorrections(int width, int height) {
    Client::m_nGameWidth = width;
    Client::m_nGameHeight = height;

    // Recalculate EverLeaf's established HD/cash-shop/login/status offsets.
    // Memory::CodeCave is idempotent for these fixed hook sites, while the
    // associated globals are recalculated from the new dimensions each call.
    Client::UpdateResolution();

    // Correct inherited axis mistakes and the verified field/render extents after
    // the broad legacy patch pass, which may rewrite some of them each call.
    WidescreenCorrections::ApplyCurrent();
    FieldRenderCorrections::ApplyCurrent();

    // Gr2D changes size in-place, so CWndMan is not reconstructed. Reapply the
    // same stock origin geometry used by a clean launch at this resolution and
    // resync the cursor vector before any more UI work occurs.
    RuntimeUiSync::ApplyCurrent();
    RuntimeHudAnchors::ApplyCurrent();

    Memory::WriteInt(dwToolTipLimitVPos + 1, static_cast<unsigned int>(height - 1));

    // Client::UpdateResolution intentionally routes an inherited malformed write
    // away from 0x89B797. Its startup guard does not re-run after the first patch,
    // so explicitly refresh the two real screen-message reset operands here.
    Memory::WriteInt(0x0089B798, static_cast<unsigned int>(height - 166));
    Memory::WriteInt(0x0089BA04, static_cast<unsigned int>(width - 300));

    RefreshActiveField();
    RefreshWindowGeometry(width, height);
}

inline void BestEffortCorrectionState(int width, int height) {
    Client::m_nGameWidth = width;
    Client::m_nGameHeight = height;
    __try {
        ApplyEverLeafRuntimeCorrections(width, height);
    }
    __except (EXCEPTION_EXECUTE_HANDLER) {
        // Keep the core width/height globals and the verified corrections coherent
        // even if one of the broad inherited HD patches was the source of the
        // original exception.
        Client::m_nGameWidth = width;
        Client::m_nGameHeight = height;
        WidescreenCorrections::ApplyCurrent();
        FieldRenderCorrections::ApplyCurrent();
        CrashDiagnostics::LogEvent("best-effort live resolution correction state applied");
    }
}

} // namespace detail

inline bool Apply(int width, int height) {
    if (!detail::IsSupportedSize(width, height)) {
        CrashDiagnostics::LogEvent("unsupported live resolution rejected");
        return false;
    }

    if (width == Client::m_nGameWidth && height == Client::m_nGameHeight) {
        return true;
    }

    const int previousWidth = Client::m_nGameWidth;
    const int previousHeight = Client::m_nGameHeight;

    if (!detail::SetRendererMode(width, height)) {
        return false;
    }

    __try {
        detail::ApplyEverLeafRuntimeCorrections(width, height);
        CrashDiagnostics::LogEvent("live resolution applied");
        std::cout << "EverLeaf Client v2: live resolution applied at "
                  << width << "x" << height << std::endl;
        return true;
    }
    __except (EXCEPTION_EXECUTE_HANDLER) {
        // Gr2D already accepted the requested mode. Attempt to put the renderer
        // itself back before restoring EverLeaf's bookkeeping; if that rollback
        // fails, keep bookkeeping aligned with the new renderer instead of lying
        // about the active mode.
        const bool rendererRolledBack = detail::SetRendererMode(previousWidth, previousHeight);
        const int coherentWidth = rendererRolledBack ? previousWidth : width;
        const int coherentHeight = rendererRolledBack ? previousHeight : height;
        detail::BestEffortCorrectionState(coherentWidth, coherentHeight);

        CrashDiagnostics::LogEvent(
            rendererRolledBack
                ? "live resolution correction failed; renderer rolled back"
                : "live resolution correction failed; renderer rollback failed");
        return false;
    }
}

} // namespace RuntimeResolution
