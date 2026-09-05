#include "stdafx.h"
#include "CrashDiagnostics.h"
#include "Client.h"

#include <DbgHelp.h>
#include <atomic>
#include <cstdint>

namespace {
constexpr wchar_t kDiagnosticsFileName[] = L"EverLeafClient.log";
constexpr wchar_t kCrashDumpFileName[] = L"EverLeafCrash.dmp";
constexpr wchar_t kFreezeReportFileName[] = L"EverLeafFreeze.txt";
constexpr DWORD kFreezeProbeIntervalMs = 5000;
constexpr UINT kFreezeProbeTimeoutMs = 1500;
constexpr int kFreezeTimeoutThreshold = 3;

wchar_t gDiagnosticsPath[MAX_PATH] = L"EverLeafClient.log";
wchar_t gCrashDumpPath[MAX_PATH] = L"EverLeafCrash.dmp";
wchar_t gFreezeReportPath[MAX_PATH] = L"EverLeafFreeze.txt";
std::atomic<const char*> gCurrentPhase{ "not-installed" };
std::atomic<bool> gFreezeWatchdogStarted{ false };
LPTOP_LEVEL_EXCEPTION_FILTER gPreviousExceptionFilter = nullptr;
HMODULE gDbgHelpModule = nullptr;

using MiniDumpWriteDump_t = BOOL (WINAPI *)(
    HANDLE,
    DWORD,
    HANDLE,
    MINIDUMP_TYPE,
    PMINIDUMP_EXCEPTION_INFORMATION,
    PMINIDUMP_USER_STREAM_INFORMATION,
    PMINIDUMP_CALLBACK_INFORMATION);
MiniDumpWriteDump_t gMiniDumpWriteDump = nullptr;

bool ResolveSiblingPath(const wchar_t* fileName, wchar_t (&destination)[MAX_PATH]) {
    wchar_t executablePath[MAX_PATH] = {};
    const DWORD length = GetModuleFileNameW(nullptr, executablePath, MAX_PATH);
    if (!length || length >= MAX_PATH) {
        return false;
    }

    wchar_t* slash = wcsrchr(executablePath, L'\\');
    wchar_t* forwardSlash = wcsrchr(executablePath, L'/');
    if (forwardSlash && (!slash || forwardSlash > slash)) {
        slash = forwardSlash;
    }
    if (!slash) {
        return false;
    }

    *(slash + 1) = L'\0';
    if (wcscat_s(executablePath, MAX_PATH, fileName) != 0) {
        return false;
    }

    return wcsncpy_s(destination, MAX_PATH, executablePath, _TRUNCATE) == 0;
}

void ResolveDiagnosticsPaths() {
    ResolveSiblingPath(kDiagnosticsFileName, gDiagnosticsPath);
    ResolveSiblingPath(kCrashDumpFileName, gCrashDumpPath);
    ResolveSiblingPath(kFreezeReportFileName, gFreezeReportPath);
}

void AppendRaw(const char* text) {
    if (!text || !*text) {
        return;
    }

    HANDLE file = CreateFileW(
        gDiagnosticsPath,
        FILE_APPEND_DATA,
        FILE_SHARE_READ | FILE_SHARE_WRITE,
        nullptr,
        OPEN_ALWAYS,
        FILE_ATTRIBUTE_NORMAL,
        nullptr
    );
    if (file == INVALID_HANDLE_VALUE) {
        return;
    }

    DWORD written = 0;
    WriteFile(file, text, static_cast<DWORD>(strlen(text)), &written, nullptr);
    FlushFileBuffers(file);
    CloseHandle(file);
}

void AppendTimestamped(const char* kind, const char* text) {
    SYSTEMTIME now = {};
    GetLocalTime(&now);

    char line[1024] = {};
    sprintf_s(
        line,
        "%04u-%02u-%02u %02u:%02u:%02u.%03u [%s] %s\r\n",
        now.wYear,
        now.wMonth,
        now.wDay,
        now.wHour,
        now.wMinute,
        now.wSecond,
        now.wMilliseconds,
        kind ? kind : "INFO",
        text ? text : ""
    );
    AppendRaw(line);
}

bool ResolveMiniDumpWriter() {
    if (gMiniDumpWriteDump) {
        return true;
    }

    wchar_t systemDirectory[MAX_PATH] = {};
    const UINT systemLength = GetSystemDirectoryW(systemDirectory, MAX_PATH);
    if (!systemLength || systemLength >= MAX_PATH) {
        return false;
    }
    if (wcscat_s(systemDirectory, MAX_PATH, L"\\dbghelp.dll") != 0) {
        return false;
    }

    // Load the Windows system copy explicitly. Never resolve dbghelp.dll through
    // the game directory, where stale or wrong-architecture copies may exist.
    gDbgHelpModule = LoadLibraryW(systemDirectory);
    if (!gDbgHelpModule) {
        return false;
    }

    gMiniDumpWriteDump = reinterpret_cast<MiniDumpWriteDump_t>(
        GetProcAddress(gDbgHelpModule, "MiniDumpWriteDump"));
    return gMiniDumpWriteDump != nullptr;
}

bool WriteLocalMiniDump(EXCEPTION_POINTERS* exceptionInfo) {
    if (!exceptionInfo || !gMiniDumpWriteDump) {
        return false;
    }

    HANDLE dump = CreateFileW(
        gCrashDumpPath,
        GENERIC_WRITE,
        FILE_SHARE_READ,
        nullptr,
        CREATE_ALWAYS,
        FILE_ATTRIBUTE_NORMAL,
        nullptr
    );
    if (dump == INVALID_HANDLE_VALUE) {
        return false;
    }

    MINIDUMP_EXCEPTION_INFORMATION exception = {};
    exception.ThreadId = GetCurrentThreadId();
    exception.ExceptionPointers = exceptionInfo;
    exception.ClientPointers = FALSE;

    // Keep the dump deliberately bounded/privacy-conscious: normal process
    // crash context plus thread metadata, never a full-memory dump.
    const auto dumpType = static_cast<MINIDUMP_TYPE>(
        MiniDumpNormal | MiniDumpWithThreadInfo);
    const BOOL success = gMiniDumpWriteDump(
        GetCurrentProcess(),
        GetCurrentProcessId(),
        dump,
        dumpType,
        &exception,
        nullptr,
        nullptr);

    FlushFileBuffers(dump);
    CloseHandle(dump);
    return success == TRUE;
}

struct WindowSearch {
    DWORD processId;
    HWND gameWindow;
};

BOOL CALLBACK FindEverLeafWindowCallback(HWND window, LPARAM param) {
    auto* search = reinterpret_cast<WindowSearch*>(param);
    if (!search) {
        return FALSE;
    }

    DWORD processId = 0;
    GetWindowThreadProcessId(window, &processId);
    if (processId != search->processId) {
        return TRUE;
    }

    char className[64] = {};
    if (!GetClassNameA(window, className, static_cast<int>(sizeof(className)))) {
        return TRUE;
    }
    if (strcmp(className, "MapleStoryClass") != 0) {
        return TRUE;
    }

    search->gameWindow = window;
    return FALSE;
}

HWND FindEverLeafGameWindow() {
    WindowSearch search = { GetCurrentProcessId(), nullptr };
    EnumWindows(FindEverLeafWindowCallback, reinterpret_cast<LPARAM>(&search));
    return search.gameWindow;
}

void WriteFreezeReport(HWND gameWindow, int consecutiveTimeouts) {
    HANDLE report = CreateFileW(
        gFreezeReportPath,
        GENERIC_WRITE,
        FILE_SHARE_READ,
        nullptr,
        CREATE_ALWAYS,
        FILE_ATTRIBUTE_NORMAL,
        nullptr
    );
    if (report == INVALID_HANDLE_VALUE) {
        return;
    }

    SYSTEMTIME now = {};
    GetLocalTime(&now);
    DWORD windowProcessId = 0;
    const DWORD windowThreadId = GetWindowThreadProcessId(gameWindow, &windowProcessId);
    const char* phase = gCurrentPhase.load(std::memory_order_relaxed);

    char text[1536] = {};
    sprintf_s(
        text,
        "EverLeaf Client v2 local freeze evidence\r\n"
        "No account, character, chat, or telemetry data is recorded or uploaded.\r\n"
        "time=%04u-%02u-%02u %02u:%02u:%02u.%03u\r\n"
        "phase=%s\r\n"
        "pid=%lu window_tid=%lu\r\n"
        "resolution=%dx%d windowed=%s\r\n"
        "consecutive_window_timeouts=%d probe_timeout_ms=%u\r\n",
        now.wYear,
        now.wMonth,
        now.wDay,
        now.wHour,
        now.wMinute,
        now.wSecond,
        now.wMilliseconds,
        phase ? phase : "unknown",
        GetCurrentProcessId(),
        windowThreadId,
        Client::m_nGameWidth,
        Client::m_nGameHeight,
        Client::WindowedMode ? "true" : "false",
        consecutiveTimeouts,
        kFreezeProbeTimeoutMs);

    DWORD written = 0;
    WriteFile(report, text, static_cast<DWORD>(strlen(text)), &written, nullptr);
    FlushFileBuffers(report);
    CloseHandle(report);
}

DWORD WINAPI FreezeWatchdogThread(void*) {
    int consecutiveTimeouts = 0;
    bool reportedCurrentFreeze = false;

    for (;;) {
        Sleep(kFreezeProbeIntervalMs);

        HWND gameWindow = FindEverLeafGameWindow();
        if (!gameWindow || !IsWindow(gameWindow)) {
            consecutiveTimeouts = 0;
            reportedCurrentFreeze = false;
            continue;
        }

        DWORD_PTR ignoredResult = 0;
        SetLastError(ERROR_SUCCESS);
        const LRESULT responsive = SendMessageTimeoutW(
            gameWindow,
            WM_NULL,
            0,
            0,
            SMTO_ABORTIFHUNG | SMTO_BLOCK,
            kFreezeProbeTimeoutMs,
            &ignoredResult);

        if (responsive != 0 || GetLastError() != ERROR_TIMEOUT) {
            if (reportedCurrentFreeze) {
                AppendTimestamped("FREEZE", "window responsiveness recovered");
            }
            consecutiveTimeouts = 0;
            reportedCurrentFreeze = false;
            continue;
        }

        ++consecutiveTimeouts;
        if (consecutiveTimeouts < kFreezeTimeoutThreshold || reportedCurrentFreeze) {
            continue;
        }

        WriteFreezeReport(gameWindow, consecutiveTimeouts);
        AppendTimestamped(
            "FREEZE",
            "EverLeaf window timed out on three bounded probes; local EverLeafFreeze.txt overwritten");
        reportedCurrentFreeze = true;
    }
}

void StartFreezeWatchdog() {
    bool expected = false;
    if (!gFreezeWatchdogStarted.compare_exchange_strong(expected, true)) {
        return;
    }

    HANDLE thread = CreateThread(nullptr, 0, FreezeWatchdogThread, nullptr, 0, nullptr);
    if (!thread) {
        gFreezeWatchdogStarted.store(false, std::memory_order_relaxed);
        AppendTimestamped("START", "freeze watchdog could not start");
        return;
    }
    CloseHandle(thread);
    AppendTimestamped("START", "bounded window-responsiveness freeze watchdog started");
}

LONG WINAPI EverLeafUnhandledExceptionFilter(EXCEPTION_POINTERS* exceptionInfo) {
    const char* phase = gCurrentPhase.load(std::memory_order_relaxed);
    const DWORD code = exceptionInfo && exceptionInfo->ExceptionRecord
        ? exceptionInfo->ExceptionRecord->ExceptionCode
        : 0;
    const uintptr_t address = exceptionInfo && exceptionInfo->ExceptionRecord
        ? reinterpret_cast<uintptr_t>(exceptionInfo->ExceptionRecord->ExceptionAddress)
        : 0;
    const uintptr_t imageBase = reinterpret_cast<uintptr_t>(GetModuleHandleW(nullptr));
    const uintptr_t imageOffset = address >= imageBase ? address - imageBase : 0;

    char details[1536] = {};
#ifdef _M_IX86
    const DWORD eip = exceptionInfo && exceptionInfo->ContextRecord
        ? exceptionInfo->ContextRecord->Eip
        : 0;
    const DWORD esp = exceptionInfo && exceptionInfo->ContextRecord
        ? exceptionInfo->ContextRecord->Esp
        : 0;
    const DWORD ebp = exceptionInfo && exceptionInfo->ContextRecord
        ? exceptionInfo->ContextRecord->Ebp
        : 0;
    sprintf_s(
        details,
        "unhandled exception code=0x%08lX address=0x%08llX exe+0x%08llX "
        "phase=%s pid=%lu tid=%lu resolution=%dx%d windowed=%s "
        "EIP=0x%08lX ESP=0x%08lX EBP=0x%08lX",
        code,
        static_cast<unsigned long long>(address),
        static_cast<unsigned long long>(imageOffset),
        phase ? phase : "unknown",
        GetCurrentProcessId(),
        GetCurrentThreadId(),
        Client::m_nGameWidth,
        Client::m_nGameHeight,
        Client::WindowedMode ? "true" : "false",
        eip,
        esp,
        ebp
    );
#else
    sprintf_s(
        details,
        "unhandled exception code=0x%08lX address=0x%016llX exe+0x%016llX "
        "phase=%s pid=%lu tid=%lu resolution=%dx%d windowed=%s",
        code,
        static_cast<unsigned long long>(address),
        static_cast<unsigned long long>(imageOffset),
        phase ? phase : "unknown",
        GetCurrentProcessId(),
        GetCurrentThreadId(),
        Client::m_nGameWidth,
        Client::m_nGameHeight,
        Client::WindowedMode ? "true" : "false"
    );
#endif

    AppendTimestamped("CRASH", details);
    AppendTimestamped(
        "CRASH",
        WriteLocalMiniDump(exceptionInfo)
            ? "local minidump written to EverLeafCrash.dmp"
            : "local minidump unavailable; text crash record retained");

    // We are an observer, not a replacement crash policy. Preserve any filter
    // Maple/the runtime installed before Client v2 diagnostics, and otherwise
    // let normal Windows unhandled-exception processing continue.
    if (gPreviousExceptionFilter && gPreviousExceptionFilter != EverLeafUnhandledExceptionFilter) {
        return gPreviousExceptionFilter(exceptionInfo);
    }
    return EXCEPTION_CONTINUE_SEARCH;
}
}

