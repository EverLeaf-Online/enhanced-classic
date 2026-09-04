#include "stdafx.h"
#include "Memory.h"
#include "detours.h"
//#pragma optimize("", off) //non-optimized function for testing purposes
bool Memory::UseVirtuProtect = true;

namespace {
    bool BeginPatch(const DWORD address, const size_t size, DWORD& oldProtect) {
        if (size == 0) {
            return false;
        }
        if (!Memory::UseVirtuProtect) {
            oldProtect = 0;
            return true;
        }
        return VirtualProtect(
            reinterpret_cast<LPVOID>(address),
            size,
            PAGE_EXECUTE_READWRITE,
            &oldProtect
        ) != FALSE;
    }

    void EndPatch(const DWORD address, const size_t size, const DWORD oldProtect) {
        if (Memory::UseVirtuProtect) {
            DWORD ignored = 0;
            VirtualProtect(
                reinterpret_cast<LPVOID>(address),
                size,
                oldProtect,
                &ignored
            );
        }

        // EverLeaf patches executable instructions after the packed v83 image
        // has unpacked. Windows requires the instruction cache to be flushed after
        // generated/modified code so all cores observe the new bytes reliably.
        FlushInstructionCache(
            GetCurrentProcess(),
            reinterpret_cast<LPCVOID>(address),
            size
        );
    }

    template <typename T>
    bool WritePatchedValue(const DWORD address, const T& value) {
        DWORD oldProtect = 0;
        if (!BeginPatch(address, sizeof(T), oldProtect)) {
            return false;
        }

        *reinterpret_cast<T*>(address) = value;
        EndPatch(address, sizeof(T), oldProtect);
        return true;
    }

    // Apply EverLeaf client-side combat QoL only after the packed v83 client has
    // unpacked and Client::UpdateGameStartup begins writing stable addresses.
    // Server-side combat/status validation remains authoritative.
    void ApplyEverLeafCombatQolPatches() {
        static bool applied = false;
        if (applied) {
            return;
        }
        applied = true;

        // No Whack: stop ranged weapons from falling back to the close-range
        // swing animation / fake local damage when a monster is nearby.
        Memory::WriteByte(0x009698BC, 0xE9);
        Memory::WriteInt(0x009698BC + 1, 0x00969A39 - (0x009698BC + 5));
        Memory::WriteByte(0x009516C2, 0xE9);
        Memory::WriteInt(0x009516C2 + 1, 0x0095138F - (0x009516C2 + 5));

        // No Breath: remove the legacy post-hit breath gate. This changes only
        // the client's generic breath comparison; stun/seal/knockback and other
        // actual status effects are still enforced by the normal client/server
        // state machinery.
        Memory::WriteByte(0x00452316, 0x7C);

        // Move while using skills: relax the three v83 action-state gates that
        // stop eligible attacks/skills while the local character is moving.
        // These exact instruction boundaries were verified against EverLeaf's
        // pinned v83 Localhost.exe before enabling the edits.
        Memory::WriteByte(0x0095F97A, 0xEB);
        Memory::WriteByte(0x0095F97B, 0x59);
        Memory::WriteByte(0x009CBFB0, 0xEB);
        Memory::FillBytes(0x0094C3BB, 0x90, 6);

        // Jump attack support for ranged and magic attacks. These retain the
        // existing destination blocks and only bypass the legacy airborne gate.
        Memory::WriteByte(0x009539FA, 0xEB);
        Memory::WriteByte(0x009559E5, 0xEB);
    }
}

bool Memory::SetHook(bool attach, void** ptrTarget, void* ptrDetour)
{
    if (DetourTransactionBegin() != NO_ERROR)
    {
        return false;
    }

    HANDLE pCurThread = GetCurrentThread();

    if (DetourUpdateThread(pCurThread) == NO_ERROR)
    {
        auto pDetourFunc = attach ? DetourAttach : DetourDetach;

        if (pDetourFunc(ptrTarget, ptrDetour) == NO_ERROR)
        {
            if (DetourTransactionCommit() == NO_ERROR)
            {
                return true;
            }
        }
    }

    DetourTransactionAbort();
    return false;
}

void Memory::FillBytes(const DWORD dwOriginAddress, const unsigned char ucValue, const int nCount) {
    if (nCount <= 0) {
        return;
    }

    const size_t size = static_cast<size_t>(nCount);
    DWORD oldProtect = 0;
    if (!BeginPatch(dwOriginAddress, size, oldProtect)) {
        return;
    }

    memset(reinterpret_cast<void*>(dwOriginAddress), ucValue, size);
    EndPatch(dwOriginAddress, size, oldProtect);
}

void Memory::WriteString(const DWORD dwOriginAddress, const char* sContent) {
    if (!sContent) {
        return;
    }

    const size_t nSize = strlen(sContent);
    if (nSize == 0) {
        return;
    }

    DWORD oldProtect = 0;
    if (!BeginPatch(dwOriginAddress, nSize, oldProtect)) {
        return;
    }

    memcpy(reinterpret_cast<void*>(dwOriginAddress), sContent, nSize);
    EndPatch(dwOriginAddress, nSize, oldProtect);
}

void Memory::WriteByte(const DWORD dwOriginAddress, const unsigned char ucValue) {
    WritePatchedValue(dwOriginAddress, ucValue);
}

void Memory::WriteShort(const DWORD dwOriginAddress, const unsigned short usValue) {
    WritePatchedValue(dwOriginAddress, usValue);
}

void Memory::WriteInt(const DWORD dwOriginAddress, const unsigned int dwValue) {
    WritePatchedValue(dwOriginAddress, dwValue);
}

void Memory::WriteDouble(const DWORD dwOriginAddress, const double dwValue) {
    const bool written = WritePatchedValue(dwOriginAddress, dwValue);

    // Client::UpdateGameStartup writes the damage cap after unpacking, giving us
    // a stable one-time point to install the EverLeaf combat QoL patches.
    if (written && dwOriginAddress == 0x00AFE8A0) {
        ApplyEverLeafCombatQolPatches();
    }
}

void Memory::WriteByteArray(const DWORD dwOriginAddress, unsigned char* ucValue, const int ucValueSize) {
    if (!ucValue || ucValueSize <= 0) {
        return;
    }

    const size_t size = static_cast<size_t>(ucValueSize);
    DWORD oldProtect = 0;
    if (!BeginPatch(dwOriginAddress, size, oldProtect)) {
        return;
    }

    // Patch the byte sequence as one protected region instead of changing page
    // permissions and writing one byte at a time. This sharply reduces the window
    // in which another thread could observe a partially protected patch region.
    memcpy(reinterpret_cast<void*>(dwOriginAddress), ucValue, size);
    EndPatch(dwOriginAddress, size, oldProtect);
}

void Memory::CodeCave(void* ptrCodeCave, const DWORD dwOriginAddress, const int nNOPCount) { //tested and working
	__try {
		if (nNOPCount) FillBytes(dwOriginAddress, 0x90, nNOPCount); // create space for the jmp
		WriteByte(dwOriginAddress, 0xe9); // jmp instruction
		WriteInt(dwOriginAddress + 1, (int)(((int)ptrCodeCave - (int)dwOriginAddress) - 5)); // [jmp(1 byte)][address(4 bytes)] //this means you need to clear a space of at least 5 bytes (nNOPCount bytes)
	} __except (EXCEPTION_EXECUTE_HANDLER) {}
}
//#pragma optimize("", on)