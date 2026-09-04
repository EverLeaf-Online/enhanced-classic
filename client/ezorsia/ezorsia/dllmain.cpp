// dllmain.cpp : EverLeaf v83 Client v2 proxy bootstrap.
#include "stdafx.h"
#include "ReplacementFuncs.h"
#include "dinput8.h"
#include "INIReader.h"

#include <atomic>

namespace {
constexpr DWORD kClientUnpackTimeoutMs = 30000;
constexpr DWORD kClientBootstrapTimeoutMs = 45000;
constexpr DWORD kClientUnpackPollMs = 10;
constexpr DWORD kDisplayWindowTimeoutMs = 60000;
constexpr DWORD kDisplayWindowPollMs = 25;

HANDLE gBootstrapComplete = nullptr;
std::atomic<bool> gBootstrapFailed{ false };

struct ClientSignature {
    DWORD address;
    BYTE expected;
    const char* name;
};

// Stable entry bytes from EverLeaf's pinned GMS v83 client after its protected
// image has unpacked. Checking several independent owners is safer than letting
// one individual hook wait forever on a single byte.
const ClientSignature kUnpackSignatures[] = {
    { 0x0044E88E, 0x55, "MyGetProcAddress" },
    { 0x009F5239, 0xB8, "CWvsApp::SetUp" },
    { 0x009F7159, 0xB8, "CWvsApp::InitializeResMan" },
};

bool ReadClientByte(DWORD address, BYTE& value) {
    __try {
        value = ReadValue<BYTE>(address);
        return true;
    }
    __except (EXCEPTION_EXECUTE_HANDLER) {
        return false;
    }
}

bool WaitForClientImage() {
    const ULONGLONG started = GetTickCount64();
    while (GetTickCount64() - started < kClientUnpackTimeoutMs) {
        bool ready = true;
        for (const auto& signature : kUnpackSignatures) {
            BYTE current = 0;
            if (!ReadClientByte(signature.address, current) || current != signature.expected) {
                ready = false;
                break;
            }
        }
        if (ready) {
            return true;
        }
        Sleep(kClientUnpackPollMs);
    }
    return false;
}

void FailBootstrap(const wchar_t* message) {
    bool expected = false;
    if (!gBootstrapFailed.compare_exchange_strong(expected, true)) {
        return;
    }
    MessageBoxW(nullptr, message, L"EverLeaf Client v2 startup error", MB_OK | MB_ICONERROR);
}

bool InstallEarlyHook(const char* name, bool (*hook)(bool), bool critical) {
    const bool installed = hook(true);
    if (!installed) {
        std::cout << "EverLeaf Client v2: failed to install early hook " << name << std::endl;
        if (critical) {
            return false;
        }
    }
    return true;
}

bool InstallEarlyHooks() {
    // Detours transactions are deliberately installed on the bootstrap worker
    // instead of inside DllMain, avoiding transaction/loader-sensitive work
    // while the Windows loader lock is held.
    if (!InstallEarlyHook("CreateMutexA", Hook_CreateMutexA, false)) return false;
    if (!InstallEarlyHook("WSPStartup", Hook_WSPStartup, true)) return false;
    if (!InstallEarlyHook("CreateWindowExA", Hook_CreateWindowExA, false)) return false;
    if (!InstallEarlyHook("FindFirstFileA", Hook_FindFirstFileA, false)) return false;
    if (!InstallEarlyHook("GetACP", Hook_GetACP, false)) return false;
    if (!InstallEarlyHook("GetModuleFileNameW", Hook_GetModuleFileNameW, false)) return false;
    return true;
}

HWND FindEverLeafGameWindow() {
    HWND window = FindWindowA("MapleStoryClass", nullptr);
    if (!window) {
        return nullptr;
    }

    DWORD windowProcess = 0;
    GetWindowThreadProcessId(window, &windowProcess);
    return windowProcess == GetCurrentProcessId() ? window : nullptr;
}

bool GetMonitorRectForWindow(HWND window, bool useWorkArea, RECT& result) {
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

void ApplyBorderlessWindow(HWND window) {
    LONG_PTR style = GetWindowLongPtrW(window, GWL_STYLE);
    LONG_PTR exStyle = GetWindowLongPtrW(window, GWL_EXSTYLE);

    style &= ~(WS_CAPTION | WS_THICKFRAME | WS_MINIMIZEBOX | WS_MAXIMIZEBOX | WS_SYSMENU);
    style |= WS_POPUP;
    exStyle &= ~(WS_EX_DLGMODALFRAME | WS_EX_CLIENTEDGE | WS_EX_STATICEDGE | WS_EX_WINDOWEDGE);

    SetWindowLongPtrW(window, GWL_STYLE, style);
    SetWindowLongPtrW(window, GWL_EXSTYLE, exStyle);

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

    std::cout << "EverLeaf Client v2: borderless window applied at "
              << width << "x" << height
              << (monitorSized ? " (fullscreen)" : " (centered)")
              << std::endl;
}

void CenterWindowedClient(HWND window) {
    LONG_PTR style = GetWindowLongPtrW(window, GWL_STYLE);
    LONG_PTR exStyle = GetWindowLongPtrW(window, GWL_EXSTYLE);

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

DWORD WINAPI DisplayModeWorker(LPVOID) {
    INIReader displayConfig("config.ini");
    if (displayConfig.ParseError()) {
        return ERROR_BAD_FORMAT;
    }

    const bool borderless = displayConfig.GetBoolean("general", "BorderlessWindow", false);
    const bool centerWindow = displayConfig.GetBoolean("general", "CenterWindow", true);
    if (!borderless && !centerWindow) {
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
            if (borderless) {
                ApplyBorderlessWindow(window);
            }
            else if (centerWindow) {
                CenterWindowedClient(window);
            }
            return 0;
        }
        Sleep(kDisplayWindowPollMs);
    }

    // Display polish is deliberately non-fatal. The bootstrap watchdog handles
    // actual client initialization failures; a missing/late HWND should not stop
    // an otherwise playable client.
    std::cout << "EverLeaf Client v2: display worker did not find MapleStoryClass before timeout" << std::endl;
    return WAIT_TIMEOUT;
}

void StartDisplayModeWorker() {
    HANDLE thread = CreateThread(nullptr, 0, DisplayModeWorker, nullptr, 0, nullptr);
    if (thread) {
        CloseHandle(thread);
    }
}

DWORD WINAPI BootstrapWatchdog(LPVOID) {
    if (!gBootstrapComplete) {
        return 0;
    }

    const DWORD result = WaitForSingleObject(gBootstrapComplete, kClientBootstrapTimeoutMs);
    if (result == WAIT_TIMEOUT && !gBootstrapFailed.load()) {
        FailBootstrap(
            L"EverLeaf could not finish initializing the v83 client.\n\n"
            L"The client build or unpacked memory layout did not match the expected EverLeaf baseline. "
            L"The game will close instead of remaining stuck on startup."
        );
        ExitProcess(ERROR_TIMEOUT);
    }
    return 0;
}
} // namespace

// Executed only after the pinned v83 image has reached its expected unpacked
// state. Function-level installers still retain their legacy readiness checks,
// but Client v2 preflight prevents normal startup from entering them early.
void MainFunc() {
    bool hooksOk = true;
    const auto requiredHook = [&hooksOk](const char* name, bool result) {
        if (!result) {
            hooksOk = false;
            std::cout << "EverLeaf Client v2: hook failed: " << name << std::endl;
        }
    };

    // Inherited pass-through/tracking replacements are intentionally omitted.
    // Most importantly, Client v2 leaves CWvsApp::Run on the stock v83 code path.
    // The inherited rewrite incorrectly gated Maple's positive Patch/Disconnect/
    // Terminate Z-exception codes with FAILED(HRESULT), preventing native dispatch.
    // Keeping stock Run restores the correct v83 exception semantics while calls
    // to separately hooked functions such as CallUpdate remain detoured normally.
    requiredHook("CClientSocket::Connect(context)", Hook_sub_494CA3(true));
    requiredHook("CClientSocket::Connect(prep)", Hook_sub_494D07(true));
    requiredHook("CClientSocket::Connect(sockaddr)", Hook_sub_494D2F(true));
    requiredHook("CRC update", Hook_sub_9F4E54(true));
    requiredHook("CWvsApp::ctor", Hook_sub_9F4FDA(true));
    requiredHook("CWvsApp::SetUp", Hook_sub_9F5239(true));
    requiredHook("CWvsApp::InitializeInput", Hook_sub_9F7CE1(true));
    requiredHook("CWvsApp::CallUpdate", Hook_sub_9F84D0(true));
    requiredHook("Dir_BackSlashToSlash", HookCWvsApp__Dir_BackSlashToSlash(true));
    requiredHook("IWzFileSystem::Init", Hook_sub_9F7964(true));
    requiredHook("CWvsApp::InitializeResMan", Hook_sub_9F7159(true));
    requiredHook("StringPool::GetString", Hook_StringPool__GetString(true));
    requiredHook("NEXTLEVEL table", Hook_sub_78C8A6(true));
    requiredHook("IWzNameSpace::Getitem", Hook_sub_5D995B(true));

    if (!hooksOk) {
        FailBootstrap(
            L"EverLeaf detected a client hook mismatch.\n\n"
            L"Please repair/update the client before launching again. No live-server changes were made."
        );
        ExitProcess(ERROR_BAD_EXE_FORMAT);
    }

    std::cout << "EverLeaf Client v2: applying startup routines" << std::endl;
    Client::UpdateGameStartup();

    std::cout << "EverLeaf Client v2: applying resolution "
              << Client::m_nGameWidth << "x" << Client::m_nGameHeight << std::endl;
    Client::UpdateResolution();

    if (Client::ModernLoginUI) {
        std::cout << "EverLeaf Client v2: applying modern login UI" << std::endl;
        Client::UpdateLogin();
    }

    dinput8::CreateHook();
    std::cout << "EverLeaf Client v2: dinput8 proxy hook initialized" << std::endl;
}

DWORD WINAPI MainProc(LPVOID) {
    if (!InstallEarlyHooks()) {
        FailBootstrap(
            L"EverLeaf could not initialize the network/client compatibility layer.\n\n"
            L"Please repair/update the client and try again."
        );
        if (gBootstrapComplete) SetEvent(gBootstrapComplete);
        ExitProcess(ERROR_DLL_INIT_FAILED);
        return ERROR_DLL_INIT_FAILED;
    }

    if (!WaitForClientImage()) {
        FailBootstrap(
            L"EverLeaf did not recognize the unpacked v83 client image.\n\n"
            L"This usually means the executable does not match the EverLeaf Client v2 baseline. "
            L"The client will close instead of hanging indefinitely."
        );
        if (gBootstrapComplete) SetEvent(gBootstrapComplete);
        ExitProcess(ERROR_BAD_EXE_FORMAT);
        return ERROR_BAD_EXE_FORMAT;
    }

    MainMain::CreateInstance(MainFunc);
    StartDisplayModeWorker();
    if (gBootstrapComplete) SetEvent(gBootstrapComplete);
    return 0;
}

// DllMain stays intentionally small. In particular, Detours transactions,
// client memory patching, network provider work, and singleton destruction are
// not performed while the loader lock is held.
BOOL APIENTRY DllMain(HMODULE hModule, DWORD ul_reason_for_call, LPVOID lpReserved) {
    switch (ul_reason_for_call) {
    case DLL_PROCESS_ATTACH: {
        DisableThreadLibraryCalls(hModule);

        // Capture a handle to MapleStory's loader/main thread for the legacy
        // resource bootstrap code that briefly suspends it while generating
        // missing config/UI resources.
        MainMain::mainTHread = OpenThread(
            THREAD_SUSPEND_RESUME | THREAD_QUERY_INFORMATION,
            FALSE,
            GetCurrentThreadId()
        );

        gBootstrapComplete = CreateEventW(nullptr, TRUE, FALSE, nullptr);
        HANDLE bootstrap = CreateThread(nullptr, 0, MainProc, nullptr, 0, nullptr);
        if (!bootstrap) {
            return FALSE;
        }
        CloseHandle(bootstrap);

        HANDLE watchdog = CreateThread(nullptr, 0, BootstrapWatchdog, nullptr, 0, nullptr);
        if (watchdog) {
            CloseHandle(watchdog);
        }
        break;
    }
    case DLL_PROCESS_DETACH:
        // Do not manually invoke MainMain's destructor here. Process teardown
        // already reclaims these resources, and provider/destructor work during
        // loader-lock teardown was a known crash/null-dereference risk.
        if (lpReserved == nullptr && gBootstrapComplete) {
            CloseHandle(gBootstrapComplete);
            gBootstrapComplete = nullptr;
        }
        if (lpReserved == nullptr && MainMain::mainTHread) {
            CloseHandle(MainMain::mainTHread);
            MainMain::mainTHread = nullptr;
        }
        break;
    default:
        break;
    }
    return TRUE;
}
