#include "stdafx.h"
#include "MainMain.h"

namespace {
    constexpr DWORD kNoWhackBranch = 0x009698BC;
    constexpr DWORD kNoWhackTarget = 0x00969A39;
    constexpr DWORD kRapidFireBranches[] = {
        0x0096AA4E,
        0x0096AA59,
        0x0096AA64,
        0x0096AA6F
    };
    constexpr DWORD kRapidFireTarget = 0x0096AEB5;

    bool IsExecutableAddress(DWORD address, SIZE_T bytes) {
        MEMORY_BASIC_INFORMATION mbi = {};
        if (VirtualQuery(reinterpret_cast<LPCVOID>(address), &mbi, sizeof(mbi)) == 0) {
            return false;
        }

        if (mbi.State != MEM_COMMIT || (mbi.Protect & (PAGE_NOACCESS | PAGE_GUARD)) != 0) {
            return false;
        }

        const DWORD regionEnd = static_cast<DWORD>(
            reinterpret_cast<ULONG_PTR>(mbi.BaseAddress) + mbi.RegionSize
        );
        return address + bytes <= regionEnd;
    }

    void ApplyNoWhackBranch() {
        if (!IsExecutableAddress(kNoWhackBranch, 6)) {
            return;
        }

        BYTE* code = reinterpret_cast<BYTE*>(kNoWhackBranch);

        // Canonical GMS v83 uses a near JNZ here (0F 85 rel32). Turn it into
        // an unconditional JMP to the existing non-whack path. A short-JNZ
        // layout is handled too so we fail safely across compatible v83 builds.
        if (code[0] == 0x0F && code[1] == 0x85) {
            Memory::WriteByte(kNoWhackBranch, 0xE9);
            Memory::WriteInt(
                kNoWhackBranch + 1,
                kNoWhackTarget - (kNoWhackBranch + 5)
            );
            Memory::WriteByte(kNoWhackBranch + 5, 0x90);
        } else if (code[0] == 0x75) {
            Memory::WriteByte(kNoWhackBranch, 0xEB);
        }
        // Already-patched or unexpected layouts are intentionally left alone.
    }

    void ApplyRapidFireNoWhackBranches() {
        for (DWORD address : kRapidFireBranches) {
            if (!IsExecutableAddress(address, 6)) {
                continue;
            }

            BYTE* code = reinterpret_cast<BYTE*>(address);
            if (code[0] == 0x0F && code[1] == 0x84) {
                Memory::WriteInt(
                    address + 2,
                    kRapidFireTarget - (address + 6)
                );
            }
        }
    }

    void ApplyEverLeafCombatQoL() {
        ApplyNoWhackBranch();
        ApplyRapidFireNoWhackBranches();
    }

    // EverLeaf always ships its HD UI overlay in the managed client package.
    // Select the full-size login-frame path from process startup so the legacy
    // 800x600 login presentation is not centered inside a black HD viewport.
    struct EverLeafClientDefaults {
        EverLeafClientDefaults() {
            MainMain::bigLoginFrame = true;
            ApplyEverLeafCombatQoL();
        }
    } gEverLeafClientDefaults;
}
