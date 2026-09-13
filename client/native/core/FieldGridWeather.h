#pragma once

#include "Client.h"
#include "Memory.h"
#include "CrashDiagnostics.h"

#include <windows.h>
#include <oleauto.h>
#include <cstdint>
#include <cstddef>
#include <iostream>

// Remaining owner-level CMapLoadable widescreen corrections from Kaentake's
// v83 resolution stack. EverLeaf keeps the fixes dynamic so live resolution
// changes do not depend on Kaentake's compile-time SCREEN_*_MAX constants.
namespace FieldGridWeather {
namespace detail {

constexpr DWORD kMakeGridPatchSite = 0x0063EAD6;
constexpr DWORD kMakeGridReturn = 0x0063EADC;
constexpr DWORD kWeatherWrapClipCallSite = 0x0064106B;

// IWzVector2D::WrapClip is vtable slot 39 when counted from IUnknown. The slot
// order comes from iw2d/WzLib's v83_DX8to9 IWzSerialize/IWzShape2D/
// IWzVector2D IDLs, which are the exact interfaces Kaentake vendors.
constexpr size_t kWrapClipVtableIndex = 39;

struct IWzVector2DLite {
    void** vtable;
};

using WrapClipFn = HRESULT(__stdcall*)(
    IWzVector2DLite*,
    VARIANT,
    int,
    int,
    unsigned int,
    unsigned int,
    VARIANT);

static volatile LONG gAdjustCenterY = 0;
static DWORD gMakeGridReturnAddress = kMakeGridReturn;
static bool gInstalled = false;

inline int CurrentAdjustCenterY() {
    return (Client::m_nGameHeight - 600) / 2;
}

inline void RefreshAdjustment() {
    InterlockedExchange(&gAdjustCenterY, static_cast<LONG>(CurrentAdjustCenterY()));
}

inline bool MatchesMakeGridPreflight() {
    static const unsigned char expected[] = {
        0xD1, 0xF9,       // sar ecx, 1
        0xF7, 0xD8,       // neg eax
        0x2B, 0xC1        // sub eax, ecx
    };

    __try {
        for (size_t i = 0; i < sizeof(expected); ++i) {
            if (*reinterpret_cast<unsigned char*>(kMakeGridPatchSite + i) != expected[i]) {
                return false;
            }
        }
        return true;
    }
    __except (EXCEPTION_EXECUTE_HANDLER) {
        return false;
    }
}

inline bool MatchesWeatherWrapClipPreflight() {
    __try {
        const unsigned char opcode =
            *reinterpret_cast<unsigned char*>(kWeatherWrapClipCallSite);
        const unsigned char modrm =
            *reinterpret_cast<unsigned char*>(kWeatherWrapClipCallSite + 1);
        // Kaentake replaces this six-byte x86 FF /2 COM CALL with E8 rel32 + NOP.
        return opcode == 0xFF && (modrm & 0x38) == 0x10;
    }
    __except (EXCEPTION_EXECUTE_HANDLER) {
        return false;
    }
}

inline void PatchDirectJump(DWORD address, void* destination, size_t size) {
    Memory::WriteByte(address, 0xE9);
    const intptr_t relative =
        reinterpret_cast<intptr_t>(destination) - static_cast<intptr_t>(address + 5);
    Memory::WriteInt(address + 1, static_cast<unsigned int>(static_cast<int32_t>(relative)));
    if (size > 5) {
        Memory::FillBytes(address + 5, 0x90, static_cast<int>(size - 5));
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

// Exact six bytes overwritten at 0x0063EAD6 are replayed before applying
// Kaentake's vertical-center correction and returning to 0x0063EADC.
__declspec(naked) inline void MakeGridHook() {
    __asm {
        sar ecx, 1
        neg eax
        sub eax, ecx
        sub eax, dword ptr [gAdjustCenterY]
        jmp dword ptr [gMakeGridReturnAddress]
    }
}

inline HRESULT __stdcall WeatherWrapClipHook(
    IWzVector2DLite* vector,
    VARIANT origin,
    int wrapLeft,
    int wrapTop,
    unsigned int wrapWidth,
    unsigned int wrapHeight,
    VARIANT clip) {
    if (!vector || !vector->vtable) {
        return E_POINTER;
    }

    const int width = Client::m_nGameWidth;
    const int height = Client::m_nGameHeight;

    wrapLeft += 400 - (width / 2);
    wrapTop += 300 - (height / 2) - ((height - 600) / 2);
    wrapWidth = static_cast<unsigned int>(
        static_cast<int>(wrapWidth) - 800 + width);
    wrapHeight = static_cast<unsigned int>(
        static_cast<int>(wrapHeight) - 600 + height);

    __try {
        auto original = reinterpret_cast<WrapClipFn>(
            vector->vtable[kWrapClipVtableIndex]);
        if (!original) {
            return E_POINTER;
        }
        return original(
            vector,
            origin,
            wrapLeft,
            wrapTop,
            wrapWidth,
            wrapHeight,
            clip);
    }
    __except (EXCEPTION_EXECUTE_HANDLER) {
        CrashDiagnostics::LogEvent("weather WrapClip correction raised an exception");
        return E_FAIL;
    }
}

} // namespace detail

inline void ApplyCurrent() {
    detail::RefreshAdjustment();
}

inline bool Install() {
    ApplyCurrent();

    if (detail::gInstalled) {
        return true;
    }

    // Treat the two owner-level fixes as one atomic compatibility unit: if the
    // pinned v83 bytes are not both what Kaentake mapped, leave both untouched.
    if (!detail::MatchesMakeGridPreflight() ||
        !detail::MatchesWeatherWrapClipPreflight()) {
        CrashDiagnostics::LogEvent("field grid/weather correction preflight mismatch");
        std::cout << "EverLeaf Client v2: field grid/weather correction preflight mismatch" << std::endl;
        return false;
    }

    detail::PatchDirectJump(
        detail::kMakeGridPatchSite,
        reinterpret_cast<void*>(detail::MakeGridHook),
        6);
    detail::PatchDirectCall(
        detail::kWeatherWrapClipCallSite,
        reinterpret_cast<void*>(detail::WeatherWrapClipHook),
        6);

    detail::gInstalled = true;
    CrashDiagnostics::LogEvent("resolution-aware field grid/weather corrections enabled");
    std::cout << "EverLeaf Client v2: field grid/weather corrections enabled" << std::endl;
    return true;
}

} // namespace FieldGridWeather
