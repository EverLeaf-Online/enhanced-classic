#pragma once

#include "Client.h"
#include "INIReader.h"
#include "CrashDiagnostics.h"
#include "RuntimeResolution.h"
#include "ResolutionUIBounds.h"

namespace DisplayMode {
namespace detail {
constexpr DWORD kDisplayWindowTimeoutMs = 60000;
constexpr DWORD kDisplayWindowPollMs = 25;

static WNDPROC gOriginalWindowProc = nullptr;
static LONG_PTR gWindowedStyle = 0;
static LONG_PTR gWindowedExStyle = 0;
static RECT gWindowedRect = {};
static bool gHasWindowedState = false;
static bool gBorderlessActive = false;
static bool gMatchMonitorRenderer = true;
static bool gFullscreenRendererChanged = false;
static int gFramedRenderWidth = 0;
static int gFramedRenderHeight = 0;

inline HWND FindEverLeafGameWindow() {
    HWND window = FindWindowA("MapleStoryClass", nullptr);
    if (!window) {
        return nullptr;
    }

    DWORD windowProcess = 0;
    GetWindowThreadProcessId(window, &windowProcess);
    return windowProcess == GetCurrentProcessId() ? window : nullptr;
}

inline bool GetMonitorRectForWindow(HWND window, bool useWorkArea, RECT& result) {
    const HMONITOR monitor = MonitorFromWindow(window, MONITOR_DEFAULTTONEAREST);
    if (!monitor) {
        return false;
    }

    MONITORINFO info = {};
    info.cbSize = sizeof(info);
    if (!GetMonitorInfoW(monitor, &info)) {
        return false;
    }

    result = useWorkArea ? info.rcWork : info.rcMonitor;
    return true;
}

inline bool IsSupportedRendererSize(int width, int height) {
    return
        (width == 800 && height == 600) ||
        (width == 1024 && height == 768) ||
        (width == 1280 && height == 720) ||
        (width == 1366 && height == 768) ||
        (width == 1600 && height == 900) ||
        (width == 1920 && height == 1080);
}

inline bool CaptureWindowedState(HWND window) {
    if (!window) {
        return false;
    }

    RECT rect = {};
    if (!GetWindowRect(window, &rect)) {
        return false;
    }

    gWindowedStyle = GetWindowLongPtrA(window, GWL_STYLE);
    gWindowedExStyle = GetWindowLongPtrA(window, GWL_EXSTYLE);
    gWindowedRect = rect;
    gHasWindowedState = true;
    return true;
}

inline void CaptureFramedRendererState() {
    gFramedRenderWidth = Client::m_nGameWidth;
    gFramedRenderHeight = Client::m_nGameHeight;
    gFullscreenRendererChanged = false;
}

inline bool MatchRendererToMonitor(HWND window) {
    if (!window || !gMatchMonitorRenderer) {
        return false;
    }

    RECT monitorRect = {};
    if (!GetMonitorRectForWindow(window, false, monitorRect)) {
        return false;
    }

    const int width = monitorRect.right - monitorRect.left;
    const int height = monitorRect.bottom - monitorRect.top;
    if (!IsSupportedRendererSize(width, height)) {
        CrashDiagnostics::LogEvent("fullscreen monitor mode is outside EverLeaf supported resolution list");
        std::cout << "EverLeaf Client v2: keeping current renderer in fullscreen; monitor mode "
                  << width << "x" << height << " is not in the supported list" << std::endl;
        return false;
    }

    if (width == Client::m_nGameWidth && height == Client::m_nGameHeight) {
        return true;
    }

    if (!RuntimeResolution::Apply(width, height)) {
        CrashDiagnostics::LogEvent("fullscreen renderer match failed; using monitor-sized window only");
        return false;
    }

    ResolutionUIBounds::SetActiveResolution(width, height);
    gFullscreenRendererChanged = true;
    CrashDiagnostics::LogEvent("fullscreen renderer matched active monitor");
    std::cout << "EverLeaf Client v2: fullscreen renderer matched monitor at "
              << width << "x" << height << std::endl;
    return true;
}

inline void RestoreFramedRenderer() {
    if (!gFullscreenRendererChanged ||
        gFramedRenderWidth <= 0 ||
        gFramedRenderHeight <= 0) {
        return;
    }

    if (RuntimeResolution::Apply(gFramedRenderWidth, gFramedRenderHeight)) {
        ResolutionUIBounds::SetActiveResolution(gFramedRenderWidth, gFramedRenderHeight);
        CrashDiagnostics::LogEvent("framed renderer resolution restored");
        std::cout << "EverLeaf Client v2: restored framed renderer at "
                  << gFramedRenderWidth << "x" << gFramedRenderHeight << std::endl;
    }
    else {
        CrashDiagnostics::LogEvent("framed renderer resolution restore failed");
    }

    gFullscreenRendererChanged = false;
}

inline void ApplyBorderlessWindow(HWND window) {
    LONG_PTR style = GetWindowLongPtrA(window, GWL_STYLE);
    LONG_PTR exStyle = GetWindowLongPtrA(window, GWL_EXSTYLE);

    style &= ~(WS_CAPTION | WS_THICKFRAME | WS_MINIMIZEBOX | WS_MAXIMIZEBOX | WS_SYSMENU);
    style |= WS_POPUP;
    exStyle &= ~(WS_EX_DLGMODALFRAME | WS_EX_CLIENTEDGE | WS_EX_STATICEDGE | WS_EX_WINDOWEDGE);

    SetWindowLongPtrA(window, GWL_STYLE, style);
    SetWindowLongPtrA(window, GWL_EXSTYLE, exStyle);

    RECT monitorRect = {};
    if (!GetMonitorRectForWindow(window, false, monitorRect)) {
        monitorRect.left = 0;
        monitorRect.top = 0;
        monitorRect.right = GetSystemMetrics(SM_CXSCREEN);
        monitorRect.bottom = GetSystemMetrics(SM_CYSCREEN);
    }

    // Borderless fullscreen is a monitor-sized window regardless of Maple's
    // current render resolution. Phase 2 additionally tries to match the renderer
    // to the monitor when that exact mode is in EverLeaf's supported list.
    const int width = monitorRect.right - monitorRect.left;
    const int height = monitorRect.bottom - monitorRect.top;

    if (IsIconic(window)) {
        ShowWindow(window, SW_RESTORE);
    }

    SetWindowPos(
        window,
        HWND_TOP,
        monitorRect.left,
        monitorRect.top,
        width,
        height,
        SWP_NOOWNERZORDER | SWP_FRAMECHANGED | SWP_SHOWWINDOW
    );

    gBorderlessActive = true;
    CrashDiagnostics::LogEvent("borderless fullscreen window applied");
    std::cout << "EverLeaf Client v2: borderless fullscreen window applied at "
              << width << "x" << height
              << " (renderer " << Client::m_nGameWidth << "x" << Client::m_nGameHeight << ")"
              << std::endl;
}

inline bool RestoreWindowedState(HWND window) {
    if (!window || !gHasWindowedState) {
        return false;
    }

    SetWindowLongPtrA(window, GWL_STYLE, gWindowedStyle);
    SetWindowLongPtrA(window, GWL_EXSTYLE, gWindowedExStyle);

    const int width = gWindowedRect.right - gWindowedRect.left;
    const int height = gWindowedRect.bottom - gWindowedRect.top;
    SetWindowPos(
        window,
        nullptr,
        gWindowedRect.left,
        gWindowedRect.top,
        width,
        height,
        SWP_NOZORDER | SWP_NOOWNERZORDER | SWP_FRAMECHANGED | SWP_SHOWWINDOW
    );

    gBorderlessActive = false;
    CrashDiagnostics::LogEvent("framed window restored");
    std::cout << "EverLeaf Client v2: restored framed window" << std::endl;
    return true;
}

inline void CenterWindowedClient(HWND window) {
    const LONG_PTR style = GetWindowLongPtrA(window, GWL_STYLE);
    const LONG_PTR exStyle = GetWindowLongPtrA(window, GWL_EXSTYLE);

    RECT outer = { 0, 0, Client::m_nGameWidth, Client::m_nGameHeight };
    if (!AdjustWindowRectEx(&outer, static_cast<DWORD>(style), FALSE, static_cast<DWORD>(exStyle))) {
        return;
    }

    RECT work = {};
    if (!GetMonitorRectForWindow(window, true, work)) {
        SystemParametersInfoW(SPI_GETWORKAREA, 0, &work, 0);
    }

    const int width = outer.right - outer.left;
    const int height = outer.bottom - outer.top;
    const int workWidth = work.right - work.left;
    const int workHeight = work.bottom - work.top;
    const int x = work.left + (workWidth - width) / 2;
    const int y = work.top + (workHeight - height) / 2;

    SetWindowPos(
        window,
        nullptr,
        x,
        y,
        width,
        height,
        SWP_NOZORDER | SWP_NOOWNERZORDER | SWP_NOACTIVATE | SWP_FRAMECHANGED
    );

    std::cout << "EverLeaf Client v2: centered windowed client" << std::endl;
}

inline void ToggleBorderlessWindow(HWND window) {
    if (!window || !Client::WindowedMode) {
        return;
    }

    if (gBorderlessActive) {
        // Restore the pre-fullscreen renderer while the window is still WS_POPUP.
        // RuntimeResolution intentionally leaves popup geometry alone, then the
        // exact framed style/size/position captured on entry is restored below.
        RestoreFramedRenderer();
        RestoreWindowedState(window);
        return;
    }

    // Preserve both the player's current framed window and render resolution so
    // Alt+Enter is a reversible fullscreen transition rather than a style toggle.
    CaptureWindowedState(window);
    CaptureFramedRendererState();
    MatchRendererToMonitor(window);
    ApplyBorderlessWindow(window);
}

inline LRESULT CALLBACK EverLeafWindowProc(HWND window, UINT message, WPARAM wParam, LPARAM lParam) {
    const bool altEnter =
        message == WM_SYSKEYDOWN &&
        wParam == VK_RETURN &&
        (lParam & (1L << 29)) != 0 &&
        (lParam & (1L << 30)) == 0;

    if (altEnter) {
        ToggleBorderlessWindow(window);
        return 0;
    }

    if (message == WM_SYSCHAR && wParam == VK_RETURN) {
        return 0;
    }

    WNDPROC original = gOriginalWindowProc;
    if (!original) {
        return DefWindowProcA(window, message, wParam, lParam);
    }

    if (message == WM_NCDESTROY) {
        SetWindowLongPtrA(window, GWLP_WNDPROC, reinterpret_cast<LONG_PTR>(original));
        gOriginalWindowProc = nullptr;
    }

    return CallWindowProcA(original, window, message, wParam, lParam);
}

inline bool InstallAltEnterToggle(HWND window) {
    SetLastError(ERROR_SUCCESS);
    const LONG_PTR previous = SetWindowLongPtrA(
        window,
        GWLP_WNDPROC,
        reinterpret_cast<LONG_PTR>(EverLeafWindowProc)
    );
    if (previous == 0 && GetLastError() != ERROR_SUCCESS) {
        CrashDiagnostics::LogEvent("Alt+Enter display toggle install failed");
        std::cout << "EverLeaf Client v2: could not install Alt+Enter display toggle" << std::endl;
        return false;
    }

    gOriginalWindowProc = reinterpret_cast<WNDPROC>(previous);
    CrashDiagnostics::LogEvent("Alt+Enter display toggle enabled");
    std::cout << "EverLeaf Client v2: Alt+Enter display toggle enabled" << std::endl;
    return true;
}

inline DWORD WINAPI Worker(LPVOID) {
    INIReader displayConfig("config.ini");
    if (displayConfig.ParseError()) {
        CrashDiagnostics::LogEvent("display settings parse error");
        return ERROR_BAD_FORMAT;
    }

    const bool borderless = displayConfig.GetBoolean("general", "BorderlessWindow", false);
    const bool centerWindow = displayConfig.GetBoolean("general", "CenterWindow", true);
    const bool enableAltEnter = displayConfig.GetBoolean("general", "EnableAltEnterToggle", true);
    gMatchMonitorRenderer = displayConfig.GetBoolean(
        "general",
        "MatchMonitorResolutionOnFullscreen",
        true);

    if (!borderless && !centerWindow && !enableAltEnter) {
        return 0;
    }

    if (borderless && !Client::WindowedMode) {
        MessageBoxW(
            nullptr,
            L"BorderlessWindow requires WindowedMode=true. EverLeaf will leave the current display mode unchanged.",
            L"EverLeaf Client v2 display setting",
            MB_OK | MB_ICONWARNING
        );
        return ERROR_INVALID_PARAMETER;
    }

    const ULONGLONG started = GetTickCount64();
    while (GetTickCount64() - started < kDisplayWindowTimeoutMs) {
        HWND window = FindEverLeafGameWindow();
        if (window) {
            if (centerWindow) {
                CenterWindowedClient(window);
            }
            CaptureWindowedState(window);

            if (borderless) {
                CaptureFramedRendererState();
                MatchRendererToMonitor(window);
                ApplyBorderlessWindow(window);
            }
            else {
                gBorderlessActive = false;
            }

            if (enableAltEnter && Client::WindowedMode) {
                InstallAltEnterToggle(window);
            }
            return 0;
        }
        Sleep(kDisplayWindowPollMs);
    }

    CrashDiagnostics::LogEvent("display worker window timeout");
    std::cout << "EverLeaf Client v2: display worker did not find MapleStoryClass before timeout" << std::endl;
    return WAIT_TIMEOUT;
}

} // namespace detail

inline void EnableSystemDpiAwareness() {
    using SetProcessDPIAwareFn = BOOL(WINAPI*)();
    HMODULE user32 = GetModuleHandleW(L"user32.dll");
    if (!user32) {
        return;
    }

    auto setProcessDpiAware = reinterpret_cast<SetProcessDPIAwareFn>(
        GetProcAddress(user32, "SetProcessDPIAware")
    );
    if (setProcessDpiAware && setProcessDpiAware()) {
        CrashDiagnostics::LogEvent("system DPI awareness enabled");
        std::cout << "EverLeaf Client v2: system DPI awareness enabled" << std::endl;
    }
}

inline void StartWorker() {
    HANDLE thread = CreateThread(nullptr, 0, detail::Worker, nullptr, 0, nullptr);
    if (thread) {
        CloseHandle(thread);
    }
    else {
        CrashDiagnostics::LogEvent("display worker thread creation failed");
    }
}

} // namespace DisplayMode
