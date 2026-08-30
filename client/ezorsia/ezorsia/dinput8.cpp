#include "stdafx.h"
#include "dinput8.h"
//NOTE: this dll can also be used to remap the core functionality of keybinds, i.e. changing arrow keys in the game to WASD. but this would
FARPROC DirectInput8Create_Proc; //require reinterpreting the functions of the dll instead of just redirecting as is done here (to dinput8.dll)
FARPROC GetdfDIJoystick_Proc;

namespace {
	volatile LONG g_launcherTicketAccepted = 0;
	const char* kLauncherTicket = ".everleaf-launch";
	const __int64 kTicketMaxAgeSeconds = 120;

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
	char szPath[MAX_PATH];
	if (GetSystemDirectoryA(szPath, sizeof(szPath))) { strcat(szPath, "\\dinput8.dll"); }
	else { Sleep(20); SuspendThread(MainMain::mainTHread); MessageBox(NULL, L"Failed to load original dinput8.dll from system location, make sure your directory path is not longer than " + MAX_PATH, L"systems directory inaccessible", 0); ExitProcess(0); }
	HMODULE hModule = LoadLibraryA(szPath);
	if (hModule) { 
		DirectInput8Create_Proc = GetProcAddress(hModule, "DirectInput8Create"); 
		GetdfDIJoystick_Proc = GetProcAddress(hModule, "GetdfDIJoystick");
	}
	else { Sleep(20); SuspendThread(MainMain::mainTHread); MessageBox(NULL, L"Failed to find original dinput8.dll, verify that a non-Ezorsia v2 dinput8.dll exists in your system directory", L"Missing file", 0); ExitProcess(0); }
}
extern "C" __declspec(dllexport) __declspec(naked) void DirectInput8Create()
{
	__asm {
		pushad
		call RequireEverLeafLauncher
		popad
		jmp dword ptr[DirectInput8Create_Proc]
	}
}
extern "C" __declspec(dllexport) __declspec(naked) void GetdfDIJoystick()
{
	__asm	jmp dword ptr[GetdfDIJoystick_Proc]
}