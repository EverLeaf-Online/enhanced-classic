#include "pch.h"
#include "hook.h"

#include <dbghelp.h>
#include <atomic>
#include <cstdio>
#include <string>

namespace {
std::atomic<bool> g_watchdogStarted{false};
LPTOP_LEVEL_EXCEPTION_FILTER g_previousFilter = nullptr;

std::string ClientPath(const char* leaf) {
    char modulePath[MAX_PATH]{};
    GetModuleFileNameA(nullptr, modulePath, MAX_PATH);
    std::string path(modulePath);
    const auto slash = path.find_last_of("\\/");
    if (slash != std::string::npos) path.resize(slash + 1);
    else path.clear();
    path += leaf;
    return path;
}

void AppendLine(const char* message) {
    const std::string path = ClientPath("EverLeafClient.log");
    FILE* file = nullptr;
    fopen_s(&file, path.c_str(), "a");
    if (!file) return;
    SYSTEMTIME now{};
    GetLocalTime(&now);
    fprintf(file, "%04u-%02u-%02u %02u:%02u:%02u.%03u %s\n",
            now.wYear, now.wMonth, now.wDay,
            now.wHour, now.wMinute, now.wSecond, now.wMilliseconds,
            message ? message : "");
    fclose(file);
}

void WriteMiniDump(EXCEPTION_POINTERS* exceptionPointers) {
    HMODULE dbghelp = LoadLibraryA("dbghelp.dll");
    if (!dbghelp) return;
    using MiniDumpWriteDump_t = BOOL (WINAPI*)(HANDLE, DWORD, HANDLE, MINIDUMP_TYPE,
                                               PMINIDUMP_EXCEPTION_INFORMATION,
                                               PMINIDUMP_USER_STREAM_INFORMATION,
                                               PMINIDUMP_CALLBACK_INFORMATION);
    auto writeDump = reinterpret_cast<MiniDumpWriteDump_t>(GetProcAddress(dbghelp, "MiniDumpWriteDump"));
    if (!writeDump) {
        FreeLibrary(dbghelp);
        return;
    }
    const std::string dumpPath = ClientPath("EverLeafCrash.dmp");
    HANDLE file = CreateFileA(dumpPath.c_str(), GENERIC_WRITE, 0, nullptr,
                              CREATE_ALWAYS, FILE_ATTRIBUTE_NORMAL, nullptr);
    if (file != INVALID_HANDLE_VALUE) {
        MINIDUMP_EXCEPTION_INFORMATION info{};
        info.ThreadId = GetCurrentThreadId();
        info.ExceptionPointers = exceptionPointers;
        info.ClientPointers = FALSE;
        writeDump(GetCurrentProcess(), GetCurrentProcessId(), file,
                  MiniDumpNormal, exceptionPointers ? &info : nullptr,
                  nullptr, nullptr);
        CloseHandle(file);
    }
    FreeLibrary(dbghelp);
}

LONG WINAPI EverLeafUnhandledExceptionFilter(EXCEPTION_POINTERS* exceptionPointers) {
    char message[160]{};
    const DWORD code = exceptionPointers && exceptionPointers->ExceptionRecord
        ? exceptionPointers->ExceptionRecord->ExceptionCode : 0;
    const void* address = exceptionPointers && exceptionPointers->ExceptionRecord
        ? exceptionPointers->ExceptionRecord->ExceptionAddress : nullptr;
    sprintf_s(message, "fatal exception code=0x%08lX address=%p", code, address);
    AppendLine(message);
    WriteMiniDump(exceptionPointers);
    if (g_previousFilter && g_previousFilter != EverLeafUnhandledExceptionFilter)
        return g_previousFilter(exceptionPointers);
    return EXCEPTION_EXECUTE_HANDLER;
}

DWORD WINAPI FreezeWatchdog(LPVOID) {
    // Give the client enough time to finish startup before checking responsiveness.
    Sleep(30000);
    unsigned int consecutiveTimeouts = 0;
    while (true) {
        HWND window = FindWindowA("MapleStoryClass", nullptr);
        if (window) {
            DWORD_PTR result = 0;
            const LRESULT ok = SendMessageTimeoutA(window, WM_NULL, 0, 0,
                SMTO_ABORTIFHUNG | SMTO_BLOCK, 5000, &result);
            if (!ok && GetLastError() == ERROR_TIMEOUT) {
                ++consecutiveTimeouts;
                if (consecutiveTimeouts == 3) {
                    AppendLine("client window was unresponsive for three watchdog checks");
                }
            } else {
                consecutiveTimeouts = 0;
            }
        }
        Sleep(10000);
    }
}
} // namespace

void AttachEverLeafDiagnosticsMod() {
    AppendLine("EverLeaf client diagnostics initialized");
    g_previousFilter = SetUnhandledExceptionFilter(EverLeafUnhandledExceptionFilter);
    if (!g_watchdogStarted.exchange(true)) {
        HANDLE thread = CreateThread(nullptr, 0, FreezeWatchdog, nullptr, 0, nullptr);
        if (thread) CloseHandle(thread);
        else AppendLine("freeze watchdog could not start");
    }
}
