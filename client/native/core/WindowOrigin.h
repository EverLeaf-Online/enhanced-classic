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

// Authoritative v83_DX8to9 WzLib ordering:
// IWzGr2D::center = slot 23.
// IWzVector2D::origin propput = slot 25.
// IWzVector2D::RelMove = slot 36.
constexpr size_t kGr2DCenterVtableIndex = 23;
constexpr size_t kVectorPutOriginVtableIndex = 25;
constexpr size_t kVectorRelMoveVtableIndex = 36;

// IWzVector2D IID from iw2d/WzLib v83_DX8to9 IWzVector2D.idl.
static const GUID kIidWzVector2D = {
    0xF28BD1ED,
    0x3DEB,
    0x4F92,
    { 0x9E, 0xEC, 0x10, 0xEF, 0x5A, 0x1C, 0x3F, 0xB4 }
};

struct IWzVector2DLite {
    void** vtable;
};

using GetCenterFn = HRESULT(__stdcall*)(void*, IWzVector2DLite**);
using PutOriginFn = HRESULT(__stdcall*)(IWzVector2DLite*, VARIANT);
using RelMoveFn = HRESULT(__stdcall*)(IWzVector2DLite*, int, int, VARIANT, VARIANT);
using PcCreateObjectFn = HRESULT(__cdecl*)(const wchar_t*, const GUID*, void**, IUnknown*);
using WndManConstructorFn = void(__thiscall*)(void*, HWND);
using WndManDestructorFn = void(__thiscall*)(void*);

static WndManConstructorFn gWndManConstructor =
    reinterpret_cast<WndManConstructorFn>(kWndManConstructorAddress);
static WndManDestructorFn gWndManDestructor =
    reinterpret_cast<WndManDestructorFn>(kWndManDestructorAddress);
static IWzVector2DLite* gExtendedOrigins[kOriginCount] = {};
static IWzVector2DLite* gStatusBarOrigin = nullptr;
static IWzVector2DLite* gScreenMsgOrigin = nullptr;
static IWzVector2DLite* gQuickSlotOrigin = nullptr;
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

inline void ReleaseVector(IWzVector2DLite*& vector) {
    if (!vector) {
        return;
    }
    reinterpret_cast<IUnknown*>(vector)->Release();
    vector = nullptr;
}

