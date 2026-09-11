#pragma once

#include "Client.h"
#include "Memory.h"
#include "CrashDiagnostics.h"

#include <windows.h>
#include <cstdio>
#include <cstring>

// EverLeaf's safe in-game resolution preference selector for the pinned GMS v83
// client. The System Options hook points and selector placement follow the proven
// Kaentake v83 approach, with EverLeaf's 1280x720 mode added to the list.
//
// IMPORTANT: this module deliberately does not mutate Gr2D/D3D screen-mode state
// while the client is running. The previous live renderer reset path caused an
// access violation when Alt+Enter was used. A player's selection is persisted to
// config.ini and applied by EverLeaf's normal startup resolution path next launch.
namespace DisplayResolution {
namespace detail {
constexpr DWORD kApplySysOptAddress = 0x0049EA33;
constexpr DWORD kSysOptOnCreateAddress = 0x00994163;
constexpr DWORD kSysOptDestructorAddress = 0x007FF4AA;
constexpr DWORD kSysOptButtonYOperand = 0x009945BD; // CUISysOpt::OnCreate immediate
constexpr int kSysOptButtonY = 372;

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

static ApplySysOptFn gApplySysOpt = reinterpret_cast<ApplySysOptFn>(kApplySysOptAddress);
static SysOptOnCreateFn gSysOptOnCreate = reinterpret_cast<SysOptOnCreateFn>(kSysOptOnCreateAddress);
static SysOptDestructorFn gSysOptDestructor = reinterpret_cast<SysOptDestructorFn>(kSysOptDestructorAddress);
static HWND gResolutionCombo = nullptr;
static HWND gResolutionLabel = nullptr;
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
    if (gResolutionCombo && IsWindow(gResolutionCombo)) {
        const LRESULT selected = SendMessageA(gResolutionCombo, CB_GETCURSEL, 0, 0);
        if (selected >= 0 && selected < kResolutionCount) {
            return static_cast<int>(selected);
        }
    }
    return ResolutionIndexFor(ConfiguredWidth(), ConfiguredHeight());
}

inline void DestroySelector() {
    if (gResolutionCombo && IsWindow(gResolutionCombo)) DestroyWindow(gResolutionCombo);
    if (gResolutionLabel && IsWindow(gResolutionLabel)) DestroyWindow(gResolutionLabel);
    gResolutionCombo = nullptr;
    gResolutionLabel = nullptr;
}

inline void CreateSelector(void* sysOpt) {
    DestroySelector();

    HWND parent = FindGameWindow();
    if (!parent) return;

    RECT client = {};
    if (!GetClientRect(parent, &client)) return;

    int dialogWidth = 320;
    int dialogHeight = 400;
    __try {
        const int candidateWidth = *reinterpret_cast<int*>(reinterpret_cast<unsigned char*>(sysOpt) + 0x24);
        const int candidateHeight = *reinterpret_cast<int*>(reinterpret_cast<unsigned char*>(sysOpt) + 0x28);
        if (candidateWidth >= 200 && candidateWidth <= 700) dialogWidth = candidateWidth;
        if (candidateHeight >= 300 && candidateHeight <= 600) dialogHeight = candidateHeight;
    }
    __except (EXCEPTION_EXECUTE_HANDLER) {
        // Fall back to the stock v83 System Options dimensions.
    }

    const int clientWidth = client.right - client.left;
    const int clientHeight = client.bottom - client.top;
    const int left = (clientWidth - dialogWidth) / 2;
    const int top = (clientHeight - dialogHeight) / 2;

    // Kaentake's v83 System Options resolution selector is positioned at
    // (76,338) inside the options dialog. Keep that proven layout here.
    const int selectorX = left + 76;
    const int selectorY = top + 338;

    gResolutionLabel = CreateWindowExA(
        0,
        "STATIC",
        "Resolution",
        WS_CHILD | WS_VISIBLE,
        selectorX,
        selectorY - 18,
        166,
        18,
        parent,
        nullptr,
        GetModuleHandleA(nullptr),
        nullptr
    );

    gResolutionCombo = CreateWindowExA(
        WS_EX_CLIENTEDGE,
        "COMBOBOX",
        "",
        WS_CHILD | WS_VISIBLE | WS_TABSTOP | CBS_DROPDOWNLIST | WS_VSCROLL,
        selectorX,
        selectorY,
        166,
        150,
        parent,
        nullptr,
        GetModuleHandleA(nullptr),
        nullptr
    );

    if (!gResolutionCombo) {
        DestroySelector();
        CrashDiagnostics::LogEvent("in-game resolution selector creation failed");
        return;
    }

    HFONT font = static_cast<HFONT>(GetStockObject(DEFAULT_GUI_FONT));
    if (gResolutionLabel) {
        SendMessageA(gResolutionLabel, WM_SETFONT, reinterpret_cast<WPARAM>(font), TRUE);
    }
    SendMessageA(gResolutionCombo, WM_SETFONT, reinterpret_cast<WPARAM>(font), TRUE);

    for (int i = 0; i < kResolutionCount; ++i) {
        SendMessageA(gResolutionCombo, CB_ADDSTRING, 0, reinterpret_cast<LPARAM>(kResolutions[i].label));
    }

    SendMessageA(
        gResolutionCombo,
        CB_SETCURSEL,
        ResolutionIndexFor(ConfiguredWidth(), ConfiguredHeight()),
        0
    );

    SetWindowPos(
        gResolutionCombo,
        HWND_TOP,
        0,
        0,
        0,
        0,
        SWP_NOMOVE | SWP_NOSIZE | SWP_SHOWWINDOW
    );
    if (gResolutionLabel) {
        SetWindowPos(
            gResolutionLabel,
            HWND_TOP,
            0,
            0,
            0,
            0,
            SWP_NOMOVE | SWP_NOSIZE | SWP_SHOWWINDOW
        );
    }
}

inline void __fastcall ApplySysOptHook(void* self, void*, void* sysOpt, int applyVideo) {
    gApplySysOpt(self, sysOpt, applyVideo);
    if (!sysOpt || !applyVideo) return;

    const int index = SelectedIndex();
    const ResolutionEntry& selected = kResolutions[index];
    const int configuredWidth = ConfiguredWidth();
    const int configuredHeight = ConfiguredHeight();

    if (selected.width == configuredWidth && selected.height == configuredHeight) {
        return;
    }

    SaveResolutionConfig(selected.width, selected.height);
    CrashDiagnostics::LogEvent("resolution preference saved for next launch");
    MessageBoxW(
        FindGameWindow(),
        L"Resolution saved. It will be applied the next time EverLeaf starts.",
        L"EverLeaf display settings",
        MB_OK | MB_ICONINFORMATION
    );
}

inline void __fastcall SysOptOnCreateHook(void* self, void*, void* data) {
    gSysOptOnCreate(self, data);
    CreateSelector(self);
}

inline void __fastcall SysOptDestructorHook(void* self, void*) {
    DestroySelector();
    gSysOptDestructor(self);
}

} // namespace detail

inline bool Install() {
    if (detail::gInstalled) return true;

    // Make room beneath the stock v83 video options, matching Kaentake's proven
    // System Options placement while keeping EverLeaf's renderer untouched.
    Memory::WriteInt(detail::kSysOptButtonYOperand, detail::kSysOptButtonY);

    if (!Memory::SetHook(
            true,
            reinterpret_cast<void**>(&detail::gApplySysOpt),
            reinterpret_cast<void*>(detail::ApplySysOptHook))) {
        return false;
    }
    if (!Memory::SetHook(
            true,
            reinterpret_cast<void**>(&detail::gSysOptOnCreate),
            reinterpret_cast<void*>(detail::SysOptOnCreateHook))) {
        return false;
    }
    if (!Memory::SetHook(
            true,
            reinterpret_cast<void**>(&detail::gSysOptDestructor),
            reinterpret_cast<void*>(detail::SysOptDestructorHook))) {
        return false;
    }

    detail::gInstalled = true;
    CrashDiagnostics::LogEvent("safe in-game resolution selector hooks installed");
    std::cout << "EverLeaf Client v2: in-game resolution selector enabled" << std::endl;
    return true;
}

inline void Shutdown() {
    detail::DestroySelector();
}

} // namespace DisplayResolution
