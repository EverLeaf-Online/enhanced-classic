#pragma once

#include "Memory.h"
#include "CrashDiagnostics.h"

#include <windows.h>
#include <cstdio>

// Kaentake-style saved UI window bounds for the pinned GMS v83 CConfig layout.
// This prevents windows that were saved on a larger resolution from remaining
// unreachable after a live switch to a smaller EverLeaf resolution.
namespace ResolutionUIBounds {
namespace detail {

constexpr DWORD kConfigSingletonAddress = 0x00BEBF9C;
constexpr DWORD kGetUIWndPosAddress = 0x0049F0B5;
constexpr DWORD kLoadCharacterAddress = 0x0049D0B6;
constexpr size_t kUIWndXOffset = 0xCC;
constexpr size_t kUIWndYOffset = 0x154;
constexpr int kUIWindowCount = 34;

using GetUIWndPosFn = void(__thiscall*)(void*, int, int*, int*, int*);
using LoadCharacterFn = void(__thiscall*)(void*, int, unsigned int);

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

    detail::gInstalled = true;
    CrashDiagnostics::LogEvent("Kaentake-style saved UI bounds enabled");
    return true;
}

} // namespace ResolutionUIBounds