void CrashDiagnostics::Install() {
    ResolveDiagnosticsPaths();

    HANDLE file = CreateFileW(
        gDiagnosticsPath,
        GENERIC_WRITE,
        FILE_SHARE_READ | FILE_SHARE_WRITE,
        nullptr,
        CREATE_ALWAYS,
        FILE_ATTRIBUTE_NORMAL,
        nullptr
    );
    if (file != INVALID_HANDLE_VALUE) {
        const char header[] =
            "EverLeaf Client v2 local diagnostics\r\n"
            "No account, character, chat, or telemetry data is intentionally recorded or uploaded.\r\n"
            "On an unhandled crash, one bounded EverLeafCrash.dmp may be overwritten locally; it is never transmitted automatically.\r\n"
            "If the game window repeatedly stops responding, one bounded EverLeafFreeze.txt may be overwritten locally.\r\n";
        DWORD written = 0;
        WriteFile(file, header, static_cast<DWORD>(sizeof(header) - 1), &written, nullptr);
        FlushFileBuffers(file);
        CloseHandle(file);
    }

    const bool dumpWriterReady = ResolveMiniDumpWriter();
    gCurrentPhase.store("diagnostics-installed", std::memory_order_relaxed);
    gPreviousExceptionFilter = SetUnhandledExceptionFilter(EverLeafUnhandledExceptionFilter);
    AppendTimestamped("START", "client diagnostics installed");
    AppendTimestamped(
        "START",
        dumpWriterReady
            ? "system dbghelp MiniDumpWriteDump ready; local bounded crash dump enabled"
            : "system dbghelp MiniDumpWriteDump unavailable; text crash diagnostics remain enabled");
    StartFreezeWatchdog();
}

void CrashDiagnostics::SetPhase(const char* phase) {
    if (!phase || !*phase) {
        return;
    }
    gCurrentPhase.store(phase, std::memory_order_relaxed);

    char eventText[256] = {};
    sprintf_s(eventText, "phase=%s", phase);
    AppendTimestamped("PHASE", eventText);
}

void CrashDiagnostics::LogEvent(const char* eventText) {
    AppendTimestamped("INFO", eventText);
}
