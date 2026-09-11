#pragma once

#include "Client.h"
#include "Memory.h"
#include "WidescreenCorrections.h"
#include "CrashDiagnostics.h"

#include <windows.h>
#include <cstdio>
#include <cstring>

// EverLeaf's runtime display integration for the pinned GMS v83 client.
//
// The original inherited HD layer patched width/height constants only at startup.
// Maple's own System Options path can recreate the Gr2D screen mode at stock
// 800x600, and the old Alt+Enter code only changed Win32 window chrome.  This
// module keeps the selected HD resolution authoritative across both paths.
//
// The v83 contracts below were cross-checked against the same client layout used
// by EverLeaf and the Kaentake v83 implementation.  We intentionally reproduce
// the behavior independently rather than importing Kaentake source.
namespace DisplayResolution {
namespace detail {
constexpr DWORD kGr2DGlobal = 0x00BF14EC;
constexpr DWORD kApplySysOptAddress = 0x0049EA33;
constexpr DWORD kSysOptOnCreateAddress = 0x00994163;
constexpr DWORD kSysOptDestructorAddress = 0x007FF4AA;
constexpr DWORD kSysOptButtonYOperand = 0x009945BD; // CUISysOpt::OnCreate immediate
constexpr int kSysOptButtonY = 372;

constexpr int kScreenModeOffset = 0x20;
constexpr int kScreenModeSize = 0x5C;
constexpr int kScreenModeWidthOffset = 0x00;
constexpr int kScreenModeHeightOffset = 0x04;
constexpr int kScreenModeFullscreenOffset = 0x58;
constexpr int kGr2DInitializedOffset = 0x90;
constexpr int kGr2DErrorOffset = 0x94;
constexpr int kD3DDeviceNotReset = static_cast<int>(0x88760869u);

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

using ApplySysOptFn = void(__thiscall*)(void*, void*, int);
using SysOptOnCreateFn = void(__thiscall*)(void*, void*);
using SysOptDestructorFn = void(__thiscall*)(void*);
using FindScreenModeFn = int(__thiscall*)(void*, void*, int, int, int, int);

static ApplySysOptFn gApplySysOpt = reinterpret_cast<ApplySysOptFn>(kApplySysOptAddress);
static SysOptOnCreateFn gSysOptOnCreate = reinterpret_cast<SysOptOnCreateFn>(kSysOptOnCreateAddress);
static SysOptDestructorFn gSysOptDestructor = reinterpret_cast<SysOptDestructorFn>(kSysOptDestructorAddress);
static FindScreenModeFn gFindScreenMode = nullptr;
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

inline void SaveDisplayConfig(int width, int height, bool fullscreen) {
    char widthText[16] = {};
    char heightText[16] = {};
    std::sprintf(widthText, "%d", width);
    std::sprintf(heightText, "%d", height);
    WritePrivateProfileStringA("GENERAL", "GameWidth", widthText, ConfigPath());
    WritePrivateProfileStringA("GENERAL", "GameHeight", heightText, ConfigPath());
    WritePrivateProfileStringA("GENERAL", "WindowedMode", fullscreen ? "false" : "true", ConfigPath());
}

inline int ResolutionIndexFor(int width, int height) {
    for (int i = 0; i < kResolutionCount; ++i) {
        if (kResolutions[i].width == width && kResolutions[i].height == height) return i;
    }
    return 2; // EverLeaf default: 1280x720
}

inline void* Gr2D() {
    __try {
        auto holder = reinterpret_cast<void**>(kGr2DGlobal);
        return holder ? *holder : nullptr;
    }
    __except (EXCEPTION_EXECUTE_HANDLER) {
        return nullptr;
    }
}

inline bool ReadFullscreen(bool& fullscreen) {
    void* gr = Gr2D();
    if (!gr) return false;
    __try {
        fullscreen = *reinterpret_cast<int*>(reinterpret_cast<unsigned char*>(gr) + kScreenModeOffset + kScreenModeFullscreenOffset) != 0;
        return true;
    }
    __except (EXCEPTION_EXECUTE_HANDLER) {
        return false;
    }
}

inline FindScreenModeFn LocateFindScreenMode() {
    if (gFindScreenMode) return gFindScreenMode;

    HMODULE module = GetModuleHandleA(nullptr);
    if (!module) return nullptr;
    auto base = reinterpret_cast<unsigned char*>(module);
    auto dos = reinterpret_cast<IMAGE_DOS_HEADER*>(base);
    if (dos->e_magic != IMAGE_DOS_SIGNATURE) return nullptr;
    auto nt = reinterpret_cast<IMAGE_NT_HEADERS*>(base + dos->e_lfanew);
    if (nt->Signature != IMAGE_NT_SIGNATURE) return nullptr;

    const unsigned char signature[] = { 0xB8, 0, 0, 0, 0, 0xE8, 0, 0, 0, 0, 0x83, 0xEC, 0x68 };
    const char mask[] = "x????x????xxx";
    const size_t sigSize = sizeof(signature);
    const size_t imageSize = nt->OptionalHeader.SizeOfImage;

    for (size_t i = 0; i + sigSize <= imageSize; ++i) {
        bool match = true;
        for (size_t j = 0; j < sigSize; ++j) {
            if (mask[j] == 'x' && base[i + j] != signature[j]) {
                match = false;
                break;
            }
        }
        if (match) {
            gFindScreenMode = reinterpret_cast<FindScreenModeFn>(base + i);
            return gFindScreenMode;
        }
    }
    return nullptr;
}

inline bool SetGr2DMode(int width, int height, bool fullscreen) {
    if (width <= 0 || height <= 0) return false;
    void* gr = Gr2D();
    FindScreenModeFn findScreenMode = LocateFindScreenMode();
    if (!gr || !findScreenMode) {
        CrashDiagnostics::LogEvent("Gr2D screen-mode contract unavailable");
        return false;
    }

    __try {
        unsigned char* bytes = reinterpret_cast<unsigned char*>(gr);
        const int initialized = *reinterpret_cast<int*>(bytes + kGr2DInitializedOffset);
        if (!initialized) return false;

        const int currentWidth = *reinterpret_cast<int*>(bytes + kScreenModeOffset + kScreenModeWidthOffset);
        const int currentHeight = *reinterpret_cast<int*>(bytes + kScreenModeOffset + kScreenModeHeightOffset);
        const bool currentFullscreen = *reinterpret_cast<int*>(bytes + kScreenModeOffset + kScreenModeFullscreenOffset) != 0;
        if (currentWidth == width && currentHeight == height && currentFullscreen == fullscreen) return true;

        unsigned char mode[kScreenModeSize] = {};
        if (!findScreenMode(gr, mode, fullscreen ? 1 : 0, width, height, 0)) {
            return false;
        }
        std::memcpy(bytes + kScreenModeOffset, mode, kScreenModeSize);
        *reinterpret_cast<int*>(bytes + kGr2DErrorOffset) = kD3DDeviceNotReset;
        return true;
    }
    __except (EXCEPTION_EXECUTE_HANDLER) {
        CrashDiagnostics::LogEvent("Gr2D screen-mode update raised an exception");
        return false;
    }
}

inline void ApplyClientResolutionConstants(int width, int height) {
    Client::m_nGameWidth = width;
    Client::m_nGameHeight = height;
    Client::UpdateResolution();
    WidescreenCorrections::ApplyCurrent();
}

inline bool ApplyResolution(int width, int height, bool fullscreen, bool persist) {
    const int previousWidth = Client::m_nGameWidth;
    const int previousHeight = Client::m_nGameHeight;
    const bool previousWindowed = Client::WindowedMode;

    ApplyClientResolutionConstants(width, height);
    if (!SetGr2DMode(width, height, fullscreen)) {
        ApplyClientResolutionConstants(previousWidth, previousHeight);
        Client::WindowedMode = previousWindowed;
        return false;
    }

    Client::WindowedMode = !fullscreen;
    if (persist) SaveDisplayConfig(width, height, fullscreen);
    return true;
}

inline int SelectedIndex() {
    if (gResolutionCombo && IsWindow(gResolutionCombo)) {
        const LRESULT selected = SendMessageA(gResolutionCombo, CB_GETCURSEL, 0, 0);
        if (selected >= 0 && selected < kResolutionCount) return static_cast<int>(selected);
    }
    return ResolutionIndexFor(Client::m_nGameWidth, Client::m_nGameHeight);
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
        int candidateWidth = *reinterpret_cast<int*>(reinterpret_cast<unsigned char*>(sysOpt) + 0x24);
        int candidateHeight = *reinterpret_cast<int*>(reinterpret_cast<unsigned char*>(sysOpt) + 0x28);
        if (candidateWidth >= 200 && candidateWidth <= 700) dialogWidth = candidateWidth;
        if (candidateHeight >= 300 && candidateHeight <= 600) dialogHeight = candidateHeight;
    }
    __except (EXCEPTION_EXECUTE_HANDLER) {
    }

