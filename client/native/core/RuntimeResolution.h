#pragma once

#include "AutoTypes.h"
#include "Client.h"
#include "Memory.h"
#include "CrashDiagnostics.h"
#include "WidescreenCorrections.h"
#include "AddyLocations.h"

#include <windows.h>
#include <cstddef>
#include <cstdint>
#include <cstring>

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
constexpr int kMinWidth = 800;
constexpr int kMinHeight = 600;
constexpr int kMaxWidth = 1920;
constexpr int kMaxHeight = 1080;

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
    return width >= kMinWidth && width <= kMaxWidth &&
           height >= kMinHeight && height <= kMaxHeight;
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

    // Correct inherited axis mistakes after the broad legacy patch pass.
    WidescreenCorrections::ApplyCurrent();
    Memory::WriteInt(dwToolTipLimitVPos + 1, static_cast<unsigned int>(height - 1));

    // Client::UpdateResolution intentionally routes an inherited malformed write
    // away from 0x89B797. Its startup guard does not re-run after the first patch,
    // so explicitly refresh the two real screen-message reset operands here.
    Memory::WriteInt(0x0089B798, static_cast<unsigned int>(height - 166));
    Memory::WriteInt(0x0089BA04, static_cast<unsigned int>(width - 300));

    RefreshWindowGeometry(width, height);
}

} // namespace detail

inline bool Apply(int width, int height) {
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
        // Gr2D has already accepted the mode; restore EverLeaf's bookkeeping and
        // patch operands as far as possible so a failed correction pass does not
        // leave width/height globals describing a different mode.
        Client::m_nGameWidth = previousWidth;
        Client::m_nGameHeight = previousHeight;
        Client::UpdateResolution();
        WidescreenCorrections::ApplyCurrent();
        CrashDiagnostics::LogEvent("live resolution correction pass failed");
        return false;
    }
}

} // namespace RuntimeResolution
