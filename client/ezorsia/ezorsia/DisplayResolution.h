#pragma once

#include "Client.h"
#include "Memory.h"
#include "CrashDiagnostics.h"

#include <windows.h>
#include <cstdio>
#include <cstring>
#include <new>

// EverLeaf's safe in-game resolution preference selector for the pinned GMS v83
// client. The System Options hook points, native CCtrlComboBox and placement are
// based on Kaentake's proven v83 implementation, with EverLeaf's 1280x720 mode
// added to the list.
//
// IMPORTANT: selecting a resolution here only persists the preference. EverLeaf
// applies it through the normal startup resolution path on the next launch. We do
// not mutate the live Gr2D/D3D screen mode here; that partial renderer-reset path
// was the cause of the Alt+Enter crash and must stay out of this module.
namespace DisplayResolution {
namespace detail {
constexpr DWORD kApplySysOptAddress = 0x0049EA33;
constexpr DWORD kSysOptOnCreateAddress = 0x00994163;
constexpr DWORD kSysOptDestructorAddress = 0x007FF4AA;
constexpr DWORD kSysOptButtonYOperand = 0x009945BD;
constexpr int kSysOptButtonY = 372;

// GMS v83 native CCtrlComboBox contracts used by Kaentake.
constexpr DWORD kComboCtorAddress = 0x004C4259;
constexpr DWORD kComboParamCtorAddress = 0x004B620C;
constexpr DWORD kComboParamDtorAddress = 0x004B63AE;
constexpr DWORD kComboAddItemAddress = 0x004C6DD6;
constexpr DWORD kComboSetSelectAddress = 0x004C738B;
constexpr size_t kComboObjectSize = 0x10C;
constexpr size_t kComboSelectOffset = 0x68;
constexpr size_t kComboParamSize = 0x50;
constexpr size_t kComboCreateVtableIndex = 8;

struct ResolutionEntry {
    int width;
    int height;
    const char* label;
};

static const ResolutionEntry kResolutions[] = {
    { 800, 600, "800 x 600" },
    { 1024, 768, "1024 x 768" },
    { 1280, 720, "1280 x 720" },
    { 1366, 768, "1366 x 768" },
    { 1600, 900, "1600 x 900" },
    { 1920, 1080, "1920 x 1080" },
};
constexpr int kResolutionCount = sizeof(kResolutions) / sizeof(kResolutions[0]);
constexpr int kEverLeafDefaultResolutionIndex = 2;

using ApplySysOptFn = void(__thiscall*)(void*, void*, int);
using SysOptOnCreateFn = void(__thiscall*)(void*, void*);
using SysOptDestructorFn = void(__thiscall*)(void*);
using ComboCtorFn = void(__thiscall*)(void*);
using ComboParamCtorFn = void(__thiscall*)(void*);
using ComboParamDtorFn = void(__thiscall*)(void*);
using ComboCreateFn = void(__thiscall*)(void*, void*, unsigned int, int, int, int, int, int, void*);
using ComboAddItemFn = void(__thiscall*)(void*, const char*, unsigned int);
using ComboSetSelectFn = void(__thiscall*)(void*, int);

static ApplySysOptFn gApplySysOpt = reinterpret_cast<ApplySysOptFn>(kApplySysOptAddress);
static SysOptOnCreateFn gSysOptOnCreate = reinterpret_cast<SysOptOnCreateFn>(kSysOptOnCreateAddress);
static SysOptDestructorFn gSysOptDestructor = reinterpret_cast<SysOptDestructorFn>(kSysOptDestructorAddress);
static void* gResolutionCombo = nullptr;
static bool gInstalled = false;

inline HWND FindGameWindow() {
    HWND window = FindWindowA("MapleStoryClass", nullptr);
    if (!window) return nullptr;

    DWORD processId = 0;
    GetWindowThreadProcessId(window, &processId);
    return processId == GetCurrentProcessId() ? window : nullptr;
}

inline const char* ConfigPath() {
    static char path[MAX_PATH] = {};
    static bool initialized = false;
    if (initialized) return path;
    initialized = true;

    DWORD length = GetModuleFileNameA(nullptr, path, MAX_PATH);
    if (length == 0 || length >= MAX_PATH) {
        std::strcpy(path, "config.ini");
        return path;
    }

    char* slash = std::strrchr(path, '\\');
    if (slash) {
        *(slash + 1) = '\0';
        std::strcat(path, "config.ini");
    }
    else {
        std::strcpy(path, "config.ini");
    }
    return path;
}

inline int ConfiguredWidth() {
    return GetPrivateProfileIntA("general", "width", Client::m_nGameWidth, ConfigPath());
}

inline int ConfiguredHeight() {
    return GetPrivateProfileIntA("general", "height", Client::m_nGameHeight, ConfigPath());
}

inline void SaveResolutionConfig(int width, int height) {
    char widthText[16] = {};
    char heightText[16] = {};
    std::sprintf(widthText, "%d", width);
    std::sprintf(heightText, "%d", height);
    WritePrivateProfileStringA("general", "width", widthText, ConfigPath());
    WritePrivateProfileStringA("general", "height", heightText, ConfigPath());
}

inline int ResolutionIndexFor(int width, int height) {
    for (int i = 0; i < kResolutionCount; ++i) {
        if (kResolutions[i].width == width && kResolutions[i].height == height) {
            return i;
        }
    }
    return kEverLeafDefaultResolutionIndex;
}

inline int SelectedIndex() {
    if (!gResolutionCombo) {
        return ResolutionIndexFor(ConfiguredWidth(), ConfiguredHeight());
    }

    __try {
        const int selected = *reinterpret_cast<int*>(
            reinterpret_cast<unsigned char*>(gResolutionCombo) + kComboSelectOffset);
        if (selected >= 0 && selected < kResolutionCount) return selected;
    }
    __except (EXCEPTION_EXECUTE_HANDLER) {
        CrashDiagnostics::LogEvent("native resolution selector state unavailable");
    }

    return ResolutionIndexFor(ConfiguredWidth(), ConfiguredHeight());
}

inline bool CreateNativeSelector(void* sysOpt) {
    if (!sysOpt) return false;
    gResolutionCombo = nullptr;

    void* combo = ::operator new(kComboObjectSize, std::nothrow);
    if (!combo) return false;
    std::memset(combo, 0, kComboObjectSize);

    alignas(4) unsigned char params[kComboParamSize] = {};
    bool paramConstructed = false;

    __try {
        reinterpret_cast<ComboCtorFn>(kComboCtorAddress)(combo);
        reinterpret_cast<ComboParamCtorFn>(kComboParamCtorAddress)(params);
        paramConstructed = true;

        *reinterpret_cast<int*>(params + 0x00) = static_cast<int>(0xFFEEEEEEu);
        *reinterpret_cast<int*>(params + 0x04) = static_cast<int>(0xFFA5A198u);
        *reinterpret_cast<int*>(params + 0x08) = static_cast<int>(0xFF999999u);

        void** vtable = *reinterpret_cast<void***>(combo);
        if (!vtable || !vtable[kComboCreateVtableIndex]) {
            if (paramConstructed) reinterpret_cast<ComboParamDtorFn>(kComboParamDtorAddress)(params);
            CrashDiagnostics::LogEvent("native resolution selector vtable unavailable");
            return false;
        }

        auto createCtrl = reinterpret_cast<ComboCreateFn>(vtable[kComboCreateVtableIndex]);
        // Kaentake v83 placement: native combo at (76,338), 166x18, control id 2000.
        createCtrl(combo, sysOpt, 2000, 0, 76, 338, 166, 18, params);

        if (paramConstructed) {
            reinterpret_cast<ComboParamDtorFn>(kComboParamDtorAddress)(params);
            paramConstructed = false;
        }

        auto addItem = reinterpret_cast<ComboAddItemFn>(kComboAddItemAddress);
        for (int i = 0; i < kResolutionCount; ++i) {
            addItem(combo, kResolutions[i].label, static_cast<unsigned int>(i));
        }

        reinterpret_cast<ComboSetSelectFn>(kComboSetSelectAddress)(
            combo,
            ResolutionIndexFor(ConfiguredWidth(), ConfiguredHeight()));

        gResolutionCombo = combo;
        CrashDiagnostics::LogEvent("Maple-native resolution selector created");
        return true;
    }
    __except (EXCEPTION_EXECUTE_HANDLER) {
        if (paramConstructed) {
            __try {
                reinterpret_cast<ComboParamDtorFn>(kComboParamDtorAddress)(params);
            }
            __except (EXCEPTION_EXECUTE_HANDLER) {
            }
        }
        CrashDiagnostics::LogEvent("Maple-native resolution selector creation raised an exception");
        return false;
    }
}

inline void __fastcall ApplySysOptHook(void* self, void*, void* sysOpt, int applyVideo) {
    gApplySysOpt(self, sysOpt, applyVideo);
    if (!sysOpt || !applyVideo) return;

    const int index = SelectedIndex();
    const ResolutionEntry& selected = kResolutions[index];
    const int configuredWidth = ConfiguredWidth();
    const int configuredHeight = ConfiguredHeight();

    if (selected.width == configuredWidth && selected.height == configuredHeight) return;

    SaveResolutionConfig(selected.width, selected.height);
    CrashDiagnostics::LogEvent("resolution preference saved for next launch");
    MessageBoxW(
        FindGameWindow(),
        L"Resolution saved. It will be applied the next time EverLeaf starts.",
        L"EverLeaf display settings",
        MB_OK | MB_ICONINFORMATION);
}

inline void __fastcall SysOptOnCreateHook(void* self, void*, void* data) {
    gSysOptOnCreate(self, data);
    if (!CreateNativeSelector(self)) {
        CrashDiagnostics::LogEvent("Maple-native in-game resolution selector unavailable");
    }
}

inline void __fastcall SysOptDestructorHook(void* self, void*) {
    // CUISysOpt owns its child controls after CreateCtrl. Do not separately delete
    // the combo here; the parent destroys/releases it through Maple's native list.
    gResolutionCombo = nullptr;
    gSysOptDestructor(self);
}

} // namespace detail

inline bool Install() {
    if (detail::gInstalled) return true;

    // Shift the stock OK/Cancel row down to make room for the native resolution
    // combo, matching Kaentake's v83 System Options layout.
    Memory::WriteInt(detail::kSysOptButtonYOperand, detail::kSysOptButtonY);

    if (!Memory::SetHook(
            true,
            reinterpret_cast<void**>(&detail::gApplySysOpt),
            reinterpret_cast<void*>(detail::ApplySysOptHook))) return false;
    if (!Memory::SetHook(
            true,
            reinterpret_cast<void**>(&detail::gSysOptOnCreate),
            reinterpret_cast<void*>(detail::SysOptOnCreateHook))) return false;
    if (!Memory::SetHook(
            true,
            reinterpret_cast<void**>(&detail::gSysOptDestructor),
            reinterpret_cast<void*>(detail::SysOptDestructorHook))) return false;

    detail::gInstalled = true;
    CrashDiagnostics::LogEvent("Maple-native in-game resolution selector hooks installed");
    std::cout << "EverLeaf Client v2: Maple-native resolution selector enabled" << std::endl;
    return true;
}

inline void Shutdown() {
    detail::gResolutionCombo = nullptr;
}

} // namespace DisplayResolution
