#pragma once

#include <cstddef>
#include <cstring>
#include <iostream>
#include <windows.h>
#include "Memory.h"

namespace EverLeafEvanClientPatch {

// Blu3sky's v83 Evan release requires two independent client NOPs:
//   PatchNop(0x0075C783, 4)
//   PatchNop(0x00761714, 21)
//
// EverLeaf runs against a packed executable, so historical virtual addresses
// are not safe to write directly. Both sites are therefore located only after
// the executable is mapped, using signatures derived from EverLeaf's verified
// unpacked v83 localhost. The patch fails closed if either signature is absent
// or ambiguous.

// Signature around the first Evan activation patch. The 4 bytes at offset 8
// are the exact historical patch target: 33 C0 EB 2E.
inline constexpr unsigned char kEvanActivation1Signature[] = {
    0x81, 0xFE, 0xD1, 0x07, 0x00, 0x00, 0x75, 0x04,
    0x33, 0xC0, 0xEB, 0x2E,
    0x33, 0xF6, 0x89, 0x75, 0xF0, 0x8D, 0x45, 0xEC
};
inline constexpr std::size_t kEvanActivation1PatchOffset = 8;
inline constexpr std::size_t kEvanActivation1PatchLength = 4;
inline constexpr unsigned char kEvanActivation1Original[] = {
    0x33, 0xC0, 0xEB, 0x2E
};

// v83 CSkillInfo::GetSkill contains this Evan-specific early-out. Historical
// releases quote several different virtual addresses, so EverLeaf intentionally
// locates the instruction sequence by signature instead of hardcoding an RVA.
inline constexpr unsigned char kEvanSkillGuard[] = {
    0x83, 0xF8, 0x16, 0x0F, 0x84, 0xD7, 0x00,
    0x00, 0x00, 0x81, 0xFE, 0xD1, 0x07, 0x00,
    0x00, 0x0F, 0x84, 0xCB, 0x00, 0x00, 0x00
};

inline bool IsExecutableSection(const IMAGE_SECTION_HEADER& section) {
    return (section.Characteristics & IMAGE_SCN_MEM_EXECUTE) != 0;
}

template <std::size_t N>
inline unsigned char* FindUniqueExecutableSignature(const unsigned char (&signature)[N]) {
    HMODULE module = GetModuleHandleW(nullptr);
    if (!module) {
        return nullptr;
    }

    auto* base = reinterpret_cast<unsigned char*>(module);
    auto* dos = reinterpret_cast<IMAGE_DOS_HEADER*>(base);
    if (dos->e_magic != IMAGE_DOS_SIGNATURE) {
        return nullptr;
    }

    auto* nt = reinterpret_cast<IMAGE_NT_HEADERS*>(base + dos->e_lfanew);
    if (nt->Signature != IMAGE_NT_SIGNATURE) {
        return nullptr;
    }

    auto* section = IMAGE_FIRST_SECTION(nt);
    unsigned char* match = nullptr;
    std::size_t matches = 0;

    for (WORD i = 0; i < nt->FileHeader.NumberOfSections; ++i, ++section) {
        if (!IsExecutableSection(*section)) {
            continue;
        }

        const std::size_t sectionSize = static_cast<std::size_t>(section->Misc.VirtualSize);
        if (sectionSize < N) {
            continue;
        }

        unsigned char* begin = base + section->VirtualAddress;
        const std::size_t last = sectionSize - N;
        for (std::size_t offset = 0; offset <= last; ++offset) {
            if (std::memcmp(begin + offset, signature, N) == 0) {
                match = begin + offset;
                ++matches;
                if (matches > 1) {
                    return nullptr;
                }
            }
        }
    }

    return matches == 1 ? match : nullptr;
}

inline bool ApplyActivation1Patch() {
    unsigned char* signature = FindUniqueExecutableSignature(kEvanActivation1Signature);
    if (!signature) {
        std::cerr << "EverLeaf Evan client patch: expected unique activation-1 signature was not found; no activation-1 bytes changed." << std::endl;
        return false;
    }

    unsigned char* target = signature + kEvanActivation1PatchOffset;
    if (std::memcmp(target, kEvanActivation1Original, sizeof(kEvanActivation1Original)) != 0) {
        std::cerr << "EverLeaf Evan client patch: activation-1 target changed before write; no activation-1 bytes changed." << std::endl;
        return false;
    }

    Memory::FillBytes(reinterpret_cast<DWORD>(target), 0x90, static_cast<int>(kEvanActivation1PatchLength));
    std::cout << "EverLeaf Evan client patch: unlocked first Evan skill activation path." << std::endl;
    return true;
}

inline bool ApplySkillGuardPatch() {
    unsigned char* guard = FindUniqueExecutableSignature(kEvanSkillGuard);
    if (!guard) {
        std::cerr << "EverLeaf Evan client patch: expected unique CSkillInfo::GetSkill signature was not found; no skill-guard bytes changed." << std::endl;
        return false;
    }

    if (std::memcmp(guard, kEvanSkillGuard, sizeof(kEvanSkillGuard)) != 0) {
        std::cerr << "EverLeaf Evan client patch: skill-guard signature changed before write; no skill-guard bytes changed." << std::endl;
        return false;
    }

    Memory::FillBytes(reinterpret_cast<DWORD>(guard), 0x90, static_cast<int>(sizeof(kEvanSkillGuard)));
    std::cout << "EverLeaf Evan client patch: unlocked CSkillInfo::GetSkill Evan path." << std::endl;
    return true;
}

inline bool Apply() {
    // Keep these independent so logs identify exactly which v83 Evan guard was
    // rejected if a future executable changes. The DLL does not guess offsets.
    const bool activation1 = ApplyActivation1Patch();
    const bool skillGuard = ApplySkillGuardPatch();
    return activation1 && skillGuard;
}

// The executable is fully mapped before the proxy dinput8 DLL initializes.
// An inline variable ensures this executes once even though stdafx.h is shared.
struct AutoApply {
    AutoApply() { Apply(); }
};

inline AutoApply g_autoApply;

} // namespace EverLeafEvanClientPatch
