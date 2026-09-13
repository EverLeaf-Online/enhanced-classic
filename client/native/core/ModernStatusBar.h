#pragma once

// EverLeaf modern StatusBar quickslot compatibility for the v83 client.
// The geometry/buffer expansion is derived from the public MapleRoot v83
// expanded-quickslot implementation and kept byte-compatible with the original
// client structures.  v180 StatusBar2/3 supplies the visible HUD assets.
namespace EverLeafModernStatusBar {

static unsigned char Array_aDefaultQKM[] = {
	42, 0, 0, 0,
	82, 0, 0, 0,
	71, 0, 0, 0,
	73, 0, 0, 0,
	2, 0, 0, 0,
	3, 0, 0, 0,
	4, 0, 0, 0,
	5, 0, 0, 0,
	6, 0, 0, 0,
	30, 0, 0, 0,
	31, 0, 0, 0,
	32, 0, 0, 0,
	33, 0, 0, 0,
	29, 0, 0, 0,
	83, 0, 0, 0,
	79, 0, 0, 0,
	81, 0, 0, 0,
	16, 0, 0, 0,
	17, 0, 0, 0,
	18, 0, 0, 0,
	19, 0, 0, 0,
	20, 0, 0, 0,
	44, 0, 0, 0,
	45, 0, 0, 0,
	46, 0, 0, 0,
	47, 0, 0, 0,
	52, 0, 0, 0
};

static unsigned char Array_ptShortKeyPos[] = {
	7, 0, 0, 0,
	8, 0, 0, 0,
	42, 0, 0, 0,
	8, 0, 0, 0,
	77, 0, 0, 0,
	8, 0, 0, 0,
	112, 0, 0, 0,
	8, 0, 0, 0,
	147, 0, 0, 0,
	8, 0, 0, 0,
	182, 0, 0, 0,
	8, 0, 0, 0,
	217, 0, 0, 0,
	8, 0, 0, 0,
	252, 0, 0, 0,
	8, 0, 0, 0,
	287, 1, 0, 0,
	8, 0, 0, 0,
	322, 1, 0, 0,
	8, 0, 0, 0,
	357, 1, 0, 0,
	8, 0, 0, 0,
	392, 1, 0, 0,
	8, 0, 0, 0,
	427, 1, 0, 0,
	8, 0, 0, 0,
	7, 0, 0, 0,
	41, 0, 0, 0,
	42, 0, 0, 0,
	41, 0, 0, 0,
	77, 0, 0, 0,
	41, 0, 0, 0,
	112, 0, 0, 0,
	41, 0, 0, 0,
	147, 0, 0, 0,
	41, 0, 0, 0,
	182, 0, 0, 0,
	41, 0, 0, 0,
	217, 0, 0, 0,
	41, 0, 0, 0,
	252, 0, 0, 0,
	41, 0, 0, 0,
	287, 1, 0, 0,
	41, 0, 0, 0,
	322, 1, 0, 0,
	41, 0, 0, 0,
	357, 1, 0, 0,
	41, 0, 0, 0,
	392, 1, 0, 0,
	41, 0, 0, 0,
	427, 1, 0, 0,
	41, 0, 0, 0
};

static unsigned char Array_ptShortKeyPos_Fixed_Tooltips[] = {
	7,0,0,0,0,0,0,0,42,0,0,0,0,0,0,0,77,0,0,0,0,0,0,0,112,0,0,0,0,0,0,0,147,0,0,0,0,0,0,0,182,0,0,0,0,0,0,0,217,0,0,0,0,0,0,0,252,0,0,0,0,0,0,0,287,1,0,0,0,0,0,0,322,1,0,0,0,0,0,0,357,1,0,0,0,0,0,0,392,1,0,0,0,0,0,0,427,1,0,0,0,0,0,0,7,0,0,0,33,0,0,0,42,0,0,0,33,0,0,0,77,0,0,0,33,0,0,0,112,0,0,0,33,0,0,0,147,0,0,0,33,0,0,0,182,0,0,0,33,0,0,0,217,0,0,0,33,0,0,0,252,0,0,0,33,0,0,0,287,1,0,0,33,0,0,0,322,1,0,0,33,0,0,0,357,1,0,0,33,0,0,0,392,1,0,0,33,0,0,0,427,1,0,0,33,0,0,0
};

static unsigned char Array_aDefaultQKM_0[] = {
	42, 0, 0, 0,
	82, 0, 0, 0,
	71, 0, 0, 0,
	73, 0, 0, 0, //4
	29, 0, 0, 0,
	83, 0, 0, 0,
	79, 0, 0, 0,
	81, 0, 0, 0, //8
	42, 0, 0, 0,
	82, 0, 0, 0,
	71, 0, 0, 0,
	73, 0, 0, 0, //12
	29, 0, 0, 0,
	83, 0, 0, 0,
	79, 0, 0, 0,
	81, 0, 0, 0, //16
	84, 0, 0, 0,
	85, 0, 0, 0,
	86, 0, 0, 0,
	87, 0, 0, 0, //20
	88, 0, 0, 0,
	89, 0, 0, 0,
	29, 0, 0, 0,
	29, 0, 0, 0, //24
	29, 0, 0, 0,
	29, 0, 0, 0,
	29, 0, 0, 0,
};

static unsigned char Array_Expanded[312] = { 4, 4, 0, 0,
	0, 0, 0, 0,
	0, 0, 0, 0,
	4, 0, 0, 0,
	0, 0, 0, 0,
	0, 0, 0, 0,
	4, 1, 0, 0,
	0, 0, 0, 0,
	0, 0, 0, 0,
	4, 2, 0, 0,
	0, 0, 0, 0,
	0, 0, 0, 0,
	4, 3, 0, 0,
	0, 0, 0, 0,
	0, 0, 0, 0,
	4, 5, 0, 0,
	0, 0, 0, 0,
	0, 0, 0, 0,
	4, 6, 0, 0,
	0, 0, 0, 0,
	0, 0, 0, 0,
	4, 7, 0, 0,
	0, 0, 0, 0,
	0, 0, 0, 0,
	4, 8, 0, 0,
	0, 0, 0, 0,
	0, 0, 0, 0,
	4, 10, 0, 0,
	0, 0, 0, 0,
	0, 0, 0, 0,
	4, 11, 0, 0,
	0, 0, 0, 0,
	0, 0, 0, 0,
	4, 12, 0, 0,
	0, 0, 0, 0,
	0, 0, 0, 0,
	4, 13, 0, 0,
	0, 0, 0, 0,
	0, 0, 0, 0,
	4, 14, 0, 0,
	0, 0, 0, 0,
	0, 0, 0, 0,
	4, 15, 0, 0,
	0, 0, 0, 0,
	0, 0, 0, 0,
	4, 16, 0, 0,
	0, 0, 0, 0,
	0, 0, 0, 0,
	4, 17, 0, 0,
	0, 0, 0, 0,
	0, 0, 0, 0,
	4, 23, 0, 0,
	0, 0, 0, 0,
	0, 0, 0, 0,
	4, 24, 0, 0,
	0, 0, 0, 0,
	0, 0, 0, 0,
	4, 25, 0, 0,
	0, 0, 0, 0,
	0, 0, 0, 0,
	4, 26, 0, 0,
	0, 0, 0, 0,
	0, 0, 0, 0,
	4, 27, 0, 0,
	0, 0, 0, 0,
	0, 0, 0, 0,
	5, 50, 0, 0,
	0, 0, 0, 0,
	0, 0, 0, 0,
	5, 51, 0, 0,
	0, 0, 0, 0,
	0, 0, 0, 0,
	5, 52, 0, 0,
	0, 0, 0, 0,
	0, 0, 0, 0,
	5, 53, 0, 0,
	0, 0, 0, 0,
	0, 0, 0, 0 };

static unsigned char Array_Expanded_Testing_Cooldown_fix[312] = { 0 };

static unsigned char cooldown_Array[124] = { 255, 255, 255, 255, 255, 255, 255, 255,255, 255, 255, 255,255, 255, 255, 255,255, 255, 255, 255,255, 255, 255, 255,255, 255, 255, 255,255, 255, 255, 255,255, 255, 255, 255,255, 255, 255, 255,255, 255, 255, 255,255, 255, 255, 255,255, 255, 255, 255,255, 255, 255, 255,255, 255, 255, 255,255, 255, 255, 255,255, 255, 255, 255,255, 255, 255, 255,255, 255, 255, 255,255, 255, 255, 255,255, 255, 255, 255,255, 255, 255, 255,255, 255, 255, 255,255, 255, 255, 255,255, 255, 255, 255,255, 255, 255, 255,255, 255, 255, 255,255, 255, 255, 255 };

static_assert(sizeof(Array_ptShortKeyPos) == 26 * 2 * sizeof(DWORD), "26-slot quickslot geometry must contain 26 POINTs");
static_assert(sizeof(Array_ptShortKeyPos_Fixed_Tooltips) == 26 * 2 * sizeof(DWORD), "tooltip geometry must contain 26 POINTs");
static_assert(sizeof(Array_Expanded) == 26 * 12, "expanded quickslot cache must contain 26 entries");

static DWORD Array_aDefaultQKM_Address = (DWORD)&Array_aDefaultQKM;
static DWORD Array_mystery_Address = (DWORD)&Array_Expanded;
static DWORD Array_mystery_Address_plus = (DWORD)&Array_Expanded + 1;
static DWORD cooldown_Array_Address = (DWORD)&cooldown_Array;
static DWORD Array_Expanded_Testing_Cooldown_fix_Address = (DWORD)&Array_Expanded_Testing_Cooldown_fix;

static DWORD CompareValidate_Retn = 0x008DD8BD;
__declspec(naked) static void CompareValidateFuncKeyMappedInfo_cave()
{
    __asm {
        push 0x138
        push 0x0
        push eax
        pushad
        popad
        jmp dword ptr [CompareValidate_Retn]
    }
}

static DWORD sub_9FA0CB_cave_retn_1 = 0x009FA0E1;
__declspec(naked) static void sub_9FA0CB_cave()
{
    __asm {
        test eax, eax
        jne already_allocated
        push 0xD4
        pushad
        popad
        jmp dword ptr [sub_9FA0CB_cave_retn_1]
    already_allocated:
        push 0x138
        push 0x0
        push eax
        pushad
        popad
        jmp dword ptr [CompareValidate_Retn]
    }
}

__declspec(naked) static void sDefaultQuickslotKeyMap_cave()
{
    __asm {
        push ebx
        push esi
        push edi
        xor edx, edx
        mov ebx, ecx
        call original_prefix
        nop
        lea edi, dword ptr ds:[ebx + 0x4]
        mov ecx, 0x1A
        mov esi, Array_aDefaultQKM_Address
        rep movsd
        lea edi, dword ptr ds:[ebx + 0x6C]
        mov ecx, 0x1A
        mov esi, Array_aDefaultQKM_Address
        rep movsd
        pop edi
        pop esi
        pop ebx
        ret
    original_prefix:
        push esi
        mov esi, ecx
        lea eax, dword ptr ds:[esi + 0x4]
        push 0x0072B7C2
        ret
    }
}

__declspec(naked) static void DefaultQuickslotKeyMap_cave()
{
    __asm {
        push esi
        push edi
        lea eax, dword ptr ds:[ecx + 0x4]
        mov esi, Array_aDefaultQKM_Address
        mov ecx, 0x1A
        mov edi, eax
        rep movsd
        pop edi
        pop esi
        ret
    }
}

__declspec(naked) static void Restore_Array_Expanded()
{
    __asm {
        lea eax, [esi + 0x0D7C]
        push esi
        push edi
        push ecx
        mov esi, [Array_Expanded_Testing_Cooldown_fix_Address]
        mov edi, Array_mystery_Address
        mov ecx, 78
        rep movsd
        pop ecx
        pop edi
        pop esi
        push 0x008CFE03
        ret
    }
}

static void Install()
{
    static bool installed = false;
    if (installed) return;
    installed = true;

    // CUIStatusBar::OnCreate: expose the full modern quickslot/hotkey/cooldown area.
    Memory::WriteByte(0x008D155C + 1, 0xF0);
    Memory::WriteByte(0x008D155C + 2, 0x03);
    Memory::WriteByte(0x008D182E + 1, 0xF0);
    Memory::WriteByte(0x008D182E + 2, 0x03);
    Memory::WriteByte(0x008D1AC0 + 1, 0xF0);
    Memory::WriteByte(0x008D1AC0 + 2, 0x03);

    // CQuickslotKeyMappedMan default/expanded storage.
    Memory::WriteInt(0x0072B7CE + 1, (DWORD)&Array_aDefaultQKM_0);
    Memory::WriteInt(0x0072B8EB + 1, (DWORD)&Array_aDefaultQKM_0);

    // CUIStatusBar::CQuickSlot::CompareValidateFuncKeyMappedInfo.
    Memory::WriteByte(0x008DD916, 0x1A);
    Memory::WriteByte(0x008DD8AD, 0x1A);
    Memory::WriteByte(0x008DD8FD, 0xBB);
    Memory::WriteInt(0x008DD8FD + 1, (DWORD)&Array_Expanded);
    Memory::WriteByte(0x008DD8FD + 5, 0x90);
    Memory::WriteByte(0x008DD898, 0xB8);
    Memory::WriteInt(0x008DD898 + 1, (DWORD)&Array_Expanded);
    Memory::WriteByte(0x008DD898 + 5, 0x90);

    // CUIStatusBar::CQuickSlot::Draw + statusbar drag/hover mapping.
    Memory::WriteByte(0x008DE75E + 3, 0x6C);
    Memory::WriteByte(0x008DDF99, 0xB8);
    Memory::WriteInt(0x008DDF99 + 1, (DWORD)&Array_Expanded);
    Memory::FillBytes(0x008DDF99 + 5, 0x90, 3);
    Memory::WriteByte(0x008D7F1E + 1, 0x34);
    Memory::WriteByte(0x008D7F1E + 2, 0x85);
    Memory::WriteInt(0x008D7F1E + 3, (DWORD)&Array_Expanded);

    // 13x2 / 26-slot geometry and hit testing.
    Memory::WriteInt(0x008DE94D + 2, (DWORD)&Array_ptShortKeyPos);
    Memory::WriteInt(0x008DE955 + 2, (DWORD)&Array_ptShortKeyPos + 4);
    Memory::WriteByte(0x008DE941 + 2, 0x1A);
    Memory::WriteInt(0x008DE8F4 + 1, (DWORD)&Array_ptShortKeyPos_Fixed_Tooltips + 4);
    Memory::WriteByte(0x008DE926 + 1, 0x3E);

    // Expanded cooldown presentation.
    Memory::WriteByte(0x008E099F + 3, 0x1A);
    Memory::WriteByte(0x008E069D, 0xBE);
    Memory::WriteInt(0x008E069D + 1, (DWORD)&cooldown_Array);
    Memory::WriteByte(0x008E069D + 5, 0x90);
    Memory::WriteByte(0x008E06A3, 0xBF);
    Memory::WriteInt(0x008E06A3 + 1, (DWORD)&Array_Expanded + 1);
    Memory::WriteByte(0x008E06A3 + 5, 0x90);

    // Drag/drop and key-config persistence must expand with the HUD.
    Memory::WriteByte(0x004F928A + 2, 0x1A);
    Memory::WriteByte(0x004F93F9 + 2, 0x1A);
    Memory::WriteByte(0x00833797 + 2, 0x6C);
    Memory::WriteByte(0x00833841 + 2, 0x6C);
    Memory::WriteByte(0x00833791 + 1, 0x68);
    Memory::WriteByte(0x0083383B + 1, 0x68);
    Memory::WriteByte(0x0083287F + 2, 0x6C);
    Memory::WriteByte(0x00832882 + 1, 0x68);
    Memory::WriteByte(0x0072B8C0 + 2, 0x6C);
    Memory::WriteByte(0x0072B8A0 + 1, 0x68);
    Memory::WriteByte(0x0072B8BD + 1, 0x68);
    Memory::WriteByte(0x0072B861 + 1, 0x68);
    Memory::WriteByte(0x0072B867 + 2, 0x6C);
    Memory::WriteByte(0x00836A1E + 1, 0x68);
    Memory::WriteByte(0x00836A21 + 2, 0x6C);

    Memory::CodeCave(CompareValidateFuncKeyMappedInfo_cave, 0x008DD8B8, 5);
    Memory::CodeCave(sub_9FA0CB_cave, 0x009FA0DB, 5);
    Memory::CodeCave(sDefaultQuickslotKeyMap_cave, 0x0072B7BC, 5);
    Memory::CodeCave(DefaultQuickslotKeyMap_cave, 0x0072B8E6, 5);
    Memory::CodeCave(Restore_Array_Expanded, 0x008CFDFD, 6);
}

} // namespace EverLeafModernStatusBar
