#pragma once

#include "Client.h"
#include "Memory.h"
#include "CrashDiagnostics.h"

#include <windows.h>
#include <oleauto.h>
#include <cstddef>
#include <iostream>

// Owner-level CUIToolTip::MakeLayer correction selectively ported from Kaentake.
// EverLeaf already patches tooltip width/height limit constants; this hook clamps
// the actual finished tooltip layer inside the active runtime resolution.
namespace TooltipBounds {
namespace detail {

constexpr DWORD kMakeLayerAddress = 0x008F3141;
constexpr size_t kTooltipHeightOffset = 0x08;
constexpr size_t kTooltipWidthOffset = 0x0C;
constexpr size_t kTooltipLayerOffset = 0x10;

// IWzGr2DLayer inherits IWzVector2D in iw2d/WzLib v83_DX8to9. RelMove is slot 36
// from IUnknown across IWzSerialize + IWzShape2D + IWzVector2D.
constexpr size_t kRelMoveVtableIndex = 36;

struct IWzVector2DLite {
    void** vtable;
};

using RelMoveFn = HRESULT(__stdcall*)(
    IWzVector2DLite*,
    int,
    int,
    VARIANT,
    VARIANT);

using MakeLayerFn = void* (__thiscall*)(
    void*,
    void*,
    int,
    int,
    int,
    int,
    int,
    unsigned int);

static MakeLayerFn gMakeLayer = reinterpret_cast<MakeLayerFn>(kMakeLayerAddress);
static bool gInstalled = false;

inline int ClampInt(int value, int low, int high) {
    if (high < low) return low;
    if (value < low) return low;
    if (value > high) return high;
    return value;
}

inline HRESULT RelMove(IWzVector2DLite* vector, int x, int y) {
    if (!vector || !vector->vtable) {
        return E_POINTER;
    }

    auto original = reinterpret_cast<RelMoveFn>(vector->vtable[kRelMoveVtableIndex]);
    if (!original) {
        return E_POINTER;
    }

    VARIANT missing = {};
    missing.vt = VT_ERROR;
    missing.scode = DISP_E_PARAMNOTFOUND;
    return original(vector, x, y, missing, missing);
}

inline void ClampFinishedLayer(void* self, int requestedLeft, int requestedTop) {
    if (!self || Client::m_nGameWidth < 800 || Client::m_nGameHeight < 600) {
        return;
    }

    __try {
        auto bytes = reinterpret_cast<unsigned char*>(self);
        const int tooltipHeight = *reinterpret_cast<int*>(bytes + kTooltipHeightOffset);
        const int tooltipWidth = *reinterpret_cast<int*>(bytes + kTooltipWidthOffset);
        auto layer = *reinterpret_cast<IWzVector2DLite**>(bytes + kTooltipLayerOffset);

        if (!layer || tooltipWidth <= 0 || tooltipHeight <= 0 ||
            tooltipWidth > 8192 || tooltipHeight > 8192) {
            return;
        }

        const int maxX = Client::m_nGameWidth > tooltipWidth + 1
            ? Client::m_nGameWidth - 1 - tooltipWidth
            : 0;
        const int maxY = Client::m_nGameHeight > tooltipHeight + 1
            ? Client::m_nGameHeight - 1 - tooltipHeight
            : 0;

        const int left = ClampInt(requestedLeft, 0, maxX);
        const int top = ClampInt(requestedTop, 0, maxY);
        const HRESULT hr = RelMove(layer, left, top);
        if (FAILED(hr)) {
            CrashDiagnostics::LogEvent("tooltip layer RelMove failed");
        }
    }
    __except (EXCEPTION_EXECUTE_HANDLER) {
        CrashDiagnostics::LogEvent("tooltip bounds clamp raised an exception");
    }
}

inline void* __fastcall MakeLayerHook(
    void* self,
    void*,
    void* result,
    int left,
    int top,
    int doubleOutline,
    int login,
    int charToolTip,
    unsigned int color) {
    void* returned = gMakeLayer(
        self,
        result,
        left,
        top,
        doubleOutline,
        login,
        charToolTip,
        color);

    // Preserve Kaentake behavior: character tooltip placement has its own owner
    // and should not be moved by this generic post-layout clamp.
    if (!charToolTip) {
        ClampFinishedLayer(self, left, top);
    }
    return returned;
}

} // namespace detail

inline bool Install() {
    if (detail::gInstalled) {
        return true;
    }

    if (!Memory::SetHook(
            true,
            reinterpret_cast<void**>(&detail::gMakeLayer),
            reinterpret_cast<void*>(detail::MakeLayerHook))) {
        CrashDiagnostics::LogEvent("tooltip bounds hook install failed");
        return false;
    }

    detail::gInstalled = true;
    CrashDiagnostics::LogEvent("resolution-aware tooltip bounds enabled");
    std::cout << "EverLeaf Client v2: tooltip bounds enabled" << std::endl;
    return true;
}

} // namespace TooltipBounds
