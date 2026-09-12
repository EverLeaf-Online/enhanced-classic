#include <windows.h>
#include <strsafe.h>

namespace {
INIT_ONCE g_once = INIT_ONCE_STATIC_INIT;
HMODULE g_systemDinput8 = nullptr;
FARPROC g_directInput8Create = nullptr;
FARPROC g_getdfDIJoystick = nullptr;

BOOL CALLBACK ResolveSystemDinput8(PINIT_ONCE, PVOID, PVOID*) {
    wchar_t path[MAX_PATH] = {};
    const UINT length = GetSystemDirectoryW(path, MAX_PATH);
    if (!length || length >= MAX_PATH) return FALSE;
    if (FAILED(StringCchCatW(path, MAX_PATH, L"\\dinput8.dll"))) return FALSE;

    g_systemDinput8 = LoadLibraryW(path);
    if (!g_systemDinput8) return FALSE;

    g_directInput8Create = GetProcAddress(g_systemDinput8, "DirectInput8Create");
    g_getdfDIJoystick = GetProcAddress(g_systemDinput8, "GetdfDIJoystick");
    return g_directInput8Create != nullptr && g_getdfDIJoystick != nullptr;
}

FARPROC Resolve(FARPROC* proc) {
    PVOID unused = nullptr;
    if (!InitOnceExecuteOnce(&g_once, ResolveSystemDinput8, nullptr, &unused) || !*proc) {
        ExitProcess(ERROR_MOD_NOT_FOUND);
    }
    return *proc;
}
}

extern "C" __declspec(noinline) FARPROC __cdecl EverLeafResolveDirectInput8Create() {
    return Resolve(&g_directInput8Create);
}

extern "C" __declspec(noinline) FARPROC __cdecl EverLeafResolveGetdfDIJoystick() {
    return Resolve(&g_getdfDIJoystick);
}

extern "C" __declspec(naked) void DirectInput8CreateForward() {
    __asm {
        call EverLeafResolveDirectInput8Create
        jmp eax
    }
}

extern "C" __declspec(naked) void GetdfDIJoystickForward() {
    __asm {
        call EverLeafResolveGetdfDIJoystick
        jmp eax
    }
}

BOOL APIENTRY DllMain(HMODULE module, DWORD reason, LPVOID) {
    if (reason == DLL_PROCESS_ATTACH) DisableThreadLibraryCalls(module);
    return TRUE;
}

// EverLeaf managed runtime forwarder.