    const int clientWidth = client.right - client.left;
    const int clientHeight = client.bottom - client.top;
    const int left = (clientWidth - dialogWidth) / 2;
    const int top = (clientHeight - dialogHeight) / 2;
    const int selectorX = left + 76;
    const int selectorY = top + 338;

    gResolutionLabel = CreateWindowExA(
        0, "STATIC", "Resolution", WS_CHILD | WS_VISIBLE,
        selectorX, selectorY - 18, 166, 18, parent, nullptr, GetModuleHandleA(nullptr), nullptr
    );
    gResolutionCombo = CreateWindowExA(
        WS_EX_CLIENTEDGE, "COMBOBOX", "",
        WS_CHILD | WS_VISIBLE | WS_TABSTOP | CBS_DROPDOWNLIST | WS_VSCROLL,
        selectorX, selectorY, 166, 150, parent, nullptr, GetModuleHandleA(nullptr), nullptr
    );
    if (!gResolutionCombo) {
        DestroySelector();
        return;
    }

    HFONT font = static_cast<HFONT>(GetStockObject(DEFAULT_GUI_FONT));
    if (gResolutionLabel) SendMessageA(gResolutionLabel, WM_SETFONT, reinterpret_cast<WPARAM>(font), TRUE);
    SendMessageA(gResolutionCombo, WM_SETFONT, reinterpret_cast<WPARAM>(font), TRUE);
    for (int i = 0; i < kResolutionCount; ++i) {
        SendMessageA(gResolutionCombo, CB_ADDSTRING, 0, reinterpret_cast<LPARAM>(kResolutions[i].label));
    }
    SendMessageA(gResolutionCombo, CB_SETCURSEL, ResolutionIndexFor(Client::m_nGameWidth, Client::m_nGameHeight), 0);
    SetWindowPos(gResolutionCombo, HWND_TOP, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE | SWP_SHOWWINDOW);
    if (gResolutionLabel) SetWindowPos(gResolutionLabel, HWND_TOP, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE | SWP_SHOWWINDOW);
}

inline void __fastcall ApplySysOptHook(void* self, void*, void* sysOpt, int applyVideo) {
    gApplySysOpt(self, sysOpt, applyVideo);
    if (!sysOpt || !applyVideo) return;

    const int index = SelectedIndex();
    bool fullscreen = !Client::WindowedMode;
    ReadFullscreen(fullscreen); // use Maple's freshly-applied fullscreen choice when available
    if (!ApplyResolution(kResolutions[index].width, kResolutions[index].height, fullscreen, true)) {
        MessageBoxW(FindGameWindow(), L"EverLeaf could not apply that display mode. The previous resolution was kept.", L"EverLeaf display settings", MB_OK | MB_ICONWARNING);
    }
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

    if (!detail::LocateFindScreenMode()) {
        CrashDiagnostics::LogEvent("FindScreenMode signature not found");
        return false;
    }

    // Make room for EverLeaf's resolution selector beneath the stock video options.
    Memory::WriteInt(detail::kSysOptButtonYOperand, detail::kSysOptButtonY);

    if (!Memory::SetHook(true, reinterpret_cast<void**>(&detail::gApplySysOpt), reinterpret_cast<void*>(detail::ApplySysOptHook))) return false;
    if (!Memory::SetHook(true, reinterpret_cast<void**>(&detail::gSysOptOnCreate), reinterpret_cast<void*>(detail::SysOptOnCreateHook))) return false;
    if (!Memory::SetHook(true, reinterpret_cast<void**>(&detail::gSysOptDestructor), reinterpret_cast<void*>(detail::SysOptDestructorHook))) return false;

    detail::gInstalled = true;
    CrashDiagnostics::LogEvent("runtime resolution selector hooks installed");
    std::cout << "EverLeaf Client v2: runtime resolution selector enabled" << std::endl;
    return true;
}

inline bool IsFullscreen() {
    bool fullscreen = !Client::WindowedMode;
    detail::ReadFullscreen(fullscreen);
    return fullscreen;
}

inline bool ToggleFullscreen() {
    const bool targetFullscreen = !IsFullscreen();
    const bool applied = detail::ApplyResolution(Client::m_nGameWidth, Client::m_nGameHeight, targetFullscreen, true);
    if (applied) {
        CrashDiagnostics::LogEvent(targetFullscreen ? "Alt+Enter fullscreen applied" : "Alt+Enter windowed mode applied");
    }
    return applied;
}

inline void Shutdown() {
    detail::DestroySelector();
}

} // namespace DisplayResolution
