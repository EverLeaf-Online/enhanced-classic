#include "../core/stdafx.h"
#include "../core/DiscordPresence.h"

extern "C" __declspec(dllexport) void __cdecl EverLeafDiscord_Start() {
    DiscordPresence::Start();
}

extern "C" __declspec(dllexport) void __cdecl EverLeafDiscord_Stop() {
    DiscordPresence::Stop();
}

extern "C" __declspec(dllexport) void __cdecl EverLeafDiscord_SetActivity(const char* details, const char* state) {
    DiscordPresence::SetActivity(details ? details : "", state ? state : "");
}

BOOL APIENTRY DllMain(HMODULE module, DWORD reason, LPVOID) {
    if (reason == DLL_PROCESS_ATTACH) DisableThreadLibraryCalls(module);
    return TRUE;
}
