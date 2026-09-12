#pragma once

#include "Memory.h"
#include "CrashDiagnostics.h"

#include <windows.h>
#include <oleauto.h>
#include <string>
#include <iostream>

// Phase 11 of the Kaentake resource-manager backport: mount an optional
// EverLeaf_Custom.wz into a private child namespace after the stock v83 resource
// manager initializes. This phase deliberately does NOT change normal root lookup
// behavior yet; lookup fallback and property merge remain later phases.
namespace CustomWzOverride {
namespace detail {

constexpr DWORD kInitializeResManAddress = 0x009F7159;
constexpr DWORD kRootNameSpaceHolderAddress = 0x00BF14E0;
constexpr DWORD kPcomApiTableAddress = 0x00BF0CC0;
constexpr const wchar_t* kCustomFileName = L"EverLeaf_Custom.wz";
constexpr const wchar_t* kCustomRootName = L"EverLeafCustom";

static const GUID kIidWritableNameSpace = {
    0xEE7659A2, 0x23CD, 0x4E44,
    { 0x86, 0xE5, 0xD8, 0x2A, 0x68, 0x0E, 0x83, 0xF7 }
};
static const GUID kIidFileSystem = {
    0x352D8655, 0x51E4, 0x4668,
    { 0x8C, 0xE4, 0x08, 0x66, 0xE2, 0xB6, 0xA5, 0xB5 }
};
static const GUID kIidPackage = {
    0xE610818B, 0x038D, 0x4522,
    { 0x92, 0x32, 0x30, 0xFC, 0xD5, 0xF4, 0x73, 0x7C }
};
static const GUID kIidSeekableArchive = {
    0x35C1F133, 0x7F61, 0x496E,
    { 0x87, 0x8F, 0x9A, 0x17, 0x58, 0xAF, 0xA9, 0xEA }
};

struct ComObjectLite {
    void** vtable;
};

using InitializeResManFn = void(__thiscall*)(void*);
using PcCreateObjectFn = HRESULT(__cdecl*)(const wchar_t*, const GUID*, void**, IUnknown*);
using NameSpaceItemFn = HRESULT(__stdcall*)(ComObjectLite*, BSTR, VARIANT*);
using NameSpaceMountFn = HRESULT(__stdcall*)(ComObjectLite*, BSTR, ComObjectLite*, int);
using CreateChildNameSpaceFn = HRESULT(__stdcall*)(ComObjectLite*, BSTR, ComObjectLite**);
using FileSystemInitFn = HRESULT(__stdcall*)(ComObjectLite*, BSTR);
using PackageInitFn = HRESULT(__stdcall*)(ComObjectLite*, BSTR, BSTR, ComObjectLite*);

// IWzNameSpace indices: item=3, Mount=6.
// IWzWritableNameSpace extends it: CreateChildNameSpace=10.
// IWzFileSystem extends writable namespace: Init=13.
// IWzPackage extends IWzNameSpace directly: Init=10.
constexpr size_t kNameSpaceItemIndex = 3;
constexpr size_t kNameSpaceMountIndex = 6;
constexpr size_t kCreateChildNameSpaceIndex = 10;
constexpr size_t kFileSystemInitIndex = 13;
constexpr size_t kPackageInitIndex = 10;

static InitializeResManFn gInitializeResMan =
    reinterpret_cast<InitializeResManFn>(kInitializeResManAddress);
static ComObjectLite* gCustomNameSpace = nullptr;
static bool gMounted = false;
static bool gInstalled = false;

inline void ReleaseObject(ComObjectLite*& object) {
    if (!object) return;
    reinterpret_cast<IUnknown*>(object)->Release();
    object = nullptr;
}

inline PcCreateObjectFn GetPcCreateObject() {
    __try {
        return reinterpret_cast<PcCreateObjectFn>(
            *reinterpret_cast<void**>(kPcomApiTableAddress));
    }
    __except (EXCEPTION_EXECUTE_HANDLER) {
        return nullptr;
    }
}

inline bool CreateObject(
    const wchar_t* className,
    const GUID& iid,
    ComObjectLite** outObject) {
    if (!outObject) return false;
    *outObject = nullptr;

    auto createObject = GetPcCreateObject();
    if (!createObject) return false;

    __try {
        return SUCCEEDED(createObject(
            className,
            &iid,
            reinterpret_cast<void**>(outObject),
            nullptr)) && *outObject != nullptr;
    }
    __except (EXCEPTION_EXECUTE_HANDLER) {
        *outObject = nullptr;
        return false;
    }
}

inline std::wstring GameDirectory() {
    wchar_t path[MAX_PATH] = {};
    const DWORD length = GetModuleFileNameW(nullptr, path, MAX_PATH);
    if (length == 0 || length >= MAX_PATH) {
        return L"";
    }

    std::wstring directory(path, length);
    const size_t slash = directory.find_last_of(L"\\/");
    if (slash == std::wstring::npos) {
        return L"";
    }
    directory.resize(slash);
    for (wchar_t& ch : directory) {
        if (ch == L'\\') ch = L'/';
    }
    return directory;
}

inline bool CustomFileExists(const std::wstring& directory) {
    if (directory.empty()) return false;
    const std::wstring filePath = directory + L"/" + kCustomFileName;
    const DWORD attributes = GetFileAttributesW(filePath.c_str());
    return attributes != INVALID_FILE_ATTRIBUTES &&
           (attributes & FILE_ATTRIBUTE_DIRECTORY) == 0;
}

inline ComObjectLite* GetRootNameSpace() {
    __try {
        return *reinterpret_cast<ComObjectLite**>(kRootNameSpaceHolderAddress);
    }
    __except (EXCEPTION_EXECUTE_HANDLER) {
        return nullptr;
    }
}

inline bool MountCustomPackage() {
    if (gMounted) return true;

    const std::wstring directory = GameDirectory();
    if (!CustomFileExists(directory)) {
        CrashDiagnostics::LogEvent("EverLeaf_Custom.wz not present; custom namespace disabled");
        return true;
    }

    ComObjectLite* root = GetRootNameSpace();
    if (!root) {
        CrashDiagnostics::LogEvent("root WZ namespace unavailable for EverLeaf custom mount");
        return false;
    }

    ComObjectLite* writableRoot = nullptr;
    ComObjectLite* fileSystem = nullptr;
    ComObjectLite* package = nullptr;
    ComObjectLite* archive = nullptr;
    ComObjectLite* customNameSpace = nullptr;
    VARIANT archiveVariant = {};
    VariantInit(&archiveVariant);

    bool success = false;
    BSTR customRootName = nullptr;
    BSTR directoryBstr = nullptr;
    BSTR customFileName = nullptr;
    BSTR packageKey = nullptr;
    BSTR packageBase = nullptr;
    BSTR mountRoot = nullptr;

    __try {
        if (FAILED(reinterpret_cast<IUnknown*>(root)->QueryInterface(
                kIidWritableNameSpace,
                reinterpret_cast<void**>(&writableRoot))) || !writableRoot) {
            CrashDiagnostics::LogEvent("root WZ namespace is not writable");
            __leave;
        }

        customRootName = SysAllocString(kCustomRootName);
        if (!customRootName) __leave;
        auto createChild = reinterpret_cast<CreateChildNameSpaceFn>(
            writableRoot->vtable[kCreateChildNameSpaceIndex]);
        if (!createChild || FAILED(createChild(
                writableRoot,
                customRootName,
                &customNameSpace)) || !customNameSpace) {
            CrashDiagnostics::LogEvent("failed to create EverLeaf custom child namespace");
            __leave;
        }

        if (!CreateObject(L"NameSpace#FileSystem", kIidFileSystem, &fileSystem)) {
            CrashDiagnostics::LogEvent("failed to create WZ file-system object");
            __leave;
        }
        directoryBstr = SysAllocString(directory.c_str());
        if (!directoryBstr) __leave;
        auto initializeFileSystem = reinterpret_cast<FileSystemInitFn>(
            fileSystem->vtable[kFileSystemInitIndex]);
        if (!initializeFileSystem || FAILED(initializeFileSystem(
                fileSystem,
                directoryBstr))) {
            CrashDiagnostics::LogEvent("failed to initialize WZ file-system object");
            __leave;
        }

        customFileName = SysAllocString(kCustomFileName);
        if (!customFileName) __leave;
        auto getItem = reinterpret_cast<NameSpaceItemFn>(
            fileSystem->vtable[kNameSpaceItemIndex]);
        if (!getItem || FAILED(getItem(
                fileSystem,
                customFileName,
                &archiveVariant))) {
            CrashDiagnostics::LogEvent("EverLeaf custom WZ archive lookup failed");
            __leave;
        }

        IUnknown* archiveUnknown = nullptr;
        if (archiveVariant.vt == VT_UNKNOWN) {
            archiveUnknown = archiveVariant.punkVal;
        }
        else if (archiveVariant.vt == VT_DISPATCH) {
            archiveUnknown = archiveVariant.pdispVal;
        }
        if (!archiveUnknown || FAILED(archiveUnknown->QueryInterface(
                kIidSeekableArchive,
                reinterpret_cast<void**>(&archive))) || !archive) {
            CrashDiagnostics::LogEvent("EverLeaf custom WZ is not a seekable archive");
            __leave;
        }

        if (!CreateObject(L"NameSpace#Package", kIidPackage, &package)) {
            CrashDiagnostics::LogEvent("failed to create WZ package object");
            __leave;
        }
        packageKey = SysAllocString(L"83");
        packageBase = SysAllocString(kCustomRootName);
        if (!packageKey || !packageBase) __leave;
        auto initializePackage = reinterpret_cast<PackageInitFn>(
            package->vtable[kPackageInitIndex]);
        if (!initializePackage || FAILED(initializePackage(
                package,
                packageKey,
                packageBase,
                archive))) {
            CrashDiagnostics::LogEvent("EverLeaf custom WZ package initialization failed");
            __leave;
        }

        mountRoot = SysAllocString(L"/");
        if (!mountRoot) __leave;
        auto mount = reinterpret_cast<NameSpaceMountFn>(
            customNameSpace->vtable[kNameSpaceMountIndex]);
        if (!mount || FAILED(mount(customNameSpace, mountRoot, package, 1))) {
            CrashDiagnostics::LogEvent("EverLeaf custom WZ package mount failed");
            __leave;
        }

        gCustomNameSpace = customNameSpace;
        customNameSpace = nullptr;
        gMounted = true;
        success = true;
        CrashDiagnostics::LogEvent("EverLeaf custom WZ mounted in private namespace");
        std::cout << "EverLeaf Client v2: mounted EverLeaf_Custom.wz privately" << std::endl;
    }
    __except (EXCEPTION_EXECUTE_HANDLER) {
        CrashDiagnostics::LogEvent("EverLeaf custom WZ mount raised an exception");
        success = false;
    }

    if (customRootName) SysFreeString(customRootName);
    if (directoryBstr) SysFreeString(directoryBstr);
    if (customFileName) SysFreeString(customFileName);
    if (packageKey) SysFreeString(packageKey);
    if (packageBase) SysFreeString(packageBase);
    if (mountRoot) SysFreeString(mountRoot);
    VariantClear(&archiveVariant);
    ReleaseObject(archive);
    ReleaseObject(package);
    ReleaseObject(fileSystem);
    ReleaseObject(writableRoot);
    ReleaseObject(customNameSpace);

    return success;
}

inline void __fastcall InitializeResManHook(void* self, void*) {
    gInitializeResMan(self);
    if (!MountCustomPackage()) {
        // The stock v83 resource manager is already initialized. Custom WZ failure
        // is non-fatal until the override path is explicitly enabled later.
        CrashDiagnostics::LogEvent("EverLeaf custom WZ mount unavailable; stock resources kept");
    }
}

} // namespace detail

inline bool Install() {
    if (detail::gInstalled) return true;

    if (!Memory::SetHook(
            true,
            reinterpret_cast<void**>(&detail::gInitializeResMan),
            reinterpret_cast<void*>(detail::InitializeResManHook))) {
        CrashDiagnostics::LogEvent("EverLeaf custom WZ InitializeResMan hook failed");
        return false;
    }

    detail::gInstalled = true;
    CrashDiagnostics::LogEvent("EverLeaf custom WZ mount hook installed");
    return true;
}

inline bool IsMounted() {
    return detail::gMounted && detail::gCustomNameSpace != nullptr;
}

inline void* CustomNameSpace() {
    return detail::gCustomNameSpace;
}

inline void Shutdown() {
    detail::ReleaseObject(detail::gCustomNameSpace);
    detail::gMounted = false;
}

} // namespace CustomWzOverride
