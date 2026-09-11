#include <windows.h>
#include <strsafe.h>
#include <cwchar>

namespace {
INIT_ONCE gOnce = INIT_ONCE_STATIC_INIT;
HMODULE gSystemDinput8 = nullptr;
FARPROC gDirectInput8Create = nullptr;
FARPROC gGetdfDIJoystick = nullptr;

BOOL CALLBACK ResolveSystemDinput8(PINIT_ONCE, PVOID, PVOID*) {
    wchar_t path[MAX_PATH] = {};
    const UINT n = GetSystemDirectoryW(path, MAX_PATH);
    if (!n || n >= MAX_PATH) return FALSE;
    if (FAILED(StringCchCatW(path, MAX_PATH, L"\\dinput8.dll"))) return FALSE;
    gSystemDinput8 = LoadLibraryW(path);
    if (!gSystemDinput8) return FALSE;
    gDirectInput8Create = GetProcAddress(gSystemDinput8, "DirectInput8Create");
    gGetdfDIJoystick = GetProcAddress(gSystemDinput8, "GetdfDIJoystick");
    return gDirectInput8Create && gGetdfDIJoystick;
}

void EnsureSystemDinput8() {
    PVOID unused = nullptr;
    if (!InitOnceExecuteOnce(&gOnce, ResolveSystemDinput8, nullptr, &unused)) {
        ExitProcess(ERROR_MOD_NOT_FOUND);
    }
}

DWORD WINAPI LoadEverLeafCore(LPVOID) {
    wchar_t exePath[MAX_PATH] = {};
    GetModuleFileNameW(nullptr, exePath, MAX_PATH);
    wchar_t* slash = std::wcsrchr(exePath, L'\\');
    if (slash) *(slash + 1) = L'\0';
    if (FAILED(StringCchCatW(exePath, MAX_PATH, L"EverLeafMS.dll")) || !LoadLibraryW(exePath)) {
        MessageBoxW(nullptr,
            L"EverLeafMS.dll is missing or could not be loaded. Run Install / Repair Files in EverLeafLauncher.",
            L"EverLeaf client bootstrap error", MB_OK | MB_ICONERROR);
        ExitProcess(ERROR_MOD_NOT_FOUND);
    }
    return 0;
}
}

extern "C" __declspec(noinline) FARPROC __cdecl EverLeafResolveDirectInput8Create() {
    EnsureSystemDinput8();
    return gDirectInput8Create;
}

extern "C" __declspec(noinline) FARPROC __cdecl EverLeafResolveGetdfDIJoystick() {
    EnsureSystemDinput8();
    return gGetdfDIJoystick;
}

extern "C" __declspec(dllexport) __declspec(naked) void DirectInput8Create() {
    __asm {
        call EverLeafResolveDirectInput8Create
        jmp eax
    }
}

extern "C" __declspec(dllexport) __declspec(naked) void GetdfDIJoystick() {
    __asm {
        call EverLeafResolveGetdfDIJoystick
        jmp eax
    }
}

BOOL APIENTRY DllMain(HMODULE module, DWORD reason, LPVOID) {
    if (reason == DLL_PROCESS_ATTACH) {
        DisableThreadLibraryCalls(module);
        HANDLE thread = CreateThread(nullptr, 0, LoadEverLeafCore, nullptr, 0, nullptr);
        if (thread) CloseHandle(thread);
    }
    return TRUE;
}
