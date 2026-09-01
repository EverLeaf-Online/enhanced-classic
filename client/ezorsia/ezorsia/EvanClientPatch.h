#pragma once

#include <cstddef>
#include <cstdint>
#include <cstring>
#include <iostream>
#include <string>
#include <vector>
#include <windows.h>
#include "Memory.h"

namespace EverLeafEvanClientPatch {

// Blu3sky's v83 Evan release requires two independent client NOPs:
//   PatchNop(0x0075C783, 4)
//   PatchNop(0x00761714, 21)
//
// EverLeaf runs against a packed executable, so historical virtual addresses
// are not safe to write directly for code patches. Both code sites are located
// only after the executable is mapped, using signatures derived from EverLeaf's
// verified unpacked v83 localhost. The patch fails closed if either signature
// is absent or ambiguous.

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

// STREDIT's v83 StringPool locations. These are intentionally used only after
// the packed executable is mapped/unpacked in memory. The status bar currently
// exposes the internal beginner label "Evan0" for job 2001; official-facing UI
// should display simply "Evan". Every address and decoded value is validated
// before a single byte is changed.
inline constexpr std::uintptr_t kStringPoolTableAddress = 0x00A6F17C;
inline constexpr std::uintptr_t kStringPoolKeyAddress = 0x009E30C4;
inline constexpr std::uintptr_t kStringPoolKeySizeAddress = 0x009E30D4;
inline constexpr std::uintptr_t kStringPoolCountAddress = 0x009E30D8;
inline constexpr std::size_t kMaxStringPoolKeySize = 64;
inline constexpr std::uint32_t kMinStringPoolCount = 1000;
inline constexpr std::uint32_t kMaxStringPoolCount = 100000;
inline constexpr std::size_t kMaxDecodedPoolString = 512;

inline bool IsExecutableSection(const IMAGE_SECTION_HEADER& section) {
    return (section.Characteristics & IMAGE_SCN_MEM_EXECUTE) != 0;
}

inline bool IsReadableMemory(const void* address, std::size_t size) {
    if (!address || size == 0) {
        return false;
    }

    const auto start = reinterpret_cast<std::uintptr_t>(address);
    if (start + size < start) {
        return false;
    }

    std::uintptr_t current = start;
    const std::uintptr_t end = start + size;
    while (current < end) {
        MEMORY_BASIC_INFORMATION mbi{};
        if (VirtualQuery(reinterpret_cast<const void*>(current), &mbi, sizeof(mbi)) != sizeof(mbi)) {
            return false;
        }
        if (mbi.State != MEM_COMMIT || (mbi.Protect & (PAGE_NOACCESS | PAGE_GUARD)) != 0) {
            return false;
        }
        const DWORD readable = PAGE_READONLY | PAGE_READWRITE | PAGE_WRITECOPY |
                               PAGE_EXECUTE_READ | PAGE_EXECUTE_READWRITE | PAGE_EXECUTE_WRITECOPY;
        if ((mbi.Protect & readable) == 0) {
            return false;
        }
        const std::uintptr_t regionStart = reinterpret_cast<std::uintptr_t>(mbi.BaseAddress);
        const std::uintptr_t regionEnd = regionStart + mbi.RegionSize;
        if (regionEnd <= current) {
            return false;
        }
        current = regionEnd < end ? regionEnd : end;
    }
    return true;
}

inline bool IsAddressInsideMainImage(std::uintptr_t address, std::size_t size = 1) {
    HMODULE module = GetModuleHandleW(nullptr);
    if (!module || size == 0) {
        return false;
    }
    auto* base = reinterpret_cast<unsigned char*>(module);
    auto* dos = reinterpret_cast<IMAGE_DOS_HEADER*>(base);
    if (dos->e_magic != IMAGE_DOS_SIGNATURE) {
        return false;
    }
    auto* nt = reinterpret_cast<IMAGE_NT_HEADERS*>(base + dos->e_lfanew);
    if (nt->Signature != IMAGE_NT_SIGNATURE) {
        return false;
    }
    const std::uintptr_t imageStart = reinterpret_cast<std::uintptr_t>(base);
    const std::uintptr_t imageEnd = imageStart + nt->OptionalHeader.SizeOfImage;
    if (address < imageStart || address + size < address || address + size > imageEnd) {
        return false;
    }
    return IsReadableMemory(reinterpret_cast<const void*>(address), size);
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

inline std::vector<unsigned char> RotateStringPoolKey(const unsigned char* key, std::size_t length, signed char signedShift) {
    std::vector<unsigned char> rotated(key, key + length);
    const std::uint32_t shift = static_cast<std::uint32_t>(static_cast<std::int32_t>(signedShift));

    if (shift >= 8) {
        const std::size_t byteShift = static_cast<std::size_t>((shift >> 3) % length);
        if (byteShift != 0) {
            std::vector<unsigned char> original = rotated;
            for (std::size_t i = 0; i < length; ++i) {
                rotated[i] = original[(i + byteShift) % length];
            }
        }
    }

    const unsigned int bitShift = shift & 7U;
    if (bitShift != 0) {
        const unsigned int rightShift = 8U - bitShift;
        const unsigned char carry = length > 1 ? static_cast<unsigned char>(rotated[0] >> rightShift) : 0;
        for (std::size_t i = 0; i < length; ++i) {
            const unsigned char next = i + 1 < length ? static_cast<unsigned char>(rotated[i + 1] >> rightShift) : 0;
            rotated[i] = static_cast<unsigned char>((rotated[i] << bitShift) | next);
        }
        rotated[length - 1] = static_cast<unsigned char>(rotated[length - 1] | carry);
    }
    return rotated;
}

struct DecodedPoolEntry {
    bool valid = false;
    std::string value;
    unsigned char* encrypted = nullptr;
    std::vector<unsigned char> rotatedKey;
};

inline DecodedPoolEntry DecodePoolEntry(std::uint32_t index,
                                        std::uint32_t count,
                                        const unsigned char* key,
                                        std::size_t keySize) {
    DecodedPoolEntry result;
    if (index >= count || keySize == 0 || keySize > kMaxStringPoolKeySize) {
        return result;
    }

    const auto tableAddress = kStringPoolTableAddress + static_cast<std::uintptr_t>(index) * sizeof(std::uint32_t);
    if (!IsAddressInsideMainImage(tableAddress, sizeof(std::uint32_t))) {
        return result;
    }
    const std::uint32_t stringAddress = *reinterpret_cast<const std::uint32_t*>(tableAddress);
    if (!IsAddressInsideMainImage(stringAddress, 2)) {
        return result;
    }

    auto* cursor = reinterpret_cast<unsigned char*>(static_cast<std::uintptr_t>(stringAddress));
    const signed char shift = *reinterpret_cast<const signed char*>(cursor);
    ++cursor;
    result.rotatedKey = RotateStringPoolKey(key, keySize, shift);
    result.encrypted = cursor;

    for (std::size_t i = 0; i < kMaxDecodedPoolString; ++i) {
        const auto byteAddress = reinterpret_cast<std::uintptr_t>(cursor + i);
        if (!IsAddressInsideMainImage(byteAddress, 1)) {
            return DecodedPoolEntry{};
        }
        const unsigned char encrypted = cursor[i];
        if (encrypted == 0) {
            result.valid = true;
            return result;
        }
        const unsigned char keyByte = result.rotatedKey[i % keySize];
        const unsigned char plain = encrypted == keyByte ? keyByte : static_cast<unsigned char>(encrypted ^ keyByte);
        result.value.push_back(static_cast<char>(plain));
    }
    return DecodedPoolEntry{};
}

inline bool ApplyEvanBeginnerLabelPatch() {
    if (!IsAddressInsideMainImage(kStringPoolKeySizeAddress, sizeof(std::int32_t)) ||
        !IsAddressInsideMainImage(kStringPoolCountAddress, sizeof(std::uint32_t))) {
        std::cerr << "EverLeaf Evan client patch: v83 StringPool metadata is not mapped; Evan label left unchanged." << std::endl;
        return false;
    }

    const std::int32_t keySizeSigned = *reinterpret_cast<const std::int32_t*>(kStringPoolKeySizeAddress);
    const std::uint32_t count = *reinterpret_cast<const std::uint32_t*>(kStringPoolCountAddress);
    if (keySizeSigned <= 0 || static_cast<std::size_t>(keySizeSigned) > kMaxStringPoolKeySize ||
        count < kMinStringPoolCount || count > kMaxStringPoolCount) {
        std::cerr << "EverLeaf Evan client patch: v83 StringPool metadata failed validation; Evan label left unchanged." << std::endl;
        return false;
    }

    const std::size_t keySize = static_cast<std::size_t>(keySizeSigned);
    if (!IsAddressInsideMainImage(kStringPoolKeyAddress, keySize) ||
        !IsAddressInsideMainImage(kStringPoolTableAddress, static_cast<std::size_t>(count) * sizeof(std::uint32_t))) {
        std::cerr << "EverLeaf Evan client patch: v83 StringPool storage failed range validation; Evan label left unchanged." << std::endl;
        return false;
    }

    const auto* key = reinterpret_cast<const unsigned char*>(kStringPoolKeyAddress);
    std::uint32_t matchIndex = 0;
    DecodedPoolEntry match;
    std::size_t matches = 0;

    for (std::uint32_t index = 0; index < count; ++index) {
        DecodedPoolEntry entry = DecodePoolEntry(index, count, key, keySize);
        if (entry.valid && entry.value == "Evan0") {
            matchIndex = index;
            match = std::move(entry);
            ++matches;
            if (matches > 1) {
                break;
            }
        }
    }

    if (matches != 1 || !match.valid || !match.encrypted || match.rotatedKey.size() != keySize) {
        std::cerr << "EverLeaf Evan client patch: expected exactly one decoded Evan0 StringPool entry; Evan label left unchanged." << std::endl;
        return false;
    }

    constexpr char replacement[] = "Evan";
    unsigned char encoded[sizeof(replacement)]{};
    for (std::size_t i = 0; i < sizeof(replacement) - 1; ++i) {
        const unsigned char plain = static_cast<unsigned char>(replacement[i]);
        const unsigned char keyByte = match.rotatedKey[i % keySize];
        encoded[i] = plain == keyByte ? plain : static_cast<unsigned char>(plain ^ keyByte);
        if (encoded[i] == 0) {
            std::cerr << "EverLeaf Evan client patch: Evan replacement encoded to an unsafe null; label left unchanged." << std::endl;
            return false;
        }
    }
    encoded[sizeof(replacement) - 1] = 0;

    Memory::WriteByteArray(reinterpret_cast<DWORD>(match.encrypted), encoded, static_cast<int>(sizeof(encoded)));
    DecodedPoolEntry verify = DecodePoolEntry(matchIndex, count, key, keySize);
    if (!verify.valid || verify.value != "Evan") {
        std::cerr << "EverLeaf Evan client patch: Evan StringPool post-write verification failed." << std::endl;
        return false;
    }

    std::cout << "EverLeaf Evan client patch: normalized beginner status label Evan0 -> Evan (StringPool index "
              << matchIndex << ")." << std::endl;
    return true;
}

inline bool Apply() {
    // Keep these independent so logs identify exactly which v83 Evan guard was
    // rejected if a future executable changes. The DLL does not guess code offsets.
    const bool activation1 = ApplyActivation1Patch();
    const bool skillGuard = ApplySkillGuardPatch();
    const bool label = ApplyEvanBeginnerLabelPatch();
    return activation1 && skillGuard && label;
}

// The executable is fully mapped before the proxy dinput8 DLL initializes.
// An inline variable ensures this executes once even though stdafx.h is shared.
struct AutoApply {
    AutoApply() { Apply(); }
};

inline AutoApply g_autoApply;

} // namespace EverLeafEvanClientPatch
