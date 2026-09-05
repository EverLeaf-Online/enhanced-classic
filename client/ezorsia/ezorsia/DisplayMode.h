#pragma once

#include "Client.h"
#include "INIReader.h"
#include "CrashDiagnostics.h"

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

    const int monitorWidth = monitorRect.right - monitorRect.left;
    const int monitorHeight = monitorRect.bottom - monitorRect.top;
    const int width = Client::m_nGameWidth;
    const int height = Client::m_nGameHeight;
    const bool monitorSized = width == monitorWidth && height == monitorHeight;
    const int x = monitorSized ? monitorRect.left : monitorRect.left + (monitorWidth - width) / 2;
    const int y = monitorSized ? monitorRect.top : monitorRect.top + (monitorHeight - height) / 2;

    SetWindowPos(
        window,
        HWND_TOP,
        x,
        y,
        width,
        height,
        SWP_NOOWNERZORDER | SWP_FRAMECHANGED | SWP_SHOWWINDOW
    );

    gBorderlessActive = true;
    CrashDiagnostics::LogEvent("borderless window applied");
    std::cout << "EverLeaf Client v2: borderless window applied at "
              << width << "x" << height
              << (monitorSized ? " (fullscreen)" : " (centered)")
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
        RestoreWindowedState(window);
        return;
    }

    // Preserve the player's current framed location before each transition so
    // later toggles return to the correct monitor and position.
    CaptureWindowedState(window);
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

