#pragma once

#include "Client.h"
#include "Memory.h"
#include "CrashDiagnostics.h"

#include <windows.h>
#include <cstdio>
#include <cstdint>

// Kaentake-style UI bounds for the pinned GMS v83 client. Phase 2 clamps saved
// CConfig positions; phase 3 adds runtime context-menu placement so a right-click
// menu cannot open beyond the active resolution after HD/live-resolution changes.
namespace ResolutionUIBounds {
namespace detail {

constexpr DWORD kConfigSingletonAddress = 0x00BEBF9C;
constexpr DWORD kGetUIWndPosAddress = 0x0049F0B5;
constexpr DWORD kLoadCharacterAddress = 0x0049D0B6;
constexpr size_t kUIWndXOffset = 0xCC;
constexpr size_t kUIWndYOffset = 0x154;
constexpr int kUIWindowCount = 34;

// Kaentake patches this v83 CUIContextMenu call site so the menu is created at
// the current cursor position but clamped to the active screen dimensions.
constexpr DWORD kContextMenuCreateCallSite = 0x009966E3;
constexpr DWORD kCWndCreateWndAddress = 0x009DE4D2;
constexpr size_t kContextMenuButtonCountOffset = 0xCC;
constexpr int kContextMenuWidth = 100;
constexpr int kContextMenuRowHeight = 15;

using GetUIWndPosFn = void(__thiscall*)(void*, int, int*, int*, int*);
using LoadCharacterFn = void(__thiscall*)(void*, int, unsigned int);
using CreateWndFn = void(__thiscall*)(void*, int, int, int, int, int, int, void*, int);

static GetUIWndPosFn gGetUIWndPos = reinterpret_cast<GetUIWndPosFn>(kGetUIWndPosAddress);
static LoadCharacterFn gLoadCharacter = reinterpret_cast<LoadCharacterFn>(kLoadCharacterAddress);
static bool gInstalled = false;
static int gActiveWidth = 800;
static int gActiveHeight = 600;

inline void GetDefaultPosition(int uiType, int* x, int* y) {
    int defaultX = 0;
    int defaultY = 0;

    switch (uiType) {
    case 4:
        defaultX = 8;
        defaultY = 8;
        break;
    case 8:
        defaultX = 500;
        defaultY = 50;
        break;
    case 9:
        defaultX = 250;
        defaultY = 100;
        break;
    case 22:
        defaultX = 500;
        defaultY = 100;
        break;
    case 14:
        defaultX = 600;
        defaultY = 35;
        break;
    case 15:
        defaultX = 730;
        defaultY = 400;
        break;
    case 18:
        defaultX = 11;
        defaultY = 24;
        break;
    case 20:
        defaultX = 720;
        defaultY = 80;
        break;
    case 23:
    case 31:
    case 33:
        defaultX = 100;
        defaultY = 100;
        break;
    case 24:
    case 25:
    case 26:
    case 27:
    case 29:
    case 32:
        defaultX = 244;
        defaultY = 105;
        break;
    case 30:
        defaultX = 769;
        defaultY = 343;
        break;
    default:
        defaultX = 8 * (3 * uiType + 3);
        defaultY = defaultX;
        break;
    }

    if (x) *x = defaultX;
    if (y) *y = defaultY;
}

inline bool IsOutside(int x, int y, int width, int height) {
    return x < -5 || x > width - 6 || y < -5 || y > height - 6;
}

inline void ClampConfigObject(void* config, int width, int height) {
    if (!config || width < 800 || height < 600) {
        return;
    }

    __try {
        auto bytes = reinterpret_cast<unsigned char*>(config);
        auto xs = reinterpret_cast<int*>(bytes + kUIWndXOffset);
        auto ys = reinterpret_cast<int*>(bytes + kUIWndYOffset);

        for (int i = 0; i < kUIWindowCount; ++i) {
            if (!IsOutside(xs[i], ys[i], width, height)) {
                continue;
            }

            int defaultX = 0;
            int defaultY = 0;
            GetDefaultPosition(i, &defaultX, &defaultY);
            xs[i] = defaultX;
            ys[i] = defaultY;
        }
    }
    __except (EXCEPTION_EXECUTE_HANDLER) {
        CrashDiagnostics::LogEvent("saved UI bounds clamp raised an exception");
    }
}

inline HWND FindGameWindow() {
    HWND window = FindWindowA("MapleStoryClass", nullptr);
    if (!window) {
        return nullptr;
    }

    DWORD processId = 0;
    GetWindowThreadProcessId(window, &processId);
    return processId == GetCurrentProcessId() ? window : nullptr;
}

inline void CreateContextMenuFallback(
    void* self,
    int l,
    int t,
    int w,
    int h,
    int z,
    int screenCoord,
    void* data) {
    reinterpret_cast<CreateWndFn>(kCWndCreateWndAddress)(
        self,
        l,
        t,
        w,
        h,
        z,
        screenCoord,
        data,
        1);
}

inline void __fastcall ContextMenuCreateHook(
    void* self,
    void*,
    int l,
    int t,
    int w,
    int h,
    int z,
    int screenCoord,
    void* data) {
    if (!self) {
        return;
    }

    __try {
        const int buttonCount = *reinterpret_cast<int*>(
            reinterpret_cast<unsigned char*>(self) + kContextMenuButtonCountOffset);
        HWND window = FindGameWindow();
        if (!window || buttonCount < 0 || buttonCount > 100) {
            CreateContextMenuFallback(self, l, t, w, h, z, screenCoord, data);
            return;
        }

        POINT cursor = {};
        if (!GetCursorPos(&cursor) || !ScreenToClient(window, &cursor)) {
            CreateContextMenuFallback(self, l, t, w, h, z, screenCoord, data);
            return;
        }

        const int menuHeight = kContextMenuRowHeight * (buttonCount + 2);
        const int maxX = gActiveWidth > kContextMenuWidth
            ? gActiveWidth - kContextMenuWidth
            : 0;
        const int maxY = gActiveHeight > menuHeight
            ? gActiveHeight - menuHeight
            : 0;

        if (cursor.x < 0) cursor.x = 0;
        if (cursor.y < 0) cursor.y = 0;
        if (cursor.x > maxX) cursor.x = maxX;
        if (cursor.y > maxY) cursor.y = maxY;

        reinterpret_cast<CreateWndFn>(kCWndCreateWndAddress)(
            self,
            cursor.x,
            cursor.y,
            kContextMenuWidth,
            menuHeight,
            10,
            1,
            data,
            1);
    }
    __except (EXCEPTION_EXECUTE_HANDLER) {
        CrashDiagnostics::LogEvent("context menu bounds hook raised an exception");
        CreateContextMenuFallback(self, l, t, w, h, z, screenCoord, data);
    }
}

inline bool InstallContextMenuBounds() {
    __try {
        if (*reinterpret_cast<unsigned char*>(kContextMenuCreateCallSite) != 0xE8) {
            CrashDiagnostics::LogEvent("context menu bounds preflight mismatch");
            return false;
        }
    }
    __except (EXCEPTION_EXECUTE_HANDLER) {
        CrashDiagnostics::LogEvent("context menu bounds preflight unavailable");
        return false;
    }

    const intptr_t relative =
        reinterpret_cast<intptr_t>(&ContextMenuCreateHook) -
        static_cast<intptr_t>(kContextMenuCreateCallSite + 5);
    Memory::WriteInt(
        kContextMenuCreateCallSite + 1,
        static_cast<unsigned int>(static_cast<int32_t>(relative)));
    CrashDiagnostics::LogEvent("resolution-aware context menu bounds enabled");
    return true;
}

inline void __fastcall GetUIWndPosHook(
    void* self,
    void*,
    int uiType,
    int* x,
    int* y,
    int* op) {
    gGetUIWndPos(self, uiType, x, y, op);
    if (!x || !y || !IsOutside(*x, *y, gActiveWidth, gActiveHeight)) {
        return;
    }
    GetDefaultPosition(uiType, x, y);
}

inline void __fastcall LoadCharacterHook(
    void* self,
    void*,
    int worldId,
    unsigned int characterId) {
    gLoadCharacter(self, worldId, characterId);
    ClampConfigObject(self, gActiveWidth, gActiveHeight);
}

} // namespace detail

inline void SetActiveResolution(int width, int height) {
    if (width < 800 || height < 600) {
        return;
    }
    detail::gActiveWidth = width;
    detail::gActiveHeight = height;

    __try {
        void* config = *reinterpret_cast<void**>(detail::kConfigSingletonAddress);
        detail::ClampConfigObject(config, width, height);
    }
    __except (EXCEPTION_EXECUTE_HANDLER) {
        CrashDiagnostics::LogEvent("CConfig singleton unavailable for UI bounds clamp");
    }
}

inline bool Install(int width, int height) {
    SetActiveResolution(width, height);
    if (detail::gInstalled) {
        return true;
    }

    if (!Memory::SetHook(
            true,
            reinterpret_cast<void**>(&detail::gGetUIWndPos),
            reinterpret_cast<void*>(detail::GetUIWndPosHook))) {
        CrashDiagnostics::LogEvent("GetUIWndPos bounds hook install failed");
        return false;
    }

    if (!Memory::SetHook(
            true,
            reinterpret_cast<void**>(&detail::gLoadCharacter),
            reinterpret_cast<void*>(detail::LoadCharacterHook))) {
        Memory::SetHook(
            false,
            reinterpret_cast<void**>(&detail::gGetUIWndPos),
            reinterpret_cast<void*>(detail::GetUIWndPosHook));
        CrashDiagnostics::LogEvent("LoadCharacter UI bounds hook install failed");
        return false;
    }

    if (!detail::InstallContextMenuBounds()) {
        // Saved-position hardening is still useful on its own. Leave it active
        // and record the context-menu preflight failure for runtime diagnostics.
        CrashDiagnostics::LogEvent("context menu bounds unavailable; saved UI bounds kept enabled");
    }

    detail::gInstalled = true;
    CrashDiagnostics::LogEvent("Kaentake-style resolution UI bounds enabled");
    return true;
}

} // namespace ResolutionUIBounds
