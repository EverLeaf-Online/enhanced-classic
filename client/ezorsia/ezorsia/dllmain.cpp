// dllmain.cpp : EverLeaf v83 Client v2 proxy bootstrap.
#include "stdafx.h"
#include "ReplacementFuncs.h"
#include "dinput8.h"
#include "CrashDiagnostics.h"

#include <atomic>

namespace {
constexpr DWORD kClientUnpackTimeoutMs = 30000;
constexpr DWORD kClientBootstrapTimeoutMs = 45000;
constexpr DWORD kClientUnpackPollMs = 10;

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
    CrashDiagnostics::LogEvent("bootstrap failure dialog raised");
    MessageBoxW(nullptr, message, L"EverLeaf Client v2 startup error", MB_OK | MB_ICONERROR);
}

bool InstallEarlyHook(const char* name, bool (*hook)(bool), bool critical) {
    const bool installed = hook(true);
    if (!installed) {
        std::cout << "EverLeaf Client v2: failed to install early hook " << name << std::endl;
        CrashDiagnostics::LogEvent(name);
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

DWORD WINAPI BootstrapWatchdog(LPVOID) {
    if (!gBootstrapComplete) {
        return 0;
    }

    const DWORD result = WaitForSingleObject(gBootstrapComplete, kClientBootstrapTimeoutMs);
    if (result == WAIT_TIMEOUT && !gBootstrapFailed.load()) {
        CrashDiagnostics::SetPhase("bootstrap-watchdog-timeout");
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
    CrashDiagnostics::SetPhase("installing-client-hooks");

    bool hooksOk = true;
    const auto requiredHook = [&hooksOk](const char* name, bool result) {
        if (!result) {
            hooksOk = false;
            std::cout << "EverLeaf Client v2: hook failed: " << name << std::endl;
            CrashDiagnostics::LogEvent(name);
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
        CrashDiagnostics::SetPhase("client-hook-mismatch");
        FailBootstrap(
            L"EverLeaf detected a client hook mismatch.\n\n"
            L"Please repair/update the client before launching again. No live-server changes were made."
        );
        ExitProcess(ERROR_BAD_EXE_FORMAT);
    }

    CrashDiagnostics::SetPhase("applying-startup-patches");
    std::cout << "EverLeaf Client v2: applying startup routines" << std::endl;
    Client::UpdateGameStartup();

    CrashDiagnostics::SetPhase("applying-resolution-patches");
    std::cout << "EverLeaf Client v2: applying resolution "
              << Client::m_nGameWidth << "x" << Client::m_nGameHeight << std::endl;
    Client::UpdateResolution();

    if (Client::ModernLoginUI) {
        CrashDiagnostics::SetPhase("applying-login-ui");
        std::cout << "EverLeaf Client v2: applying modern login UI" << std::endl;
        Client::UpdateLogin();
    }

    CrashDiagnostics::SetPhase("initializing-dinput-proxy");
    dinput8::CreateHook();
    std::cout << "EverLeaf Client v2: dinput8 proxy hook initialized" << std::endl;
    CrashDiagnostics::SetPhase("client-hooks-ready");
}

DWORD WINAPI MainProc(LPVOID) {
    CrashDiagnostics::Install();
    CrashDiagnostics::SetPhase("installing-early-hooks");

    if (!InstallEarlyHooks()) {
        CrashDiagnostics::SetPhase("early-hook-failure");
        FailBootstrap(
            L"EverLeaf could not initialize the network/client compatibility layer.\n\n"
            L"Please repair/update the client and try again."
        );
        if (gBootstrapComplete) SetEvent(gBootstrapComplete);
        ExitProcess(ERROR_DLL_INIT_FAILED);
        return ERROR_DLL_INIT_FAILED;
    }

    CrashDiagnostics::SetPhase("waiting-for-v83-unpack");
    if (!WaitForClientImage()) {
        CrashDiagnostics::SetPhase("v83-unpack-mismatch");
        FailBootstrap(
            L"EverLeaf did not recognize the unpacked v83 client image.\n\n"
            L"This usually means the executable does not match the EverLeaf Client v2 baseline. "
            L"The client will close instead of hanging indefinitely."
        );
        if (gBootstrapComplete) SetEvent(gBootstrapComplete);
        ExitProcess(ERROR_BAD_EXE_FORMAT);
        return ERROR_BAD_EXE_FORMAT;
    }

    CrashDiagnostics::SetPhase("creating-client-runtime");
    MainMain::CreateInstance(MainFunc);
    CrashDiagnostics::SetPhase("bootstrap-complete");
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
