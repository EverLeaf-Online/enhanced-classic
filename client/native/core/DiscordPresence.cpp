#include "stdafx.h"
#include "DiscordPresence.h"

#include <windows.h>

namespace DiscordPresence {
namespace {
    using StartFn = void (__cdecl*)();
    using StopFn = void (__cdecl*)();
    using SetActivityFn = void (__cdecl*)(const char*, const char*);

    HMODULE gModule = nullptr;
    StartFn gStart = nullptr;
    StopFn gStop = nullptr;
    SetActivityFn gSetActivity = nullptr;

    bool Resolve() {
        if (gModule) return gStart && gStop;
        gModule = LoadLibraryW(L"Discord.dll");
        if (!gModule) return false;
        gStart = reinterpret_cast<StartFn>(GetProcAddress(gModule, "EverLeafDiscord_Start"));
        gStop = reinterpret_cast<StopFn>(GetProcAddress(gModule, "EverLeafDiscord_Stop"));
        gSetActivity = reinterpret_cast<SetActivityFn>(GetProcAddress(gModule, "EverLeafDiscord_SetActivity"));
        if (!gStart || !gStop) {
            FreeLibrary(gModule);
            gModule = nullptr;
            gStart = nullptr;
            gStop = nullptr;
            gSetActivity = nullptr;
            return false;
        }
        return true;
    }
}

void Start() {
    if (Resolve()) gStart();
}

void Stop() {
    if (gStop) gStop();
    if (gModule) FreeLibrary(gModule);
    gModule = nullptr;
    gStart = nullptr;
    gStop = nullptr;
    gSetActivity = nullptr;
}

void SetActivity(const std::string& details, const std::string& state) {
    if (Resolve() && gSetActivity) gSetActivity(details.c_str(), state.c_str());
}
}
