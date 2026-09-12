#pragma once

#include "Memory.h"
#include "CrashDiagnostics.h"

#include <windows.h>
#include <oleauto.h>
#include <algorithm>
#include <cstddef>
#include <cstdint>
#include <iostream>
#include <string>
#include <vector>

// Phase 12 of the Kaentake resource-manager backport. The custom WZ remains
// mounted in a private namespace; this module indexes only paths that actually
// exist there and falls back to that namespace only when the stock NameSpace.dll
// local-object lookup fails for one of those indexed paths.
namespace CustomWzLookup {
namespace detail {

constexpr size_t kNameSpaceItemIndex = 3;
constexpr size_t kNameSpaceNewEnumIndex = 5;
constexpr size_t kPropertyItemIndex = 5;
constexpr size_t kPropertyNewEnumIndex = 7;
constexpr size_t kMaxOverrideDepth = 64;
constexpr size_t kMaxOverrideCount = 200000;

static const GUID kIidNameSpace = {
    0x2AEEEB36, 0xA4E1, 0x4E2B,
    { 0x8F, 0x6F, 0x2E, 0x7B, 0xDE, 0xC5, 0xC5, 0x3D }
};
static const GUID kIidProperty = {
    0x986515D9, 0x0A0B, 0x4929,
    { 0x8B, 0x4F, 0x71, 0x86, 0x82, 0x17, 0x7B, 0x92 }
};

struct ComObjectLite {
    void** vtable;
};

enum class ContainerKind {
    NameSpace,
    Property,
};

using GetNewEnumFn = HRESULT(__stdcall*)(ComObjectLite*, IUnknown**);
using GetItemFn = HRESULT(__stdcall*)(ComObjectLite*, BSTR, VARIANT*);
using OnGetLocalObjectFn = HRESULT(__stdcall*)(
    void*,
    int,
    BSTR,
    int*,
    VARIANT*);

static std::vector<std::wstring> gOverridePaths;
static ComObjectLite* gCustomNameSpace = nullptr;
static OnGetLocalObjectFn gOnGetLocalObject = nullptr;
static bool gLookupInstalled = false;

inline IUnknown* VariantUnknown(VARIANT& value) {
    if (value.vt == VT_UNKNOWN) {
        return value.punkVal;
    }
    if (value.vt == VT_DISPATCH) {
        return value.pdispVal;
    }
    return nullptr;
}

inline bool EnumerateContainer(
    ComObjectLite* container,
    ContainerKind kind,
    const std::wstring& prefix,
    size_t depth) {
    if (!container || !container->vtable || depth > kMaxOverrideDepth) {
        CrashDiagnostics::LogEvent("custom WZ override enumeration depth/object guard hit");
        return false;
    }

    const size_t newEnumIndex = kind == ContainerKind::NameSpace
        ? kNameSpaceNewEnumIndex
        : kPropertyNewEnumIndex;
    const size_t itemIndex = kind == ContainerKind::NameSpace
        ? kNameSpaceItemIndex
        : kPropertyItemIndex;

    auto getNewEnum = reinterpret_cast<GetNewEnumFn>(
        container->vtable[newEnumIndex]);
    auto getItem = reinterpret_cast<GetItemFn>(
        container->vtable[itemIndex]);
    if (!getNewEnum || !getItem) {
        return false;
    }

    IUnknown* enumUnknown = nullptr;
    if (FAILED(getNewEnum(container, &enumUnknown)) || !enumUnknown) {
        return false;
    }

    IEnumVARIANT* enumerator = nullptr;
    const HRESULT enumHr = enumUnknown->QueryInterface(
        IID_IEnumVARIANT,
        reinterpret_cast<void**>(&enumerator));
    enumUnknown->Release();
    if (FAILED(enumHr) || !enumerator) {
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

        const std::wstring childName(
            next.bstrVal,
            static_cast<size_t>(SysStringLen(next.bstrVal)));
        if (childName.empty()) {
            VariantClear(&next);
            continue;
        }

        const std::wstring childPath = prefix.empty()
            ? childName
            : prefix + L"/" + childName;
        if (gOverridePaths.size() >= kMaxOverrideCount) {
            CrashDiagnostics::LogEvent("custom WZ override enumeration count guard hit");
            VariantClear(&next);
            ok = false;
            break;
        }
        gOverridePaths.push_back(childPath);

        VARIANT child = {};
        VariantInit(&child);
        const HRESULT itemHr = getItem(container, next.bstrVal, &child);
        if (SUCCEEDED(itemHr)) {
            IUnknown* childUnknown = VariantUnknown(child);
            if (childUnknown) {
                ComObjectLite* childNameSpace = nullptr;
                if (SUCCEEDED(childUnknown->QueryInterface(
                        kIidNameSpace,
                        reinterpret_cast<void**>(&childNameSpace))) &&
                    childNameSpace) {
                    ok = EnumerateContainer(
                        childNameSpace,
                        ContainerKind::NameSpace,
                        childPath,
                        depth + 1);
                    reinterpret_cast<IUnknown*>(childNameSpace)->Release();
                }
                else {
                    ComObjectLite* childProperty = nullptr;
                    if (SUCCEEDED(childUnknown->QueryInterface(
                            kIidProperty,
                            reinterpret_cast<void**>(&childProperty))) &&
                        childProperty) {
                        ok = EnumerateContainer(
                            childProperty,
                            ContainerKind::Property,
                            childPath,
                            depth + 1);
                        reinterpret_cast<IUnknown*>(childProperty)->Release();
                    }
                }
            }
        }
        VariantClear(&child);
        VariantClear(&next);
    }

    enumerator->Release();
    return ok;
}

inline bool BuildOverrideIndex(ComObjectLite* customNameSpace) {
    gOverridePaths.clear();
    if (!EnumerateContainer(
            customNameSpace,
            ContainerKind::NameSpace,
            L"",
            0)) {
        gOverridePaths.clear();
        CrashDiagnostics::LogEvent("custom WZ override enumeration failed");
        return false;
    }

    std::sort(gOverridePaths.begin(), gOverridePaths.end());
    gOverridePaths.erase(
        std::unique(gOverridePaths.begin(), gOverridePaths.end()),
        gOverridePaths.end());

    CrashDiagnostics::LogEvent("custom WZ override index built");
    std::cout << "EverLeaf Client v2: indexed "
              << gOverridePaths.size()
              << " custom WZ override paths" << std::endl;
    return true;
}

inline bool HasOverride(BSTR path) {
    if (!path || gOverridePaths.empty()) {
        return false;
    }
    const std::wstring key(path, static_cast<size_t>(SysStringLen(path)));
    return std::binary_search(
        gOverridePaths.begin(),
        gOverridePaths.end(),
        key);
}

inline uintptr_t FindNameSpaceLocalObjectPattern() {
    HMODULE module = GetModuleHandleA("NameSpace.dll");
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
            0x81, 0xEC, 0x80
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
                CrashDiagnostics::LogEvent("NameSpace local-object signature ambiguous");
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

inline HRESULT __stdcall OnGetLocalObjectHook(
    void* self,
    int index,
    BSTR path,
    int* pathUsed,
    VARIANT* result) {
    const HRESULT stockHr = gOnGetLocalObject(
        self,
        index,
        path,
        pathUsed,
        result);
    if (SUCCEEDED(stockHr) || !gCustomNameSpace || !HasOverride(path)) {
        return stockHr;
    }

    // Memory::SetHook converts gOnGetLocalObject into the original trampoline.
    // Calling that trampoline directly with the private namespace avoids a
    // recursive trip through this hook if the custom lookup also fails.
    const HRESULT customHr = gOnGetLocalObject(
        gCustomNameSpace,
        index,
        path,
        pathUsed,
        result);
    if (SUCCEEDED(customHr)) {
        return customHr;
    }

    // Preserve the stock failure when a malformed/incomplete custom path cannot
    // actually be resolved despite being present in the enumeration index.
    return stockHr;
}

inline bool InstallLookupHook() {
    if (gLookupInstalled || gOverridePaths.empty()) {
        return true;
    }

    const uintptr_t address = FindNameSpaceLocalObjectPattern();
    if (!address) {
        CrashDiagnostics::LogEvent("NameSpace local-object signature unavailable");
        return false;
    }

    gOnGetLocalObject = reinterpret_cast<OnGetLocalObjectFn>(address);
    if (!Memory::SetHook(
            true,
            reinterpret_cast<void**>(&gOnGetLocalObject),
            reinterpret_cast<void*>(OnGetLocalObjectHook))) {
        gOnGetLocalObject = nullptr;
        CrashDiagnostics::LogEvent("custom WZ local-object fallback hook failed");
        return false;
    }

    gLookupInstalled = true;
    CrashDiagnostics::LogEvent("custom WZ local-object fallback enabled");
    std::cout << "EverLeaf Client v2: custom WZ lookup fallback enabled" << std::endl;
    return true;
}

} // namespace detail

inline bool Prepare(void* customNameSpace) {
    auto object = reinterpret_cast<detail::ComObjectLite*>(customNameSpace);
    if (!object) {
        return false;
    }

    detail::gCustomNameSpace = object;
    if (!detail::BuildOverrideIndex(object)) {
        detail::gCustomNameSpace = nullptr;
        return false;
    }

    if (!detail::InstallLookupHook()) {
        detail::gOverridePaths.clear();
        detail::gCustomNameSpace = nullptr;
        return false;
    }
    return true;
}

inline size_t OverrideCount() {
    return detail::gOverridePaths.size();
}

inline void Shutdown() {
    // Process teardown owns hook lifetime; clearing the lookup state makes any
    // late invocation fall through to the stock trampoline without custom work.
    detail::gCustomNameSpace = nullptr;
    detail::gOverridePaths.clear();
}

} // namespace CustomWzLookup
