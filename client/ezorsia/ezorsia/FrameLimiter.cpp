#include "stdafx.h"
#include "FrameLimiter.h"
#include "Memory.h"
#include "INIReader.h"
#include "CrashDiagnostics.h"

namespace {
struct IWzGr2D;
using RenderFrame_t = HRESULT(__thiscall*)(IWzGr2D*);
constexpr DWORD kRenderFrameAddress = 0x00777326;
RenderFrame_t gRenderFrameOriginal = reinterpret_cast<RenderFrame_t>(kRenderFrameAddress);

LARGE_INTEGER gCounterFrequency = {};
LONGLONG gNextFrameTick = 0;
int gForegroundFpsCap = 60;
int gBackgroundFpsCap = 15;
bool gLimitBackgroundFps = true;
int gLastTargetFps = -1;

int ClampInt(int value, int minimum, int maximum) {
    if (value < minimum) return minimum;
    if (value > maximum) return maximum;
    return value;
}

bool IsGameForeground() {
    const HWND foreground = GetForegroundWindow();
    if (!foreground) {
        return true;
    }

    DWORD processId = 0;
    GetWindowThreadProcessId(foreground, &processId);
    return processId == GetCurrentProcessId();
}

int CurrentTargetFps() {
    if (gLimitBackgroundFps && !IsGameForeground()) {
        return gBackgroundFpsCap;
    }
    return gForegroundFpsCap;
}

void ResetSchedule() {
    LARGE_INTEGER now = {};
    QueryPerformanceCounter(&now);
    gNextFrameTick = now.QuadPart;
}

void WaitForFrameSlot(int targetFps) {
    if (targetFps <= 0 || gCounterFrequency.QuadPart <= 0) {
        gLastTargetFps = targetFps;
        return;
    }

    if (targetFps != gLastTargetFps) {
        gLastTargetFps = targetFps;
        ResetSchedule();
    }

    LARGE_INTEGER now = {};
    QueryPerformanceCounter(&now);

    const LONGLONG interval = gCounterFrequency.QuadPart / targetFps;
    if (interval <= 0) {
        return;
    }

    // Large clock jumps happen after suspend/resume, breakpoints, or long stalls.
    // Reset instead of trying to repay a large backlog of presentation frames.
    if (gNextFrameTick <= 0 || now.QuadPart - gNextFrameTick > interval * 4) {
        gNextFrameTick = now.QuadPart;
    }

    gNextFrameTick += interval;

    while (true) {
        QueryPerformanceCounter(&now);
        const LONGLONG remaining = gNextFrameTick - now.QuadPart;
        if (remaining <= 0) {
            break;
        }

        const LONGLONG remainingMs = (remaining * 1000) / gCounterFrequency.QuadPart;
        if (remainingMs > 2) {
            Sleep(static_cast<DWORD>(remainingMs - 1));
        }
        else {
            SwitchToThread();
        }
    }
}

HRESULT __fastcall RenderFrameHook(IWzGr2D* pThis, void*) {
    WaitForFrameSlot(CurrentTargetFps());
    return gRenderFrameOriginal(pThis);
}
}

bool FrameLimiter::Install() {
    INIReader config("config.ini");
    if (config.ParseError()) {
        CrashDiagnostics::LogEvent("frame limiter skipped: config parse error");
        return false;
    }

    const int requestedForeground = static_cast<int>(config.GetInteger("general", "ForegroundFPSCap", 60));
    const int requestedBackground = static_cast<int>(config.GetInteger("general", "BackgroundFPSCap", 15));
    gLimitBackgroundFps = config.GetBoolean("general", "LimitBackgroundFPS", true);

    // 0 explicitly disables the foreground cap. Otherwise keep player-facing
    // values in a conservative range that does not change the 30 ms game logic tick.
    gForegroundFpsCap = requestedForeground == 0 ? 0 : ClampInt(requestedForeground, 30, 240);
    gBackgroundFpsCap = ClampInt(requestedBackground, 5, 60);

    if (!QueryPerformanceFrequency(&gCounterFrequency) || gCounterFrequency.QuadPart <= 0) {
        CrashDiagnostics::LogEvent("frame limiter skipped: high resolution timer unavailable");
        return false;
    }

    if (!Memory::SetHook(
            true,
            reinterpret_cast<void**>(&gRenderFrameOriginal),
            reinterpret_cast<void*>(RenderFrameHook))) {
        CrashDiagnostics::LogEvent("frame limiter hook failed");
        return false;
    }

    ResetSchedule();
    CrashDiagnostics::LogEvent("frame limiter installed");
    return true;
}
