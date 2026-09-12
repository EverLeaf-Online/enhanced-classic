#pragma once

#include "Client.h"
#include "Memory.h"
#include "CrashDiagnostics.h"

#include <windows.h>
#include <oleauto.h>
#include <cstddef>
#include <iostream>

// First slice of Kaentake's CWndMan origin architecture. This phase intentionally
// adjusts only the stock m_pOrgWindow that v83 already owns. Extended LT/CT/RT,
// status-bar, screen-message and quickslot vectors remain a later review phase.
namespace WindowOrigin {
namespace detail {

constexpr DWORD kWndManInstanceAddress = 0x00BEC20C;
constexpr DWORD kWndManConstructorAddress = 0x009E2C42;
constexpr size_t kOrgWindowOffset = 0xDC;
constexpr DWORD kGr2DHolderAddress = 0x00BF14EC;

// Authoritative v83_DX8to9 WzLib ordering:
// IWzGr2D::center = slot 23.
// IWzVector2D::origin propput = slot 25.
// IWzVector2D::RelMove = slot 36.
constexpr size_t kGr2DCenterVtableIndex = 23;
constexpr size_t kVectorPutOriginVtableIndex = 25;
constexpr size_t kVectorRelMoveVtableIndex = 36;

struct IWzVector2DLite {
    void** vtable;
};

using GetCenterFn = HRESULT(__stdcall*)(void*, IWzVector2DLite**);
using PutOriginFn = HRESULT(__stdcall*)(IWzVector2DLite*, VARIANT);
using RelMoveFn = HRESULT(__stdcall*)(IWzVector2DLite*, int, int, VARIANT, VARIANT);
using WndManConstructorFn = void(__thiscall*)(void*, HWND);

static WndManConstructorFn gWndManConstructor =
    reinterpret_cast<WndManConstructorFn>(kWndManConstructorAddress);
static bool gInstalled = false;

inline int VerticalCenterAdjustment() {
    return (Client::m_nGameHeight - 600) / 2;
}

inline IWzVector2DLite* GetGr2DCenter() {
    __try {
        void* gr = *reinterpret_cast<void**>(kGr2DHolderAddress);
        if (!gr) {
            return nullptr;
        }

        void** vtable = *reinterpret_cast<void***>(gr);
        if (!vtable || !vtable[kGr2DCenterVtableIndex]) {
            return nullptr;
        }

        IWzVector2DLite* center = nullptr;
        auto getCenter = reinterpret_cast<GetCenterFn>(vtable[kGr2DCenterVtableIndex]);
        if (FAILED(getCenter(gr, &center))) {
            return nullptr;
        }
        return center;
    }
    __except (EXCEPTION_EXECUTE_HANDLER) {
        return nullptr;
    }
}

inline HRESULT PutOrigin(IWzVector2DLite* vector, IWzVector2DLite* origin) {
    if (!vector || !vector->vtable || !origin) {
        return E_POINTER;
    }

    auto putOrigin = reinterpret_cast<PutOriginFn>(
        vector->vtable[kVectorPutOriginVtableIndex]);
    if (!putOrigin) {
        return E_POINTER;
    }

    VARIANT value = {};
    value.vt = VT_UNKNOWN;
    value.punkVal = reinterpret_cast<IUnknown*>(origin);
    return putOrigin(vector, value);
}

inline HRESULT RelMove(IWzVector2DLite* vector, int x, int y) {
    if (!vector || !vector->vtable) {
        return E_POINTER;
    }

    auto relMove = reinterpret_cast<RelMoveFn>(
        vector->vtable[kVectorRelMoveVtableIndex]);
    if (!relMove) {
        return E_POINTER;
    }

    VARIANT missing = {};
    missing.vt = VT_ERROR;
    missing.scode = DISP_E_PARAMNOTFOUND;
    return relMove(vector, x, y, missing, missing);
}

inline bool ApplyTo(void* wndMan) {
    if (!wndMan || Client::m_nGameWidth < 800 || Client::m_nGameHeight < 600) {
        return false;
    }

    __try {
        auto bytes = reinterpret_cast<unsigned char*>(wndMan);
        auto orgWindow = *reinterpret_cast<IWzVector2DLite**>(
            bytes + kOrgWindowOffset);
        if (!orgWindow) {
            return false;
        }

        // Match Kaentake's ResetOrgWindow base behavior. Rebind to Gr2D center
        // when available, but keep the stock origin relationship as a fallback.
        IWzVector2DLite* center = GetGr2DCenter();
        if (center) {
            const HRESULT originHr = PutOrigin(orgWindow, center);
            reinterpret_cast<IUnknown*>(center)->Release();
            if (FAILED(originHr)) {
                CrashDiagnostics::LogEvent("base window origin center bind failed; keeping stock origin");
            }
        }

        const int x = -(Client::m_nGameWidth / 2);
        const int y = -(Client::m_nGameHeight / 2) - VerticalCenterAdjustment();
        const HRESULT moveHr = RelMove(orgWindow, x, y);
        if (FAILED(moveHr)) {
            CrashDiagnostics::LogEvent("base window origin RelMove failed");
            return false;
        }
        return true;
    }
    __except (EXCEPTION_EXECUTE_HANDLER) {
        CrashDiagnostics::LogEvent("base window origin update raised an exception");
        return false;
    }
}

inline void __fastcall WndManConstructorHook(void* self, void*, HWND window) {
    gWndManConstructor(self, window);
    if (!ApplyTo(self)) {
        CrashDiagnostics::LogEvent("base window origin unavailable after CWndMan construction");
    }
}

} // namespace detail

inline bool ApplyCurrent() {
    __try {
        void* wndMan = *reinterpret_cast<void**>(detail::kWndManInstanceAddress);
        if (!wndMan) {
            return false;
        }
        return detail::ApplyTo(wndMan);
    }
    __except (EXCEPTION_EXECUTE_HANDLER) {
        CrashDiagnostics::LogEvent("CWndMan singleton unavailable for base origin update");
        return false;
    }
}

inline bool Install() {
    if (detail::gInstalled) {
        ApplyCurrent();
        return true;
    }

    if (!Memory::SetHook(
            true,
            reinterpret_cast<void**>(&detail::gWndManConstructor),
            reinterpret_cast<void*>(detail::WndManConstructorHook))) {
        CrashDiagnostics::LogEvent("CWndMan constructor origin hook install failed");
        return false;
    }

    detail::gInstalled = true;
    // CWndMan may already exist by the time the client-v2 bootstrap runs. If it
    // does not, the constructor hook will apply the origin when it is created.
    ApplyCurrent();
    CrashDiagnostics::LogEvent("dynamic base CWndMan origin enabled");
    std::cout << "EverLeaf Client v2: base window origin enabled" << std::endl;
    return true;
}

} // namespace WindowOrigin
