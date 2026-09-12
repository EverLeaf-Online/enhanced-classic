#pragma once

#include "Client.h"
#include "Memory.h"
#include "CrashDiagnostics.h"

#include <windows.h>
#include <oleauto.h>
#include <iostream>

// Guarded Kaentake-style replacement for CMapLoadable::RestoreViewRange on the
// pinned GMS v83 client. The old EverLeaf HD path only patches three immediates
// inside the stock routine (and intentionally leaves VRRight disabled because
// that operand patch was known to crash). This hook computes all four sides from
// the field's actual VR properties, with the same physical-space defaults used by
// Kaentake, and falls back to the original routine whenever object/COM state is
// unavailable.
namespace FieldViewRange {
namespace detail {

constexpr DWORD kRestoreViewRangeAddress = 0x00641EF1;
constexpr DWORD kPhysicalSpaceSingletonAddress = 0x00BEBFA0;
constexpr size_t kPhysicalSpaceMbrOffset = 0x24;
constexpr size_t kFieldInfoPropertyOffset = 0x2C;
constexpr size_t kViewRangeOffset = 0xF0;

// Minimal WZ COM surface required here. This ABI is shared by the v83-derived
// EverLeaf lineage and avoids importing Kaentake's entire generated WzLib/ZTL
// wrapper stack just to read four integer field properties.
struct IWzPropertyLite : IUnknown {
    virtual HRESULT __stdcall get_persistentUOL(wchar_t**) = 0;
    virtual HRESULT __stdcall raw_Serialize(void*) = 0;
    virtual HRESULT __stdcall get_item(const wchar_t*, VARIANT*) = 0;
    virtual HRESULT __stdcall put_item(const wchar_t*, VARIANT) = 0;
    virtual HRESULT __stdcall get__NewEnum(IUnknown**) = 0;
    virtual HRESULT __stdcall get_count(unsigned int*) = 0;
};

using RestoreViewRangeFn = void(__thiscall*)(void*);
static RestoreViewRangeFn gRestoreViewRange =
    reinterpret_cast<RestoreViewRangeFn>(kRestoreViewRangeAddress);
static bool gInstalled = false;

inline int VerticalCenterAdjustment() {
    return (Client::m_nGameHeight - 600) / 2;
}

inline bool ReadPropertyInt(
    IWzPropertyLite* property,
    const wchar_t* key,
    int defaultValue,
    int& result) {
    if (!property || !key) {
        result = defaultValue;
        return false;
    }

    VARIANT value;
    VARIANT converted;
    VariantInit(&value);
    VariantInit(&converted);

    const HRESULT getHr = property->get_item(key, &value);
    if (FAILED(getHr) || value.vt == VT_EMPTY || value.vt == VT_ERROR) {
        VariantClear(&value);
        result = defaultValue;
        return false;
    }

    const HRESULT convertHr = VariantChangeType(&converted, &value, 0, VT_I4);
    VariantClear(&value);
    if (FAILED(convertHr)) {
        VariantClear(&converted);
        result = defaultValue;
        return false;
    }

    result = V_I4(&converted);
    VariantClear(&converted);
    return true;
}

inline void NormalizeCollapsedRange(RECT& range) {
    if (range.right - range.left <= 0) {
        const LONG middle = (range.left + range.right) / 2;
        range.left = middle;
        range.right = middle;
    }
    if (range.bottom - range.top <= 0) {
        const LONG middle = (range.top + range.bottom) / 2;
        range.top = middle;
        range.bottom = middle;
    }
}

inline bool TryRestoreViewRange(void* self) {
    if (!self || Client::m_nGameWidth < 800 || Client::m_nGameHeight < 600) {
        return false;
    }

    __try {
        void* physicalSpace =
            *reinterpret_cast<void**>(kPhysicalSpaceSingletonAddress);
        if (!physicalSpace) {
            return false;
        }

        auto fieldBytes = reinterpret_cast<unsigned char*>(self);
        IWzPropertyLite* fieldInfo =
            *reinterpret_cast<IWzPropertyLite**>(fieldBytes + kFieldInfoPropertyOffset);
        if (!fieldInfo) {
            return false;
        }

        const RECT physicalMbr = *reinterpret_cast<RECT*>(
            reinterpret_cast<unsigned char*>(physicalSpace) + kPhysicalSpaceMbrOffset);
        auto viewRange = reinterpret_cast<RECT*>(fieldBytes + kViewRangeOffset);

        int vrLeft = physicalMbr.left - 20;
        int vrTop = physicalMbr.top - 60;
        int vrRight = physicalMbr.right + 20;
        int vrBottom = physicalMbr.bottom + 190;

        // Missing/non-integer WZ values intentionally use the same physical-space
        // defaults as Kaentake instead of making the whole hook fail.
        ReadPropertyInt(fieldInfo, L"VRLeft", vrLeft, vrLeft);
        ReadPropertyInt(fieldInfo, L"VRTop", vrTop, vrTop);
        ReadPropertyInt(fieldInfo, L"VRRight", vrRight, vrRight);
        ReadPropertyInt(fieldInfo, L"VRBottom", vrBottom, vrBottom);

        RECT next = {};
        next.left = vrLeft + Client::m_nGameWidth / 2;
        next.top = vrTop + Client::m_nGameHeight / 2;
        next.right = vrRight - Client::m_nGameWidth / 2;
        next.bottom = vrBottom - Client::m_nGameHeight / 2;
        NormalizeCollapsedRange(next);

        const int adjustY = VerticalCenterAdjustment();
        next.top += adjustY;
        next.bottom += adjustY;
        *viewRange = next;
        return true;
    }
    __except (EXCEPTION_EXECUTE_HANDLER) {
        CrashDiagnostics::LogEvent("Kaentake-style view range calculation raised an exception");
        return false;
    }
}

inline void __fastcall RestoreViewRangeHook(void* self, void*) {
    if (TryRestoreViewRange(self)) {
        return;
    }

    // The original pointer is converted by Detours into the trampoline when the
    // hook attaches, so this remains a safe compatibility fallback rather than a
    // recursion back into RestoreViewRangeHook.
    gRestoreViewRange(self);
}

} // namespace detail

inline bool Install() {
    if (detail::gInstalled) {
        return true;
    }

    if (!Memory::SetHook(
            true,
            reinterpret_cast<void**>(&detail::gRestoreViewRange),
            reinterpret_cast<void*>(detail::RestoreViewRangeHook))) {
        CrashDiagnostics::LogEvent("view range hook install failed");
        return false;
    }

    detail::gInstalled = true;
    CrashDiagnostics::LogEvent("Kaentake-style dynamic field view range enabled");
    std::cout << "EverLeaf Client v2: dynamic field view range enabled" << std::endl;
    return true;
}

} // namespace FieldViewRange
