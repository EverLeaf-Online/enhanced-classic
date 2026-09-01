#pragma once

#include <cstddef>
#include <cstring>
#include <iostream>
#include <windows.h>
#include "Memory.h"

namespace EverLeafEvanClientPatch {

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

inline unsigned char* FindUniqueEvanSkillGuard() {
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
        if (sectionSize < sizeof(kEvanSkillGuard)) {
            continue;
        }

        unsigned char* begin = base + section->VirtualAddress;
        const std::size_t last = sectionSize - sizeof(kEvanSkillGuard);
        for (std::size_t offset = 0; offset <= last; ++offset) {
            if (std::memcmp(begin + offset, kEvanSkillGuard, sizeof(kEvanSkillGuard)) == 0) {
                match = begin + offset;
                ++matches;
                if (matches > 1) {
                    return nullptr; // fail closed on an ambiguous executable
                }
            }
        }
    }

    return matches == 1 ? match : nullptr;
}

inline bool Apply() {
    unsigned char* guard = FindUniqueEvanSkillGuard();
    if (!guard) {
        std::cerr << "EverLeaf Evan client patch: expected unique CSkillInfo::GetSkill signature was not found; no bytes changed." << std::endl;
        return false;
    }

    // Re-check immediately before writing so a changed or already-patched
    // executable cannot be modified at the wrong location.
    if (std::memcmp(guard, kEvanSkillGuard, sizeof(kEvanSkillGuard)) != 0) {
        std::cerr << "EverLeaf Evan client patch: signature changed before write; no bytes changed." << std::endl;
        return false;
    }

    Memory::FillBytes(reinterpret_cast<DWORD>(guard), 0x90, static_cast<int>(sizeof(kEvanSkillGuard)));
    std::cout << "EverLeaf Evan client patch: unlocked CSkillInfo::GetSkill Evan path." << std::endl;
    return true;
}

// The executable is fully mapped before the proxy dinput8 DLL initializes.
// An inline variable ensures this executes once even though stdafx.h is shared.
struct AutoApply {
    AutoApply() { Apply(); }
};

inline AutoApply g_autoApply;

} // namespace EverLeafEvanClientPatch
