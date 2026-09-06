#include "stdafx.h"
#include "MainMain.h"
#include "Memory.h"
#include "CrashDiagnostics.h"
#include <cstring>

namespace {
struct Defaults { Defaults() { MainMain::bigLoginFrame = true; } } defaults;
DWORD DialogReturn = 0x6203f6;
__declspec(naked) void DialogPosition() {
    __asm {
        push 236
        push 368
        push -86
        push -184
        jmp dword ptr [DialogReturn]
    }
}
DWORD LoginReturn = 0x620649;
__declspec(naked) void LoginPosition() {
    __asm {
        push 0
        push 10
        push 274
        jmp dword ptr [LoginReturn]
    }
}
DWORD SaveReturn = 0x6206c0;
__declspec(naked) void SavePosition() {
    __asm {
        push 0
        push 90
        push 84
        jmp dword ptr [SaveReturn]
    }
}
DWORD FindReturn = 0x62073a;
__declspec(naked) void FindPosition() {
    __asm {
        push 0
        push 90
        push 168
        jmp dword ptr [FindReturn]
    }
}
DWORD ResetReturn = 0x6207b4;
__declspec(naked) void ResetPosition() {
    __asm {
        push 0
        push 90
        push 252
        jmp dword ptr [ResetReturn]
    }
}
DWORD RegisterReturn = 0x62082b;
__declspec(naked) void RegisterPosition() {
    __asm {
        push 0
        push 140
        push 58
        jmp dword ptr [RegisterReturn]
    }
}
DWORD HomeReturn = 0x6208a2;
__declspec(naked) void HomePosition() {
    __asm {
        push 0
        push 140
        push 162
        jmp dword ptr [HomeReturn]
    }
}
DWORD QuitReturn = 0x62091c;
__declspec(naked) void QuitPosition() {
    __asm {
        push 0
        push 140
        push 268
        jmp dword ptr [QuitReturn]
    }
}
struct Patch { DWORD address; const unsigned char* expected; size_t length; void* hook; };
}
void ApplyEverLeafLoginLayout() {
    static const unsigned char DialogBytes[] = {0x68,0xb4,0x00,0x00,0x00,0x68,0x4a,0x01,0x00,0x00,0x6a,0xb0,0x6a,0x0a};
    static const unsigned char LoginBytes[] = {0x6a,0x00,0x6a,0xfb,0x68,0xd5,0x00,0x00,0x00};
    static const unsigned char SaveBytes[] = {0x6a,0x00,0x6a,0x4a,0x6a,0x25};
    static const unsigned char FindBytes[] = {0x6a,0x00,0x6a,0x49,0x68,0x90,0x00,0x00,0x00};
    static const unsigned char ResetBytes[] = {0x6a,0x00,0x6a,0x4a,0x68,0xe2,0x00,0x00,0x00};
    static const unsigned char RegisterBytes[] = {0x6a,0x00,0x6a,0x7a,0x6a,0x0e};
    static const unsigned char HomeBytes[] = {0x6a,0x00,0x6a,0x78,0x6a,0x72};
    static const unsigned char QuitBytes[] = {0x6a,0x00,0x6a,0x78,0x68,0xd6,0x00,0x00,0x00};
    const Patch patches[] = {
        {0x6203e8, DialogBytes, sizeof(DialogBytes), reinterpret_cast<void*>(DialogPosition)},
        {0x620640, LoginBytes, sizeof(LoginBytes), reinterpret_cast<void*>(LoginPosition)},
        {0x6206ba, SaveBytes, sizeof(SaveBytes), reinterpret_cast<void*>(SavePosition)},
        {0x620731, FindBytes, sizeof(FindBytes), reinterpret_cast<void*>(FindPosition)},
        {0x6207ab, ResetBytes, sizeof(ResetBytes), reinterpret_cast<void*>(ResetPosition)},
        {0x620825, RegisterBytes, sizeof(RegisterBytes), reinterpret_cast<void*>(RegisterPosition)},
        {0x62089c, HomeBytes, sizeof(HomeBytes), reinterpret_cast<void*>(HomePosition)},
        {0x620913, QuitBytes, sizeof(QuitBytes), reinterpret_cast<void*>(QuitPosition)}
    };
    for (const auto& p : patches) {
        if (std::memcmp(reinterpret_cast<const void*>(p.address), p.expected, p.length) != 0) {
            CrashDiagnostics::LogEvent("login layout signature mismatch; skipped");
            return;
        }
    }
    const unsigned char userBytes[] = {0x6a,0x0f,0x68,0x84,0,0,0,0x6a,0x0c,0x6a,0x43};
    const unsigned char passBytes[] = {0x6a,0x0f,0x6a,0x78,0x6a,0x28,0x6a,0x43};
    if (std::memcmp(reinterpret_cast<void*>(0x6209a6),userBytes,sizeof(userBytes)) || std::memcmp(reinterpret_cast<void*>(0x620a0d),passBytes,sizeof(passBytes))) return;
    if (*reinterpret_cast<const unsigned char*>(0x6210e4)!=0x6a || *reinterpret_cast<const unsigned char*>(0x6210e5)!=74 || *reinterpret_cast<const unsigned char*>(0x6210e7)!=0x6a || *reinterpret_cast<const unsigned char*>(0x6210e8)!=18) return;
    for (const auto& p : patches) Memory::CodeCave(p.hook,p.address,p.length);
    Memory::WriteByte(0x6209ae,6);
    Memory::WriteByte(0x6209b0,95);
    Memory::WriteByte(0x620a12,41);
    Memory::WriteByte(0x620a14,95);
    // Save ID checkbox is a canvas drawn separately from the native button.
    Memory::WriteByte(0x6210e5,90);
    Memory::WriteByte(0x6210e8,72);
    CrashDiagnostics::LogEvent("centered native login layout applied");
}

namespace EverLeafLoginLayout {
void Apply() { ApplyEverLeafLoginLayout(); }
}
