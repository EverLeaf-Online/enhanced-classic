#pragma once

#include "Client.h"
#include "Memory.h"
#include "CrashDiagnostics.h"

#include <windows.h>
#include <oleauto.h>
#include <intrin.h>
#include <cstddef>
#include <cstdint>

// Runtime HUD anchoring for the live-resolution path.
//
// The phase-8/PR-414 path already keeps the stock CWndMan origin and cursor
// coordinate space synchronized. This module deliberately leaves that proven
// base origin alone and creates only the specialized child origins that v83
// needs for bottom/right anchored HUD surfaces. Moving the child origins after
// a resolution change reflows already-created UI layers without scaling their
// WZ artwork or changing mouse coordinates.
namespace RuntimeHudAnchors {
namespace detail {

constexpr DWORD kWndManInstanceAddress = 0x00BEC20C;
constexpr size_t kOrgWindowOffset = 0xDC;
constexpr DWORD kPcomApiTableAddress = 0x00BF0CC0;
constexpr DWORD kGetOrgWindowAddress = 0x0048BBA5;
constexpr DWORD kCreateWndAddress = 0x009DE4D2;
constexpr DWORD kGetShortcutIndexAddress = 0x008DE8D5;
constexpr size_t kWndLayerOffset = 0x18;
constexpr size_t kVectorPutOriginVtableIndex = 25;
constexpr size_t kVectorRelMoveVtableIndex = 36;

static const GUID kIidWzVector2D = {
    0xF28BD1ED,
    0x3DEB,
    0x4F92,
    { 0x9E, 0xEC, 0x10, 0xEF, 0x5A, 0x1C, 0x3F, 0xB4 }
};

struct IWzVector2DLite { void** vtable; };
using PutOriginFn = HRESULT(__stdcall*)(IWzVector2DLite*, VARIANT);
using RelMoveFn = HRESULT(__stdcall*)(IWzVector2DLite*, int, int, VARIANT, VARIANT);
using PcCreateObjectFn = HRESULT(__cdecl*)(const wchar_t*, const GUID*, void**, IUnknown*);
using GetOrgWindowFn = void*(__thiscall*)(void*, void*);
using CreateWndFn = void(__thiscall*)(void*, int, int, int, int, int, int, void*, int);
using GetShortcutIndexFn = int(__thiscall*)(void*, int, int);

static GetOrgWindowFn gGetOrgWindow = reinterpret_cast<GetOrgWindowFn>(kGetOrgWindowAddress);
static CreateWndFn gCreateWnd = reinterpret_cast<CreateWndFn>(kCreateWndAddress);
static GetShortcutIndexFn gGetShortcutIndex = reinterpret_cast<GetShortcutIndexFn>(kGetShortcutIndexAddress);
static IWzVector2DLite* gStatusBarOrigin = nullptr;
static IWzVector2DLite* gScreenMsgOrigin = nullptr;
static IWzVector2DLite* gQuickSlotOrigin = nullptr;
static bool gInstalled = false;

inline HRESULT PutOrigin(IWzVector2DLite* vector, IWzVector2DLite* origin) {
    if (!vector || !vector->vtable || !origin) return E_POINTER;
    auto fn = reinterpret_cast<PutOriginFn>(vector->vtable[kVectorPutOriginVtableIndex]);
    if (!fn) return E_POINTER;
    VARIANT value = {};
    value.vt = VT_UNKNOWN;
    value.punkVal = reinterpret_cast<IUnknown*>(origin);
    return fn(vector, value);
}

inline HRESULT RelMove(IWzVector2DLite* vector, int x, int y) {
    if (!vector || !vector->vtable) return E_POINTER;
    auto fn = reinterpret_cast<RelMoveFn>(vector->vtable[kVectorRelMoveVtableIndex]);
    if (!fn) return E_POINTER;
    VARIANT missing = {};
    missing.vt = VT_ERROR;
    missing.scode = DISP_E_PARAMNOTFOUND;
    return fn(vector, x, y, missing, missing);
}

inline void ReleaseVector(IWzVector2DLite*& vector) {
    if (!vector) return;
    reinterpret_cast<IUnknown*>(vector)->Release();
    vector = nullptr;
}

inline void ReleaseOrigins() {
    ReleaseVector(gQuickSlotOrigin);
    ReleaseVector(gScreenMsgOrigin);
    ReleaseVector(gStatusBarOrigin);
}

inline PcCreateObjectFn GetPcCreateObject() {
    __try {
        void* entry = *reinterpret_cast<void**>(kPcomApiTableAddress);
        return reinterpret_cast<PcCreateObjectFn>(entry);
    }
    __except (EXCEPTION_EXECUTE_HANDLER) {
        return nullptr;
    }
}

inline bool CreateVector(IWzVector2DLite*& vector) {
    vector = nullptr;
    auto createObject = GetPcCreateObject();
    if (!createObject) return false;
    __try {
        return SUCCEEDED(createObject(
            L"Shape2D#Vector2D",
            &kIidWzVector2D,
            reinterpret_cast<void**>(&vector),
            nullptr)) && vector != nullptr;
    }
    __except (EXCEPTION_EXECUTE_HANDLER) {
        vector = nullptr;
        return false;
    }
}

inline bool EnsureOrigins() {
    if (gStatusBarOrigin && gScreenMsgOrigin && gQuickSlotOrigin) return true;
    ReleaseOrigins();
    if (!CreateVector(gStatusBarOrigin) ||
        !CreateVector(gScreenMsgOrigin) ||
        !CreateVector(gQuickSlotOrigin)) {
        ReleaseOrigins();
        return false;
    }
    CrashDiagnostics::LogEvent("runtime HUD anchor vectors created");
    return true;
}

inline IWzVector2DLite* GetStockOrigin(void* wndMan) {
    if (!wndMan) return nullptr;
    return *reinterpret_cast<IWzVector2DLite**>(
        reinterpret_cast<unsigned char*>(wndMan) + kOrgWindowOffset);
}

inline bool Reflow(void* wndMan) {
    if (!wndMan || !EnsureOrigins()) return false;
    IWzVector2DLite* base = GetStockOrigin(wndMan);
    if (!base) return false;

    const int extraX = (Client::m_nGameWidth > 800) ? Client::m_nGameWidth - 800 : 0;
    const int extraY = (Client::m_nGameHeight > 600) ? Client::m_nGameHeight - 600 : 0;

    bool ok = true;
    // Bottom-left: status bar/chat follows the bottom edge while keeping stock
    // 800x600 pixel sizing. No texture scaling is performed.
    if (FAILED(PutOrigin(gStatusBarOrigin, base)) ||
        FAILED(RelMove(gStatusBarOrigin, 0, extraY))) {
        ok = false;
    }

    // Bottom-right: screen messages remain on the visible screen edge.
    if (FAILED(PutOrigin(gScreenMsgOrigin, base)) ||
        FAILED(RelMove(gScreenMsgOrigin, extraX, extraY + (Client::m_nGameWidth > 800 ? -10 : 0)))) {
        ok = false;
    }

    // Quickslot is attached to the status-bar anchor with Kaentake's v83 wide
    // offset so its visual and hit-test coordinate systems stay together.
    if (FAILED(PutOrigin(gQuickSlotOrigin, base)) ||
        FAILED(RelMove(gQuickSlotOrigin,
            Client::m_nGameWidth > 800 ? 152 : 0,
            extraY + (Client::m_nGameWidth > 800 ? 68 : 0)))) {
        ok = false;
    }

    if (ok) {
        CrashDiagnostics::LogEvent("runtime HUD anchors reflowed");
    }
    return ok;
}

inline void* ReturnOrigin(void* result, IWzVector2DLite* origin) {
    if (!result || !origin) return result;
    *reinterpret_cast<IWzVector2DLite**>(result) = origin;
    reinterpret_cast<IUnknown*>(origin)->AddRef();
    return result;
}

inline void* __fastcall GetOrgWindowHook(void* self, void*, void* result) {
    const uintptr_t caller = reinterpret_cast<uintptr_t>(_ReturnAddress());
    if (!EnsureOrigins()) {
        return gGetOrgWindow(self, result);
    }

    // Order matters: quickslot's caller is inside the broader status-bar range.
    if (caller == 0x008D15EE) { // CUIStatusBar::OnCreate - CQuickSlot
        return ReturnOrigin(result, gQuickSlotOrigin);
    }
    if (caller == 0x0089AF82) { // CUIScreenMsg::CUIScreenMsg
        return ReturnOrigin(result, gScreenMsgOrigin);
    }
    if (caller == 0x008DEB75 || caller == 0x008DEE11 ||
        (caller >= 0x008D01B2 && caller <= 0x008D3ADF)) {
        return ReturnOrigin(result, gStatusBarOrigin);
    }
    return gGetOrgWindow(self, result);
}

inline void __fastcall CreateWndHook(
    void* self,
    void*,
    int l,
    int t,
    int w,
    int h,
    int z,
    int bScreenCoord,
    void* pData,
    int bSetFocus) {
    const uintptr_t caller = reinterpret_cast<uintptr_t>(_ReturnAddress());
    gCreateWnd(self, l, t, w, h, z, bScreenCoord, pData, bSetFocus);
    if (!bScreenCoord || !EnsureOrigins()) return;

    // Main CUIStatusBar and CFadeWnd layers need the same bottom-left anchor as
    // their internal layers returned through CWndMan::GetOrgWindow.
    if (caller == 0x008CFD65 || caller == 0x0051FA03) {
        __try {
            auto* layer = *reinterpret_cast<IWzVector2DLite**>(
                reinterpret_cast<unsigned char*>(self) + kWndLayerOffset);
            if (layer) PutOrigin(layer, gStatusBarOrigin);
        }
        __except (EXCEPTION_EXECUTE_HANDLER) {
            CrashDiagnostics::LogEvent("status bar layer anchor assignment raised an exception");
        }
    }
}

inline int __fastcall GetShortcutIndexHook(void* self, void*, int x, int y) {
    // CQuickSlot is visually offset from the status-bar origin in wide modes.
    // Feed the original v83 hit-test coordinates in that same local space.
    if (Client::m_nGameWidth > 800) {
        x -= 152;
        y -= 68;
    }
    return gGetShortcutIndex(self, x, y);
}

} // namespace detail

inline bool ApplyCurrent() {
    __try {
        void* wndMan = *reinterpret_cast<void**>(detail::kWndManInstanceAddress);
        if (!wndMan) return true;
        return detail::Reflow(wndMan);
    }
    __except (EXCEPTION_EXECUTE_HANDLER) {
        CrashDiagnostics::LogEvent("runtime HUD anchor reflow raised an exception");
        return false;
    }
}

inline bool Install() {
    if (detail::gInstalled) return ApplyCurrent();

    if (!Memory::SetHook(true,
            reinterpret_cast<void**>(&detail::gGetOrgWindow),
            reinterpret_cast<void*>(detail::GetOrgWindowHook))) {
        CrashDiagnostics::LogEvent("runtime HUD GetOrgWindow hook install failed");
        return false;
    }
    if (!Memory::SetHook(true,
            reinterpret_cast<void**>(&detail::gCreateWnd),
            reinterpret_cast<void*>(detail::CreateWndHook))) {
        Memory::SetHook(false,
            reinterpret_cast<void**>(&detail::gGetOrgWindow),
            reinterpret_cast<void*>(detail::GetOrgWindowHook));
        CrashDiagnostics::LogEvent("runtime HUD CreateWnd hook install failed");
        return false;
    }
    if (!Memory::SetHook(true,
            reinterpret_cast<void**>(&detail::gGetShortcutIndex),
            reinterpret_cast<void*>(detail::GetShortcutIndexHook))) {
        Memory::SetHook(false,
            reinterpret_cast<void**>(&detail::gCreateWnd),
            reinterpret_cast<void*>(detail::CreateWndHook));
        Memory::SetHook(false,
            reinterpret_cast<void**>(&detail::gGetOrgWindow),
            reinterpret_cast<void*>(detail::GetOrgWindowHook));
        CrashDiagnostics::LogEvent("runtime HUD shortcut hit-test hook install failed");
        return false;
    }

    detail::gInstalled = true;
    ApplyCurrent();
    CrashDiagnostics::LogEvent("runtime HUD anchor routing enabled");
    return true;
}

inline void Shutdown() {
    detail::ReleaseOrigins();
}

} // namespace RuntimeHudAnchors
