#include "pch.h"
#include "hook.h"

#include <cstring>

namespace {

// These addresses/signatures are the stock GMS v83 login control construction
// sites.  We only apply the layout when every signature matches, so a different
// client binary fails closed instead of receiving a partial patch.
DWORD g_dialogReturn = 0x006203F6;
DWORD g_loginReturn = 0x00620649;
DWORD g_saveReturn = 0x006206C0;
DWORD g_findReturn = 0x0062073A;
DWORD g_resetReturn = 0x006207B4;
DWORD g_registerReturn = 0x0062082B;
DWORD g_homeReturn = 0x006208A2;
DWORD g_quitReturn = 0x0062091C;

__declspec(naked) void DialogPosition() {
    __asm {
        push 236
        push 368
        push -86
        push -184
        jmp dword ptr [g_dialogReturn]
    }
}

__declspec(naked) void LoginPosition() {
    __asm {
        push 0
        push 10
        push 274
        jmp dword ptr [g_loginReturn]
    }
}

__declspec(naked) void SavePosition() {
    __asm {
        push 0
        push 90
        push 84
        jmp dword ptr [g_saveReturn]
    }
}

__declspec(naked) void FindPosition() {
    __asm {
        push 0
        push 90
        push 168
        jmp dword ptr [g_findReturn]
    }
}

__declspec(naked) void ResetPosition() {
    __asm {
        push 0
        push 90
        push 252
        jmp dword ptr [g_resetReturn]
    }
}

__declspec(naked) void RegisterPosition() {
    __asm {
        push 0
        push 140
        push 58
        jmp dword ptr [g_registerReturn]
    }
}

__declspec(naked) void HomePosition() {
    __asm {
        push 0
        push 140
        push 162
        jmp dword ptr [g_homeReturn]
    }
}

__declspec(naked) void QuitPosition() {
    __asm {
        push 0
        push 140
        push 268
        jmp dword ptr [g_quitReturn]
    }
}

struct PatchSite {
    uintptr_t address;
    const unsigned char* expected;
    size_t length;
    void* destination;
};

bool Matches(uintptr_t address, const unsigned char* expected, size_t length) {
    __try {
        return std::memcmp(reinterpret_cast<const void*>(address), expected, length) == 0;
    } __except (EXCEPTION_EXECUTE_HANDLER) {
        return false;
    }
}

void InstallJump(const PatchSite& patch) {
    PatchJmp(patch.address, patch.destination);
    if (patch.length > 5) {
        PatchNop(patch.address + 5, patch.address + patch.length);
    }
}

} // namespace

void AttachLoginLayoutMod() {
    static const unsigned char kDialogBytes[] = {
        0x68,0xB4,0x00,0x00,0x00,0x68,0x4A,0x01,0x00,0x00,0x6A,0xB0,0x6A,0x0A
    };
    static const unsigned char kLoginBytes[] = {
        0x6A,0x00,0x6A,0xFB,0x68,0xD5,0x00,0x00,0x00
    };
    static const unsigned char kSaveBytes[] = {
        0x6A,0x00,0x6A,0x4A,0x6A,0x25
    };
    static const unsigned char kFindBytes[] = {
        0x6A,0x00,0x6A,0x49,0x68,0x90,0x00,0x00,0x00
    };
    static const unsigned char kResetBytes[] = {
        0x6A,0x00,0x6A,0x4A,0x68,0xE2,0x00,0x00,0x00
    };
    static const unsigned char kRegisterBytes[] = {
        0x6A,0x00,0x6A,0x7A,0x6A,0x0E
    };
    static const unsigned char kHomeBytes[] = {
        0x6A,0x00,0x6A,0x78,0x6A,0x72
    };
    static const unsigned char kQuitBytes[] = {
        0x6A,0x00,0x6A,0x78,0x68,0xD6,0x00,0x00,0x00
    };

    const PatchSite patches[] = {
        {0x006203E8, kDialogBytes, sizeof(kDialogBytes), CastHook(&DialogPosition)},
        {0x00620640, kLoginBytes, sizeof(kLoginBytes), CastHook(&LoginPosition)},
        {0x006206BA, kSaveBytes, sizeof(kSaveBytes), CastHook(&SavePosition)},
        {0x00620731, kFindBytes, sizeof(kFindBytes), CastHook(&FindPosition)},
        {0x006207AB, kResetBytes, sizeof(kResetBytes), CastHook(&ResetPosition)},
        {0x00620825, kRegisterBytes, sizeof(kRegisterBytes), CastHook(&RegisterPosition)},
        {0x0062089C, kHomeBytes, sizeof(kHomeBytes), CastHook(&HomePosition)},
        {0x00620913, kQuitBytes, sizeof(kQuitBytes), CastHook(&QuitPosition)},
    };

    for (const auto& patch : patches) {
        if (!Matches(patch.address, patch.expected, patch.length)) {
            DEBUG_MESSAGE("EverLeaf login layout signature mismatch at 0x%08X; skipped", patch.address);
            return;
        }
    }

    static const unsigned char kUserBytes[] = {
        0x6A,0x0F,0x68,0x84,0x00,0x00,0x00,0x6A,0x0C,0x6A,0x43
    };
    static const unsigned char kPassBytes[] = {
        0x6A,0x0F,0x6A,0x78,0x6A,0x28,0x6A,0x43
    };
    if (!Matches(0x006209A6, kUserBytes, sizeof(kUserBytes)) ||
        !Matches(0x00620A0D, kPassBytes, sizeof(kPassBytes))) {
        DEBUG_MESSAGE("EverLeaf login text-field signature mismatch; skipped");
        return;
    }

    if (*reinterpret_cast<const unsigned char*>(0x006210E4) != 0x6A ||
        *reinterpret_cast<const unsigned char*>(0x006210E5) != 74 ||
        *reinterpret_cast<const unsigned char*>(0x006210E7) != 0x6A ||
        *reinterpret_cast<const unsigned char*>(0x006210E8) != 18) {
        DEBUG_MESSAGE("EverLeaf save-ID checkbox signature mismatch; skipped");
        return;
    }

    for (const auto& patch : patches) {
        InstallJump(patch);
    }

    // Align the native edit controls with the EverLeaf 800x600 signboard.
    Patch1(0x006209AE, 6);
    Patch1(0x006209B0, 95);
    Patch1(0x00620A12, 41);
    Patch1(0x00620A14, 95);

    // Save-ID checkbox is drawn separately from the button canvas.
    Patch1(0x006210E5, 90);
    Patch1(0x006210E8, 64);

    DEBUG_MESSAGE("EverLeaf 800x600 login layout applied");
}
