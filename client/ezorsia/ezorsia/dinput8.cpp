#include "stdafx.h"
#include "dinput8.h"
#include "WasdInput.h"

// System dinput8 forwarding targets. The exported naked stubs below can be
// reached before the rest of the Maple client has finished unpacking, so these
// pointers must be resolved lazily at the export boundary rather than assuming
// MainFunc already ran.
FARPROC DirectInput8Create_Proc = nullptr;
FARPROC GetdfDIJoystick_Proc = nullptr;

namespace {
	volatile LONG g_launcherTicketAccepted = 0;
	const char* kLauncherTicket = ".everleaf-launch";
	const __int64 kTicketMaxAgeSeconds = 120;
	INIT_ONCE g_dinputInitOnce = INIT_ONCE_STATIC_INIT;
	HMODULE g_systemDinput8 = nullptr;

	BOOL CALLBACK ResolveSystemDinput8(PINIT_ONCE, PVOID, PVOID*) {
		char szPath[MAX_PATH] = { 0 };
		const UINT systemPathLength = GetSystemDirectoryA(szPath, ARRAYSIZE(szPath));
		if (systemPathLength == 0 || systemPathLength >= ARRAYSIZE(szPath)) {
			SetLastError(ERROR_INSUFFICIENT_BUFFER);
			return FALSE;
		}

		if (strcat_s(szPath, "\\dinput8.dll") != 0) {
			SetLastError(ERROR_INSUFFICIENT_BUFFER);
			return FALSE;
		}

		HMODULE module = LoadLibraryA(szPath);
		if (!module) {
			return FALSE;
		}

		FARPROC directInput = GetProcAddress(module, "DirectInput8Create");
		FARPROC joystick = GetProcAddress(module, "GetdfDIJoystick");
		if (!directInput || !joystick) {
			FreeLibrary(module);
			SetLastError(ERROR_PROC_NOT_FOUND);
			return FALSE;
		}

		DirectInput8Create_Proc = directInput;
		GetdfDIJoystick_Proc = joystick;
		g_systemDinput8 = module;
		return TRUE;
	}

	void EnsureSystemDinput8() {
		PVOID context = nullptr;
		if (InitOnceExecuteOnce(&g_dinputInitOnce, ResolveSystemDinput8, nullptr, &context)) {
			return;
		}

		DWORD error = GetLastError();
		if (error == ERROR_SUCCESS) {
			error = ERROR_MOD_NOT_FOUND;
		}
		MessageBoxW(
			nullptr,
			L"EverLeaf could not load the Windows system dinput8.dll or one of its required exports.\n\n"
			L"Repair Windows system files if this persists, then launch EverLeaf again.",
			L"EverLeaf Client v2 input error",
			MB_OK | MB_ICONERROR
		);
		ExitProcess(error);
	}

	bool ConsumeFreshLauncherTicket() {
		if (InterlockedCompareExchange(&g_launcherTicketAccepted, 1, 1) == 1) return true;

		HANDLE ticket = CreateFileA(kLauncherTicket, GENERIC_READ, FILE_SHARE_READ, NULL, OPEN_EXISTING, FILE_ATTRIBUTE_HIDDEN, NULL);
		if (ticket == INVALID_HANDLE_VALUE) return false;

		char buffer[64] = { 0 };
		DWORD bytesRead = 0;
		const BOOL readOk = ReadFile(ticket, buffer, sizeof(buffer) - 1, &bytesRead, NULL);
		CloseHandle(ticket);
		DeleteFileA(kLauncherTicket); // a launch ticket is single-use even when malformed

		if (!readOk || bytesRead == 0) return false;
		buffer[bytesRead] = '\0';
		char* end = nullptr;
		const __int64 issuedAt = _strtoi64(buffer, &end, 10);
		if (issuedAt <= 0 || end == buffer) return false;

		const __int64 now = static_cast<__int64>(time(NULL));
		if (now < issuedAt - 5 || now - issuedAt > kTicketMaxAgeSeconds) return false;

		InterlockedExchange(&g_launcherTicketAccepted, 1);
		return true;
	}

	void RequireEverLeafLauncher() {
		if (ConsumeFreshLauncherTicket()) return;

		MessageBox(NULL,
			L"Please start EverLeaf with EverLeafLauncher.exe instead of opening EverLeaf.exe directly. The launcher verifies and repairs your game files before Play.",
			L"EverLeaf Launcher Required",
			MB_OK | MB_ICONINFORMATION);
		ExitProcess(0);
	}
}

void dinput8::CreateHook() {
	// Eagerly resolve during the normal bootstrap path, while the exported stubs
	// also call the same thread-safe resolver in case Maple reaches them first.
	EnsureSystemDinput8();

	// The gameplay remapper is installed only here, after Client v2 has verified
	// the unpacked v83 image. When WASDRemapping=false (the default), Install()
	// returns without creating any Detours hook and stock Maple input is untouched.
	if (!EverLeafWasdInput::Install(true)) {
		MessageBoxW(
			nullptr,
			L"EverLeaf could not initialize the optional WASD input layer.\n\n"
			L"Please repair/update the client before enabling WASD movement.",
			L"EverLeaf Client v2 input error",
			MB_OK | MB_ICONERROR
		);
		ExitProcess(ERROR_DLL_INIT_FAILED);
	}
}

extern "C" __declspec(dllexport) __declspec(naked) void DirectInput8Create()
{
	__asm {
		pushfd
		pushad
		call EnsureSystemDinput8
		call RequireEverLeafLauncher
		popad
		popfd
		jmp dword ptr[DirectInput8Create_Proc]
	}
}

extern "C" __declspec(dllexport) __declspec(naked) void GetdfDIJoystick()
{
	__asm {
		pushfd
		pushad
		call EnsureSystemDinput8
		popad
		popfd
		jmp dword ptr[GetdfDIJoystick_Proc]
	}
}
