#include "stdafx.h"
#include "AddyLocations.h"
#include "EverLeafLoginLayout.h"
#include "MainMain.h"

namespace {
    // EverLeaf's live signboard keeps the original v83 control geometry: the
    // ID/password fields are stacked vertically and the stock button offsets
    // already match the 368x236 panel artwork. Only the parent dialog is moved
    // into the centered widescreen position.
    __declspec(naked) void PositionEverLeafLoginDlg() {
        __asm {
            push 0x000000B4
            push 400
            push -48
            push -185
            jmp dword ptr[dwLoginCreateDlgRtn]
        }
    }

    __declspec(naked) void PositionEverLeafLoginUsername() {
        __asm {
            push 0x0F
            push 0x00000084
            push 12
            push 67
            jmp dword ptr[dwLoginUsernameRtn]
        }
    }

    __declspec(naked) void PositionEverLeafLoginPassword() {
        __asm {
            push 0x0F
            push 0x78
            push 40
            push 67
            jmp dword ptr[dwLoginPasswordRtn]
        }
    }

    struct EverLeafLoginLayoutDefaults {
        EverLeafLoginLayoutDefaults() {
            // Keep the existing full-width login-frame behavior. The current
            // production WZ already contains the EverLeaf panel/panorama.
            MainMain::bigLoginFrame = true;
        }
    } gEverLeafLoginLayoutDefaults;
}

void EverLeafLoginLayout::Apply() {
    Memory::CodeCave(PositionEverLeafLoginDlg, dwLoginCreateDlg, 14);
    Memory::CodeCave(PositionEverLeafLoginUsername, dwLoginUsername, 11);
    Memory::CodeCave(PositionEverLeafLoginPassword, dwLoginPassword, 8);

    // Match the dark inset fields already painted into the EverLeaf signboard.
    Memory::WriteInt(dwLoginInputBackgroundColor + 3, 0xFF171B0E);
    Memory::WriteByte(dwLoginInputFontColor + 3, 0);
}
