#include "stdafx.h"
#include "Memory.h"
#include "detours.h"
//#pragma optimize("", off) //non-optimized function for testing purposes
bool Memory::UseVirtuProtect = true;

namespace {
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
    if (UseVirtuProtect) {
        DWORD dwOldProtect;
        VirtualProtect((LPVOID)dwOriginAddress, nCount, PAGE_EXECUTE_READWRITE, &dwOldProtect); //thanks colaMint, joo, and stelmo for informing me of using virtualprotect
        memset((void*)dwOriginAddress, ucValue, nCount);
        VirtualProtect((LPVOID)dwOriginAddress, nCount, dwOldProtect, &dwOldProtect);
    }
    else { memset((void*)dwOriginAddress, ucValue, nCount); }
}

void Memory::WriteString(const DWORD dwOriginAddress, const char* sContent) {
    const size_t nSize = strlen(sContent);
    if (UseVirtuProtect) {
        DWORD dwOldProtect;
        VirtualProtect((LPVOID)dwOriginAddress, nSize, PAGE_EXECUTE_READWRITE, &dwOldProtect);
        memcpy((void*)dwOriginAddress, sContent, nSize);
        VirtualProtect((LPVOID)dwOriginAddress, nSize, dwOldProtect, &dwOldProtect);
    }
    else { memcpy((void*)dwOriginAddress, sContent, nSize); }
}

void Memory::WriteByte(const DWORD dwOriginAddress, const unsigned char ucValue) {
    if (UseVirtuProtect) {
        DWORD dwOldProtect;
        VirtualProtect((LPVOID)dwOriginAddress, sizeof(unsigned char), PAGE_EXECUTE_READWRITE, &dwOldProtect);
        *(unsigned char*)dwOriginAddress = ucValue;
        VirtualProtect((LPVOID)dwOriginAddress, sizeof(unsigned char), dwOldProtect, &dwOldProtect);
    }
    else { *(unsigned char*)dwOriginAddress = ucValue; }
}

void Memory::WriteShort(const DWORD dwOriginAddress, const unsigned short usValue) {
    if (UseVirtuProtect) {
        DWORD dwOldProtect;
        VirtualProtect((LPVOID)dwOriginAddress, sizeof(unsigned short), PAGE_EXECUTE_READWRITE, &dwOldProtect);
        *(unsigned short*)dwOriginAddress = usValue;
        VirtualProtect((LPVOID)dwOriginAddress, sizeof(unsigned short), dwOldProtect, &dwOldProtect);
    }
    else { *(unsigned short*)dwOriginAddress = usValue; }
}

void Memory::WriteInt(const DWORD dwOriginAddress, const unsigned int dwValue) {
    if (UseVirtuProtect) {
        DWORD dwOldProtect;
        VirtualProtect((LPVOID)dwOriginAddress, sizeof(unsigned int), PAGE_EXECUTE_READWRITE, &dwOldProtect);
        *(unsigned int*)dwOriginAddress = dwValue;
        VirtualProtect((LPVOID)dwOriginAddress, sizeof(unsigned int), dwOldProtect, &dwOldProtect);
    }
    else { *(unsigned int*)dwOriginAddress = dwValue; }
}

void Memory::WriteDouble(const DWORD dwOriginAddress, const double dwValue) {
    if (UseVirtuProtect) {
        DWORD dwOldProtect;
        VirtualProtect((LPVOID)dwOriginAddress, sizeof(double), PAGE_EXECUTE_READWRITE, &dwOldProtect);
        *(double*)dwOriginAddress = dwValue;
        VirtualProtect((LPVOID)dwOriginAddress, sizeof(double), dwOldProtect, &dwOldProtect);
    }
    else { *(double*)dwOriginAddress = dwValue; }

    // Client::UpdateGameStartup writes the damage cap after unpacking, giving us
    // a stable one-time point to install the EverLeaf combat QoL patches.
    if (dwOriginAddress == 0x00AFE8A0) {
        ApplyEverLeafCombatQolPatches();
    }
}

void Memory::WriteByteArray(const DWORD dwOriginAddress, unsigned char* ucValue, const int ucValueSize) {
    const size_t nSize = sizeof(ucValue);
    if (UseVirtuProtect) {
        for (int i = 0; i < ucValueSize; i++) {
            const DWORD newAddr = dwOriginAddress + i;
            DWORD dwOldProtect;
            VirtualProtect((LPVOID)newAddr, sizeof(unsigned char), PAGE_EXECUTE_READWRITE, &dwOldProtect);
            *(unsigned char*)newAddr = ucValue[i];
            VirtualProtect((LPVOID)newAddr, sizeof(unsigned char), dwOldProtect, &dwOldProtect);
        }
    }
    else {
        for (int i = 0; i < ucValueSize; i++) { const DWORD newAddr = dwOriginAddress + i; *(unsigned char*)newAddr = ucValue[i]; }
    }
}

void Memory::CodeCave(void* ptrCodeCave, const DWORD dwOriginAddress, const int nNOPCount) { //tested and working
	__try {
		if (nNOPCount) FillBytes(dwOriginAddress, 0x90, nNOPCount); // create space for the jmp
		WriteByte(dwOriginAddress, 0xe9); // jmp instruction
		WriteInt(dwOriginAddress + 1, (int)(((int)ptrCodeCave - (int)dwOriginAddress) - 5)); // [jmp(1 byte)][address(4 bytes)] //this means you need to clear a space of at least 5 bytes (nNOPCount bytes)
	} __except (EXCEPTION_EXECUTE_HANDLER) {}
}
//#pragma optimize("", on)