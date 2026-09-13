#pragma once

#include "Client.h"
#include "Memory.h"
#include "CrashDiagnostics.h"

#include <windows.h>
#include <oleauto.h>
#include <cstdint>
#include <cstddef>
#include <iostream>

// Owner-level widescreen corrections for CField_LimitedView::DrawViewRange.
// Kaentake fixes three canvas-copy call sites that EverLeaf's legacy HD block
// never adapted. This port keeps the exact pinned v83 call-site behavior but
// uses EverLeaf's current runtime resolution instead of compile-time max values.
namespace LimitedViewCorrections {
namespace detail {

constexpr DWORD kRawCopyCallSite = 0x0055BEFE;
constexpr DWORD kCopyExCallSite1 = 0x0055C08E;
constexpr DWORD kCopyExCallSite2 = 0x0055C1DD;

// Minimal IWzCanvas ABI through Copy/CopyEx, ordered from the authoritative
// iw2d/WzLib v83_DX8to9 IDL used by Kaentake. Placeholder pointer/int types are
// sufficient for methods we never call; the vtable order is what matters here.
struct IWzCanvasLite : IUnknown {
    virtual HRESULT __stdcall get_persistentUOL(BSTR*) = 0;
    virtual HRESULT __stdcall raw_Serialize(IUnknown*) = 0;
    virtual HRESULT __stdcall get_defaultDither(int*) = 0;
    virtual HRESULT __stdcall put_defaultDither(int) = 0;
    virtual HRESULT __stdcall get_defaultLevelMap(int*) = 0;
    virtual HRESULT __stdcall put_defaultLevelMap(int) = 0;
    virtual HRESULT __stdcall get_defaultAllocator(IUnknown**) = 0;
    virtual HRESULT __stdcall put_defaultAllocator(IUnknown*) = 0;
    virtual HRESULT __stdcall raw_Create(unsigned int, unsigned int, VARIANT, VARIANT) = 0;
    virtual HRESULT __stdcall raw_AddRawCanvas(int, int, IUnknown*) = 0;
    virtual HRESULT __stdcall get_rawCanvas(int, int, IUnknown**) = 0;
    virtual HRESULT __stdcall get_tileWidth(unsigned int*) = 0;
    virtual HRESULT __stdcall get_tileHeight(unsigned int*) = 0;
    virtual HRESULT __stdcall get_width(unsigned int*) = 0;
    virtual HRESULT __stdcall put_width(unsigned int) = 0;
    virtual HRESULT __stdcall get_height(unsigned int*) = 0;
    virtual HRESULT __stdcall put_height(unsigned int) = 0;
    virtual HRESULT __stdcall get_pixelFormat(int*) = 0;
    virtual HRESULT __stdcall put_pixelFormat(int) = 0;
    virtual HRESULT __stdcall get_magLevel(int*) = 0;
    virtual HRESULT __stdcall put_magLevel(int) = 0;
    virtual HRESULT __stdcall raw_GetSnapshotU(
        unsigned int*, unsigned int*, unsigned int*, unsigned int*, int*, int*) = 0;
    virtual HRESULT __stdcall raw_GetSnapshot(int*, int*, int*, int*, int*, int*) = 0;
    virtual HRESULT __stdcall get_property(IUnknown**) = 0;
    virtual HRESULT __stdcall get_cx(int*) = 0;
    virtual HRESULT __stdcall put_cx(int) = 0;
    virtual HRESULT __stdcall get_cy(int*) = 0;
    virtual HRESULT __stdcall put_cy(int) = 0;
    virtual HRESULT __stdcall raw_SetClipRect(int, int, int, int, VARIANT, VARIANT*) = 0;
    virtual HRESULT __stdcall raw_Copy(int, int, IWzCanvasLite*, VARIANT) = 0;
    virtual HRESULT __stdcall raw_CopyEx(
        int,
        int,
        IWzCanvasLite*,
        int,
        int,
        int,
        int,
        int,
        int,
        int,
        VARIANT) = 0;
};

static bool gInstalled = false;

inline int DestinationOffsetX() {
    return (Client::m_nGameWidth / 2) - 400;
}

inline int DestinationOffsetY() {
    return (Client::m_nGameHeight / 2) - 300 +
           ((Client::m_nGameHeight - 600) / 2);
}

inline HRESULT __stdcall RawCopyHook(
    IWzCanvasLite* canvas,
    int dstLeft,
    int dstTop,
    IWzCanvasLite* source,
    VARIANT alpha) {
    if (!canvas) {
        return E_POINTER;
    }

    dstLeft += DestinationOffsetX();
    dstTop += DestinationOffsetY();

    __try {
        return canvas->raw_Copy(dstLeft, dstTop, source, alpha);
    }
    __except (EXCEPTION_EXECUTE_HANDLER) {
        CrashDiagnostics::LogEvent("limited-view raw_Copy correction raised an exception");
        return E_FAIL;
    }
}

// The original v83 CopyEx helper is a thiscall-style wrapper; Kaentake replaces
// its CALL sites with a __fastcall bridge so ECX remains the IWzCanvas `this`.
inline HRESULT __fastcall CopyExHook(
    IWzCanvasLite* canvas,
    void*,
    int dstLeft,
    int dstTop,
    IWzCanvasLite* source,
    int alpha,
    int width,
    int height,
    int srcLeft,
    int srcTop,
    int srcWidth,
    int srcHeight,
    const VARIANT& adjust) {
    if (!canvas) {
        return E_POINTER;
    }

    dstLeft += DestinationOffsetX();
    dstTop += DestinationOffsetY();

    __try {
        return canvas->raw_CopyEx(
            dstLeft,
            dstTop,
            source,
            alpha,
            width,
            height,
            srcLeft,
            srcTop,
            srcWidth,
            srcHeight,
            adjust);
    }
    __except (EXCEPTION_EXECUTE_HANDLER) {
        CrashDiagnostics::LogEvent("limited-view CopyEx correction raised an exception");
        return E_FAIL;
    }
}

inline bool IsSixByteIndirectCall(DWORD address) {
    __try {
        const unsigned char opcode = *reinterpret_cast<unsigned char*>(address);
        const unsigned char modrm = *reinterpret_cast<unsigned char*>(address + 1);
        // x86 FF /2 is CALL r/m32. Kaentake replaces this six-byte COM call site
        // with E8 rel32 + NOP.
        return opcode == 0xFF && (modrm & 0x38) == 0x10;
    }
    __except (EXCEPTION_EXECUTE_HANDLER) {
        return false;
    }
}

inline bool IsRelativeCall(DWORD address) {
    __try {
        return *reinterpret_cast<unsigned char*>(address) == 0xE8;
    }
    __except (EXCEPTION_EXECUTE_HANDLER) {
        return false;
    }
}

inline void PatchDirectCall(DWORD address, void* destination, size_t size) {
    Memory::WriteByte(address, 0xE8);
    const intptr_t relative =
        reinterpret_cast<intptr_t>(destination) - static_cast<intptr_t>(address + 5);
    Memory::WriteInt(address + 1, static_cast<unsigned int>(static_cast<int32_t>(relative)));
    if (size > 5) {
        Memory::FillBytes(address + 5, 0x90, static_cast<int>(size - 5));
    }
}

} // namespace detail

inline bool Install() {
    if (detail::gInstalled) {
        return true;
    }

    if (!detail::IsSixByteIndirectCall(detail::kRawCopyCallSite) ||
        !detail::IsRelativeCall(detail::kCopyExCallSite1) ||
        !detail::IsRelativeCall(detail::kCopyExCallSite2)) {
        CrashDiagnostics::LogEvent("limited-view draw correction preflight mismatch");
        std::cout << "EverLeaf Client v2: limited-view draw correction preflight mismatch" << std::endl;
        return false;
    }

    detail::PatchDirectCall(
        detail::kRawCopyCallSite,
        reinterpret_cast<void*>(detail::RawCopyHook),
        6);
    detail::PatchDirectCall(
        detail::kCopyExCallSite1,
        reinterpret_cast<void*>(detail::CopyExHook),
        5);
    detail::PatchDirectCall(
        detail::kCopyExCallSite2,
        reinterpret_cast<void*>(detail::CopyExHook),
        5);

    detail::gInstalled = true;
    CrashDiagnostics::LogEvent("resolution-aware limited-view draw corrections enabled");
    std::cout << "EverLeaf Client v2: limited-view draw corrections enabled" << std::endl;
    return true;
}

} // namespace LimitedViewCorrections
