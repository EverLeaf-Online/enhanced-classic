#pragma once

#include "Client.h"
#include "CrashDiagnostics.h"

#include <windows.h>
#include <oleauto.h>
#include <cstddef>

namespace RuntimeUiSync {
namespace detail {

constexpr DWORD kWndManInstanceAddress = 0x00BEC20C;
constexpr size_t kOrgWindowOffset = 0xDC;
constexpr DWORD kGr2DHolderAddress = 0x00BF14EC;
constexpr size_t kGr2DCenterVtableIndex = 23;
constexpr size_t kVectorPutOriginVtableIndex = 25;
constexpr size_t kVectorRelMoveVtableIndex = 36;
constexpr DWORD kInputSystemInstanceAddress = 0x00BEC33C;
constexpr DWORD kSetCursorVectorPosAddress = 0x0059A0CB;

struct IWzVector2DLite { void** vtable; };
using GetCenterFn = HRESULT(__stdcall*)(void*, IWzVector2DLite**);
using PutOriginFn = HRESULT(__stdcall*)(IWzVector2DLite*, VARIANT);
using RelMoveFn = HRESULT(__stdcall*)(IWzVector2DLite*, int, int, VARIANT, VARIANT);
using SetCursorVectorPosFn = void(__thiscall*)(void*, int, int);

inline IWzVector2DLite* GetGr2DCenter() {
    __try {
        void* gr = *reinterpret_cast<void**>(kGr2DHolderAddress);
        if (!gr) return nullptr;
        void** vtable = *reinterpret_cast<void***>(gr);
        if (!vtable || !vtable[kGr2DCenterVtableIndex]) return nullptr;
        IWzVector2DLite* center = nullptr;
        auto fn = reinterpret_cast<GetCenterFn>(vtable[kGr2DCenterVtableIndex]);
        if (FAILED(fn(gr, &center))) return nullptr;
        return center;
    } __except (EXCEPTION_EXECUTE_HANDLER) { return nullptr; }
}

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

inline bool ReapplyStockWindowOrigin() {
    __try {
        void* wndMan = *reinterpret_cast<void**>(kWndManInstanceAddress);
        if (!wndMan) return true;
        auto* bytes = reinterpret_cast<unsigned char*>(wndMan);
        auto* origin = *reinterpret_cast<IWzVector2DLite**>(bytes + kOrgWindowOffset);
        if (!origin) return false;
        IWzVector2DLite* center = GetGr2DCenter();
        if (!center) return false;

        // Match EverLeaf's known-good clean-launch coordinate model exactly.
        // Do not use Kaentake's extra vertical-center adjustment unless the
        // complete Gr2D-center/origin-routing subsystem is installed together.
        const HRESULT bindHr = PutOrigin(origin, center);
        const HRESULT moveHr = RelMove(origin,
            -(Client::m_nGameWidth / 2),
            -(Client::m_nGameHeight / 2));
        reinterpret_cast<IUnknown*>(center)->Release();
        if (FAILED(bindHr) || FAILED(moveHr)) return false;
        CrashDiagnostics::LogEvent("stock CWndMan origin resynced after live resolution");
        return true;
    } __except (EXCEPTION_EXECUTE_HANDLER) {
        CrashDiagnostics::LogEvent("stock CWndMan origin resync raised an exception");
        return false;
    }
}

inline void ResyncCursorVector() {
    __try {
        void* input = *reinterpret_cast<void**>(kInputSystemInstanceAddress);
        if (!input) return;
        HWND window = FindWindowA("MapleStoryClass", nullptr);
        if (!window) return;
        DWORD pid = 0;
        GetWindowThreadProcessId(window, &pid);
        if (pid != GetCurrentProcessId()) return;
        POINT pt = {};
        if (!GetCursorPos(&pt) || !ScreenToClient(window, &pt)) return;
        if (pt.x < 0) pt.x = 0;
        if (pt.y < 0) pt.y = 0;
        if (pt.x > Client::m_nGameWidth) pt.x = Client::m_nGameWidth;
        if (pt.y > Client::m_nGameHeight) pt.y = Client::m_nGameHeight;
        reinterpret_cast<SetCursorVectorPosFn>(kSetCursorVectorPosAddress)(input, pt.x, pt.y);
        CrashDiagnostics::LogEvent("cursor vector resynced after live resolution");
    } __except (EXCEPTION_EXECUTE_HANDLER) {
        CrashDiagnostics::LogEvent("cursor vector resync raised an exception");
    }
}

} // namespace detail

inline bool ApplyCurrent() {
    const bool ok = detail::ReapplyStockWindowOrigin();
    detail::ResyncCursorVector();
    return ok;
}

} // namespace RuntimeUiSync
