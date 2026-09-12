#pragma once

#include "Memory.h"
#include "CrashDiagnostics.h"

#include <windows.h>
#include <oleauto.h>
#include <cstddef>
#include <cstdint>
#include <iostream>

// Phase 13 of the Kaentake resource-manager backport. Once a custom package has
// been mounted privately and indexed, merge direct non-property children from a
// matching custom property after the stock CWzProperty serializer succeeds.
// Nested properties are intentionally left to their own serialization pass,
// matching Kaentake's v83 behavior.
namespace CustomWzPropertyMerge {
namespace detail {

constexpr size_t kArchiveAbsoluteUolIndex = 6;
constexpr size_t kNameSpaceItemIndex = 3;
constexpr size_t kPropertyItemIndex = 5;
constexpr size_t kPropertyNewEnumIndex = 7;
constexpr size_t kPropertyAddIndex = 9;

static const GUID kIidProperty = {
    0x986515D9, 0x0A0B, 0x4929,
    { 0x8B, 0x4F, 0x71, 0x86, 0x82, 0x17, 0x7B, 0x92 }
};

struct ComObjectLite {
    void** vtable;
};

using PropertySerializeFn = HRESULT(__stdcall*)(void*, ComObjectLite*);
using GetAbsoluteUolFn = HRESULT(__stdcall*)(ComObjectLite*, BSTR*);
using GetItemFn = HRESULT(__stdcall*)(ComObjectLite*, BSTR, VARIANT*);
using GetNewEnumFn = HRESULT(__stdcall*)(ComObjectLite*, IUnknown**);
using PropertyAddFn = HRESULT(__stdcall*)(ComObjectLite*, BSTR, VARIANT, VARIANT);

static PropertySerializeFn gSerialize = nullptr;
static ComObjectLite* gCustomNameSpace = nullptr;
static bool gInstalled = false;
static thread_local bool gMerging = false;

inline IUnknown* VariantUnknown(VARIANT& value) {
    if (value.vt == VT_UNKNOWN) {
        return value.punkVal;
    }
    if (value.vt == VT_DISPATCH) {
        return value.pdispVal;
    }
    return nullptr;
}

inline uintptr_t FindPropertySerializePattern() {
    HMODULE module = GetModuleHandleA("PCOM.dll");
    if (!module) {
        return 0;
    }

    __try {
        auto base = reinterpret_cast<unsigned char*>(module);
        auto dos = reinterpret_cast<PIMAGE_DOS_HEADER>(base);
        if (!dos || dos->e_magic != IMAGE_DOS_SIGNATURE) {
            return 0;
        }
        auto nt = reinterpret_cast<PIMAGE_NT_HEADERS>(base + dos->e_lfanew);
        if (!nt || nt->Signature != IMAGE_NT_SIGNATURE) {
            return 0;
        }

        const unsigned char pattern[] = {
            0xB8, 0x00, 0x00, 0x00, 0x00,
            0xE8, 0x00, 0x00, 0x00, 0x00,
            0x83, 0xEC, 0x68
        };
        const char mask[] = "x????x????xxx";
        constexpr size_t patternSize = sizeof(pattern);
        const size_t imageSize = nt->OptionalHeader.SizeOfImage;
        if (imageSize < patternSize) {
            return 0;
        }

        uintptr_t match = 0;
        for (size_t i = 0; i <= imageSize - patternSize; ++i) {
            bool same = true;
            for (size_t j = 0; j < patternSize; ++j) {
                if (mask[j] == 'x' && base[i + j] != pattern[j]) {
                    same = false;
                    break;
                }
            }
            if (!same) {
                continue;
            }
            const uintptr_t current = reinterpret_cast<uintptr_t>(base + i);
            if (match != 0) {
                CrashDiagnostics::LogEvent("PCOM property serializer signature ambiguous");
                return 0;
            }
            match = current;
        }
        return match;
    }
    __except (EXCEPTION_EXECUTE_HANDLER) {
        return 0;
    }
}

inline bool IsNestedProperty(VARIANT& value) {
    IUnknown* unknown = VariantUnknown(value);
    if (!unknown) {
        return false;
    }

    ComObjectLite* nested = nullptr;
    const HRESULT hr = unknown->QueryInterface(
        kIidProperty,
        reinterpret_cast<void**>(&nested));
    if (SUCCEEDED(hr) && nested) {
        reinterpret_cast<IUnknown*>(nested)->Release();
        return true;
    }
    return false;
}

inline bool MergeMatchingProperty(
    ComObjectLite* baseProperty,
    ComObjectLite* archive) {
    if (!baseProperty || !baseProperty->vtable ||
        !archive || !archive->vtable ||
        !gCustomNameSpace || !gCustomNameSpace->vtable) {
        return true;
    }

    auto getAbsoluteUol = reinterpret_cast<GetAbsoluteUolFn>(
        archive->vtable[kArchiveAbsoluteUolIndex]);
    auto getCustomItem = reinterpret_cast<GetItemFn>(
        gCustomNameSpace->vtable[kNameSpaceItemIndex]);
    if (!getAbsoluteUol || !getCustomItem) {
        return false;
    }

    BSTR absoluteUol = nullptr;
    if (FAILED(getAbsoluteUol(archive, &absoluteUol)) || !absoluteUol) {
        if (absoluteUol) SysFreeString(absoluteUol);
        return true;
    }

    VARIANT customObject = {};
    VariantInit(&customObject);
    const HRESULT customHr = getCustomItem(
        gCustomNameSpace,
        absoluteUol,
        &customObject);
    SysFreeString(absoluteUol);
    if (FAILED(customHr)) {
        VariantClear(&customObject);
        return true;
    }

    IUnknown* customUnknown = VariantUnknown(customObject);
    if (!customUnknown) {
        VariantClear(&customObject);
        return true;
    }

    ComObjectLite* customProperty = nullptr;
    if (FAILED(customUnknown->QueryInterface(
            kIidProperty,
            reinterpret_cast<void**>(&customProperty))) ||
        !customProperty) {
        VariantClear(&customObject);
        return true;
    }

    auto getNewEnum = reinterpret_cast<GetNewEnumFn>(
        customProperty->vtable[kPropertyNewEnumIndex]);
    auto getCustomChild = reinterpret_cast<GetItemFn>(
        customProperty->vtable[kPropertyItemIndex]);
    auto addBaseChild = reinterpret_cast<PropertyAddFn>(
        baseProperty->vtable[kPropertyAddIndex]);
    if (!getNewEnum || !getCustomChild || !addBaseChild) {
        reinterpret_cast<IUnknown*>(customProperty)->Release();
        VariantClear(&customObject);
        return false;
    }

    IUnknown* enumUnknown = nullptr;
    if (FAILED(getNewEnum(customProperty, &enumUnknown)) || !enumUnknown) {
        reinterpret_cast<IUnknown*>(customProperty)->Release();
        VariantClear(&customObject);
        return false;
    }

    IEnumVARIANT* enumerator = nullptr;
    const HRESULT enumHr = enumUnknown->QueryInterface(
        IID_IEnumVARIANT,
        reinterpret_cast<void**>(&enumerator));
    enumUnknown->Release();
    if (FAILED(enumHr) || !enumerator) {
        reinterpret_cast<IUnknown*>(customProperty)->Release();
        VariantClear(&customObject);
        return false;
    }

    bool ok = true;
    while (ok) {
        VARIANT next = {};
        VariantInit(&next);
        ULONG fetched = 0;
        const HRESULT nextHr = enumerator->Next(1, &next, &fetched);
        if (nextHr == S_FALSE || fetched == 0) {
            VariantClear(&next);
            break;
        }
        if (FAILED(nextHr)) {
            VariantClear(&next);
            ok = false;
            break;
        }
        if (next.vt != VT_BSTR || !next.bstrVal) {
            VariantClear(&next);
            continue;
        }

        VARIANT customValue = {};
        VariantInit(&customValue);
        const HRESULT valueHr = getCustomChild(
            customProperty,
            next.bstrVal,
            &customValue);
        if (SUCCEEDED(valueHr) && !IsNestedProperty(customValue)) {
            VARIANT noReplace = {};
            VariantInit(&noReplace);
            noReplace.vt = VT_BOOL;
            noReplace.boolVal = VARIANT_FALSE;

            if (FAILED(addBaseChild(
                    baseProperty,
                    next.bstrVal,
                    customValue,
                    noReplace))) {
                CrashDiagnostics::LogEvent("custom WZ property child merge failed");
                ok = false;
            }
            VariantClear(&noReplace);
        }
        VariantClear(&customValue);
        VariantClear(&next);
    }

    enumerator->Release();
    reinterpret_cast<IUnknown*>(customProperty)->Release();
    VariantClear(&customObject);
    return ok;
}

inline HRESULT __stdcall SerializeHook(
    void* self,
    ComObjectLite* archive) {
    const HRESULT stockHr = gSerialize(self, archive);
    if (FAILED(stockHr) || gMerging || !self || !archive) {
        return stockHr;
    }

    gMerging = true;
    const bool merged = MergeMatchingProperty(
        reinterpret_cast<ComObjectLite*>(self),
        archive);
    gMerging = false;

    if (!merged) {
        // Stock serialization already succeeded. A custom merge failure must not
        // turn a valid base property load into a client failure.
        CrashDiagnostics::LogEvent("custom WZ property merge skipped after guarded failure");
    }
    return stockHr;
}

} // namespace detail

inline bool Install(void* customNameSpace) {
    auto object = reinterpret_cast<detail::ComObjectLite*>(customNameSpace);
    if (!object) {
        return false;
    }
    detail::gCustomNameSpace = object;

    if (detail::gInstalled) {
        return true;
    }

    const uintptr_t address = detail::FindPropertySerializePattern();
    if (!address) {
        detail::gCustomNameSpace = nullptr;
        CrashDiagnostics::LogEvent("PCOM property serializer signature unavailable");
        return false;
    }

    detail::gSerialize = reinterpret_cast<detail::PropertySerializeFn>(address);
    if (!Memory::SetHook(
            true,
            reinterpret_cast<void**>(&detail::gSerialize),
            reinterpret_cast<void*>(detail::SerializeHook))) {
        detail::gSerialize = nullptr;
        detail::gCustomNameSpace = nullptr;
        CrashDiagnostics::LogEvent("custom WZ property serializer hook failed");
        return false;
    }

    detail::gInstalled = true;
    CrashDiagnostics::LogEvent("custom WZ partial property merge enabled");
    std::cout << "EverLeaf Client v2: custom WZ property merge enabled" << std::endl;
    return true;
}

inline void Shutdown() {
    // Hook lifetime follows the process. Clear the private namespace dependency so
    // any late serializer call returns stock data only.
    detail::gCustomNameSpace = nullptr;
}

} // namespace CustomWzPropertyMerge