inline void ReleaseExtendedOrigins() {
    // Special origins reference members of gExtendedOrigins. Release them first
    // so the extended origin reference counts can fall cleanly afterward.
    ReleaseVector(gStatusBarOrigin);
    ReleaseVector(gScreenMsgOrigin);
    ReleaseVector(gQuickSlotOrigin);
    for (int i = 0; i < kOriginCount; ++i) {
        ReleaseVector(gExtendedOrigins[i]);
    }
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
    if (!createObject) {
        return false;
    }

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

inline bool EnsureExtendedOrigins() {
    bool complete =
        gStatusBarOrigin && gScreenMsgOrigin && gQuickSlotOrigin;
    for (int i = 0; i < kOriginCount && complete; ++i) {
        complete = gExtendedOrigins[i] != nullptr;
    }
    if (complete) {
        return true;
    }

    ReleaseExtendedOrigins();
    for (int i = 0; i < kOriginCount; ++i) {
        if (!CreateVector(gExtendedOrigins[i])) {
            ReleaseExtendedOrigins();
            return false;
        }
    }
    if (!CreateVector(gStatusBarOrigin) ||
        !CreateVector(gScreenMsgOrigin) ||
        !CreateVector(gQuickSlotOrigin)) {
        ReleaseExtendedOrigins();
        return false;
    }

    CrashDiagnostics::LogEvent("extended CWndMan origin vectors created");
    return true;
}

inline bool ResetExtendedOrigins(IWzVector2DLite* center) {
    if (!center || !EnsureExtendedOrigins()) {
        return false;
    }

    bool ok = true;
    const int width = Client::m_nGameWidth;
    const int height = Client::m_nGameHeight;
    const int adjustY = VerticalCenterAdjustment();

    for (int i = 0; i < kOriginCount; ++i) {
        int x = -(width / 2);
        if (i % 3 == 1) {
            x += (width - 800) / 2;
        }
        else if (i % 3 == 2) {
            x += width - 800;
        }

        int y = -(height / 2) - adjustY;
        if (i / 3 == 1) {
            y += (height - 600) / 2;
        }
        else if (i / 3 == 2) {
            y += height - 600;
        }

        if (FAILED(PutOrigin(gExtendedOrigins[i], center)) ||
            FAILED(RelMove(gExtendedOrigins[i], x, y))) {
            ok = false;
        }
    }

    // EverLeaf keeps Kaentake's default non-centered status bar layout:
    // status bar + quickslot anchor to LB (6), screen messages anchor to RB (8).
    if (FAILED(PutOrigin(gStatusBarOrigin, gExtendedOrigins[6])) ||
        FAILED(PutOrigin(gScreenMsgOrigin, gExtendedOrigins[8])) ||
        FAILED(PutOrigin(gQuickSlotOrigin, gExtendedOrigins[6]))) {
        ok = false;
    }

    if (FAILED(RelMove(gStatusBarOrigin, 0, 0))) {
        ok = false;
    }
    if (width > 800) {
        if (FAILED(RelMove(gScreenMsgOrigin, 0, -10)) ||
            FAILED(RelMove(gQuickSlotOrigin, 152, 68))) {
            ok = false;
        }
    }
    else {
        if (FAILED(RelMove(gScreenMsgOrigin, 0, 0)) ||
            FAILED(RelMove(gQuickSlotOrigin, 0, 0))) {
            ok = false;
        }
    }

    return ok;
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

        IWzVector2DLite* center = GetGr2DCenter();
        if (!center) {
            return false;
        }

        bool ok = true;
        if (FAILED(PutOrigin(orgWindow, center))) {
            CrashDiagnostics::LogEvent("base window origin center bind failed; keeping stock origin");
            ok = false;
        }

        const int x = -(Client::m_nGameWidth / 2);
        const int y = -(Client::m_nGameHeight / 2) - VerticalCenterAdjustment();
        if (FAILED(RelMove(orgWindow, x, y))) {
            CrashDiagnostics::LogEvent("base window origin RelMove failed");
            ok = false;
        }

        if (!ResetExtendedOrigins(center)) {
            CrashDiagnostics::LogEvent("extended window origins unavailable; base origin kept active");
            ok = false;
        }

        reinterpret_cast<IUnknown*>(center)->Release();
        return ok;
    }
    __except (EXCEPTION_EXECUTE_HANDLER) {
        CrashDiagnostics::LogEvent("window origin update raised an exception");
        return false;
    }
}

inline void __fastcall WndManConstructorHook(void* self, void*, HWND window) {
    gWndManConstructor(self, window);
    if (!ApplyTo(self)) {
        CrashDiagnostics::LogEvent("window origins unavailable after CWndMan construction");
    }
}

inline void __fastcall WndManDestructorHook(void* self, void*) {
    gWndManDestructor(self);
    ReleaseExtendedOrigins();
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
        CrashDiagnostics::LogEvent("CWndMan singleton unavailable for origin update");
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

    if (!Memory::SetHook(
            true,
            reinterpret_cast<void**>(&detail::gWndManDestructor),
            reinterpret_cast<void*>(detail::WndManDestructorHook))) {
        Memory::SetHook(
            false,
            reinterpret_cast<void**>(&detail::gWndManConstructor),
            reinterpret_cast<void*>(detail::WndManConstructorHook));
        CrashDiagnostics::LogEvent("CWndMan destructor origin hook install failed");
        return false;
    }

    detail::gInstalled = true;
    // CWndMan may already exist by the time the client-v2 bootstrap runs.
    ApplyCurrent();
    CrashDiagnostics::LogEvent("extended CWndMan origin infrastructure enabled");
    std::cout << "EverLeaf Client v2: extended window origin infrastructure enabled" << std::endl;
    return true;
}

inline void Shutdown() {
    detail::ReleaseExtendedOrigins();
}

} // namespace WindowOrigin
