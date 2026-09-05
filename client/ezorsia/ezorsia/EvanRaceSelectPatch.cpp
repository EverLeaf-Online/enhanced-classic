#include "stdafx.h"
#include "EvanRaceSelectPatch.h"
#include <windowsx.h>
#ifdef min
#undef min
#endif
#ifdef max
#undef max
#endif
#include "Memory.h"
#include <algorithm>
#include <array>
#include <cstring>

namespace EverLeafEvanRaceSelect {

#if defined(_M_IX86)

namespace {
constexpr DWORD kRaceSelectEntry = 0x005F569D;
constexpr DWORD kRaceSelectEntryReturn = 0x005F56A7;
constexpr DWORD kCreatePacketRacePush = 0x005F7F04;
constexpr DWORD kCreatePacketRacePushReturn = 0x005F7F0A;

constexpr unsigned char kRaceSelectEntryBytes[] = {
    0xC7, 0x86, 0x14, 0x02, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00
};
constexpr unsigned char kCreatePacketRacePushBytes[] = {
    0xFF, 0xB6, 0x14, 0x02, 0x00, 0x00
};

DWORD gRaceSelectEntryReturn = kRaceSelectEntryReturn;
DWORD gCreatePacketRacePushReturn = kCreatePacketRacePushReturn;
volatile LONG gEvanMode = 0;
BYTE* gLogin = nullptr;
HWND gOverlay = nullptr;
HWND gGameWindow = nullptr;
bool gInstalled = false;
int gHoveredCard = -1;
const wchar_t* kWindowClass = L"EverLeafClassFamilySelector";

struct Card {
    int race;
    bool enabled;
    const wchar_t* title;
    const wchar_t* subtitle;
};

constexpr std::array<Card, 8> kCards = {{
    {0, true,  L"CYGNUS KNIGHTS", L"Dawn Warrior, Blaze Wizard, and more"},
    {1, true,  L"EXPLORERS",      L"Warrior, Magician, Bowman, Thief, Pirate"},
    {2, true,  L"ARAN",           L"Legendary polearm hero"},
    {3, true,  L"EVAN",           L"Dragon Master"},
    {-1, false, L"DUAL BLADE",    L"Locked until the sub-job client is ready"},
    {-1, false, L"RESISTANCE",    L"Locked until the resistance client is ready"},
    {-1, false, L"BATTLE MAGE",   L"Locked for a future class update"},
    {-1, false, L"WILD HUNTER",   L"Locked for a future class update"},
}};

bool BytesMatch(DWORD address, const unsigned char* expected, size_t length) {
    __try {
        return std::memcmp(reinterpret_cast<const void*>(address), expected, length) == 0;
    } __except (EXCEPTION_EXECUTE_HANDLER) {
        return false;
    }
}

BOOL CALLBACK FindGameWindowProc(HWND hwnd, LPARAM param) {
    DWORD pid = 0;
    GetWindowThreadProcessId(hwnd, &pid);
    if (pid != GetCurrentProcessId() || !IsWindowVisible(hwnd) || GetWindow(hwnd, GW_OWNER)) return TRUE;
    *reinterpret_cast<HWND*>(param) = hwnd;
    return FALSE;
}

HWND FindGameWindow() {
    HWND foreground = GetForegroundWindow();
    if (foreground) {
        DWORD pid = 0;
        GetWindowThreadProcessId(foreground, &pid);
        if (pid == GetCurrentProcessId()) return foreground;
    }
    HWND result = nullptr;
    EnumWindows(FindGameWindowProc, reinterpret_cast<LPARAM>(&result));
    return result;
}

void PositionOverlay() {
    if (!gOverlay || !gGameWindow) return;
    RECT rc{};
    if (!GetClientRect(gGameWindow, &rc)) return;
    const int clientWidth = rc.right - rc.left;
    const int clientHeight = rc.bottom - rc.top;
    const int width = std::max(620, std::min(780, clientWidth - 14));
    const int height = std::max(480, std::min(588, clientHeight - 8));
    const int x = std::max(7, (clientWidth - width) / 2);
    const int y = std::max(4, (clientHeight - height) / 2);
    SetWindowPos(gOverlay, HWND_TOP, x, y, width, height, SWP_NOACTIVATE | SWP_SHOWWINDOW);
}

std::array<RECT, 8> CardRects(const RECT& rc) {
    const int w = rc.right - rc.left;
    const int gap = 8;
    const int left = 12;
    const int right = w - 12;
    const int top = 52;
    const int availableHeight = static_cast<int>(rc.bottom - rc.top);
    const int topHeight = std::min(246, std::max(212, availableHeight / 2 - 42));
    const int smallTop = top + topHeight + 12;
    const int smallHeight = std::max(132, availableHeight - smallTop - 14);
    std::array<RECT, 8> cards{};
    const int topWidth = (right - left - gap * 2) / 3;
    for (int i = 0; i < 3; ++i) {
        cards[i] = {left + i * (topWidth + gap), top,
                    left + i * (topWidth + gap) + topWidth, top + topHeight};
    }
    const int smallWidth = (right - left - gap * 4) / 5;
    for (int i = 0; i < 5; ++i) {
        cards[i + 3] = {left + i * (smallWidth + gap), smallTop,
                        left + i * (smallWidth + gap) + smallWidth, smallTop + smallHeight};
    }
    return cards;
}

void DrawCard(HDC dc, const RECT& box, const Card& card, bool hovered) {
    const bool enabled = card.enabled;
    const COLORREF outer = enabled ? (hovered ? RGB(225, 205, 111) : RGB(127, 160, 89)) : RGB(91, 96, 87);
    const COLORREF fill = enabled ? (hovered ? RGB(73, 104, 56) : RGB(45, 70, 48)) : RGB(47, 50, 48);
    HBRUSH brush = CreateSolidBrush(fill);
    HPEN pen = CreatePen(PS_SOLID, hovered ? 3 : 2, outer);
    HGDIOBJ oldBrush = SelectObject(dc, brush);
    HGDIOBJ oldPen = SelectObject(dc, pen);
    RoundRect(dc, box.left, box.top, box.right, box.bottom, 16, 16);
    SelectObject(dc, oldPen); SelectObject(dc, oldBrush);
    DeleteObject(pen); DeleteObject(brush);

    RECT stripe = box;
    stripe.left += 5; stripe.right -= 5; stripe.top += 5; stripe.bottom = stripe.top + 7;
    HBRUSH stripeBrush = CreateSolidBrush(enabled ? RGB(190, 220, 102) : RGB(115, 119, 110));
    FillRect(dc, &stripe, stripeBrush);
    DeleteObject(stripeBrush);

    SetBkMode(dc, TRANSPARENT);
    SetTextColor(dc, enabled ? RGB(250, 245, 215) : RGB(174, 176, 168));
    const int titleSize = (box.right - box.left) > 190 ? 20 : 14;
    HFONT titleFont = CreateFontW(titleSize, 0, 0, 0, FW_BOLD, FALSE, FALSE, FALSE,
        DEFAULT_CHARSET, OUT_DEFAULT_PRECIS, CLIP_DEFAULT_PRECIS, ANTIALIASED_QUALITY,
        DEFAULT_PITCH, L"Arial");
    HFONT oldFont = reinterpret_cast<HFONT>(SelectObject(dc, titleFont));
    RECT title = box; title.top += 18; title.bottom = title.top + titleSize + 12;
    DrawTextW(dc, card.title, -1, &title, DT_CENTER | DT_WORDBREAK | DT_NOPREFIX);
    SelectObject(dc, oldFont); DeleteObject(titleFont);

    SetTextColor(dc, enabled ? RGB(218, 235, 182) : RGB(157, 160, 153));
    HFONT bodyFont = CreateFontW((box.right - box.left) > 190 ? 12 : 10, 0, 0, 0,
        FW_NORMAL, FALSE, FALSE, FALSE, DEFAULT_CHARSET, OUT_DEFAULT_PRECIS,
        CLIP_DEFAULT_PRECIS, ANTIALIASED_QUALITY, DEFAULT_PITCH, L"Arial");
    oldFont = reinterpret_cast<HFONT>(SelectObject(dc, bodyFont));
    RECT body = box; body.left += 9; body.right -= 9; body.top += (box.bottom - box.top) / 2;
    body.bottom -= enabled ? 35 : 24;
    DrawTextW(dc, card.subtitle, -1, &body, DT_CENTER | DT_WORDBREAK | DT_NOPREFIX);
    if (!enabled) {
        SetTextColor(dc, RGB(214, 194, 120));
        RECT lock = box; lock.bottom -= 8; lock.top = lock.bottom - 18;
        DrawTextW(dc, L"LOCKED", -1, &lock, DT_CENTER | DT_SINGLELINE | DT_VCENTER);
    } else {
        SetTextColor(dc, RGB(238, 244, 209));
        RECT ready = box; ready.bottom -= 8; ready.top = ready.bottom - 18;
        DrawTextW(dc, L"AVAILABLE", -1, &ready, DT_CENTER | DT_SINGLELINE | DT_VCENTER);
    }
    SelectObject(dc, oldFont); DeleteObject(bodyFont);
}

void SelectCard(int index) {
    if (!gLogin || index < 0 || index >= static_cast<int>(kCards.size())) return;
    const Card& card = kCards[index];
    if (!card.enabled || card.race < 0) return;
    *reinterpret_cast<volatile int*>(gLogin + 0x214) = card.race;
    *reinterpret_cast<volatile int*>(gLogin + 0x238) = 1;
    *reinterpret_cast<volatile int*>(gLogin + 0x23C) = 1;
    InterlockedExchange(&gEvanMode, card.race == 3 ? 1 : 0);
    if (gOverlay) ShowWindow(gOverlay, SW_HIDE);
    if (gGameWindow) { SetFocus(gGameWindow); PostMessageW(gGameWindow, WM_NULL, 0, 0); }
}

LRESULT CALLBACK SelectorWndProc(HWND hwnd, UINT msg, WPARAM wParam, LPARAM lParam) {
    switch (msg) {
    case WM_ERASEBKGND: return 1;
    case WM_MOUSEMOVE: {
        RECT rc{}; GetClientRect(hwnd, &rc);
        auto cards = CardRects(rc);
        POINT p{GET_X_LPARAM(lParam), GET_Y_LPARAM(lParam)};
        int next = -1;
        for (int i = 0; i < static_cast<int>(cards.size()); ++i)
            if (PtInRect(&cards[i], p) && kCards[i].enabled) { next = i; break; }
        if (next != gHoveredCard) { gHoveredCard = next; InvalidateRect(hwnd, nullptr, FALSE); }
        return 0;
    }
    case WM_LBUTTONUP: {
        RECT rc{}; GetClientRect(hwnd, &rc);
        auto cards = CardRects(rc);
        POINT p{GET_X_LPARAM(lParam), GET_Y_LPARAM(lParam)};
        for (int i = 0; i < static_cast<int>(cards.size()); ++i)
            if (PtInRect(&cards[i], p)) { SelectCard(i); return 0; }
        return 0;
    }
    case WM_SETCURSOR: SetCursor(LoadCursor(nullptr, IDC_HAND)); return TRUE;
    case WM_PAINT: {
        PAINTSTRUCT ps{}; HDC dc = BeginPaint(hwnd, &ps);
        RECT rc{}; GetClientRect(hwnd, &rc);
        HBRUSH bg = CreateSolidBrush(RGB(21, 34, 27));
        FillRect(dc, &rc, bg); DeleteObject(bg);
        HPEN border = CreatePen(PS_SOLID, 2, RGB(191, 171, 93));
        HGDIOBJ oldPen = SelectObject(dc, border);
        HGDIOBJ oldBrush = SelectObject(dc, GetStockObject(NULL_BRUSH));
        RoundRect(dc, 1, 1, rc.right - 1, rc.bottom - 1, 18, 18);
        SelectObject(dc, oldBrush); SelectObject(dc, oldPen); DeleteObject(border);
        SetBkMode(dc, TRANSPARENT); SetTextColor(dc, RGB(244, 235, 190));
        HFONT heading = CreateFontW(25, 0, 0, 0, FW_BOLD, FALSE, FALSE, FALSE,
            DEFAULT_CHARSET, OUT_DEFAULT_PRECIS, CLIP_DEFAULT_PRECIS, ANTIALIASED_QUALITY,
            DEFAULT_PITCH, L"Arial");
        HGDIOBJ oldFont = SelectObject(dc, heading);
        RECT title{10, 10, rc.right - 10, 38};
        DrawTextW(dc, L"CHOOSE YOUR ADVENTURE", -1, &title, DT_CENTER | DT_SINGLELINE | DT_VCENTER);
        SelectObject(dc, oldFont); DeleteObject(heading);
        SetTextColor(dc, RGB(188, 218, 146));
        HFONT sub = CreateFontW(12, 0, 0, 0, FW_NORMAL, FALSE, FALSE, FALSE,
            DEFAULT_CHARSET, OUT_DEFAULT_PRECIS, CLIP_DEFAULT_PRECIS, ANTIALIASED_QUALITY,
            DEFAULT_PITCH, L"Arial");
        oldFont = SelectObject(dc, sub);
        RECT hint{10, 34, rc.right - 10, 50};
        DrawTextW(dc, L"Supported classes are available now. Future families stay locked until their server path is ready.", -1, &hint, DT_CENTER | DT_SINGLELINE | DT_VCENTER);
        SelectObject(dc, oldFont); DeleteObject(sub);
        auto cards = CardRects(rc);
        for (int i = 0; i < static_cast<int>(cards.size()); ++i) DrawCard(dc, cards[i], kCards[i], i == gHoveredCard);
        EndPaint(hwnd, &ps);
        return 0;
    }
    }
    return DefWindowProcW(hwnd, msg, wParam, lParam);
}

void EnsureOverlay() {
    if (!gGameWindow || !IsWindow(gGameWindow)) gGameWindow = FindGameWindow();
    if (!gGameWindow) return;
    if (!gOverlay || !IsWindow(gOverlay)) {
        HINSTANCE module = GetModuleHandleW(L"dinput8.dll");
        if (!module) module = GetModuleHandleW(nullptr);
        WNDCLASSEXW wc{};
        wc.cbSize = sizeof(wc); wc.lpfnWndProc = SelectorWndProc; wc.hInstance = module;
        wc.hCursor = LoadCursor(nullptr, IDC_HAND); wc.lpszClassName = kWindowClass;
        wc.style = CS_HREDRAW | CS_VREDRAW;
        if (!GetClassInfoExW(module, kWindowClass, &wc)) RegisterClassExW(&wc);
        gOverlay = CreateWindowExW(WS_EX_NOPARENTNOTIFY, kWindowClass, L"EverLeaf Class Selector",
            WS_CHILD | WS_VISIBLE, 0, 0, 780, 588, gGameWindow, nullptr, module, nullptr);
    }
    PositionOverlay();
    if (gOverlay) { gHoveredCard = -1; InvalidateRect(gOverlay, nullptr, TRUE); ShowWindow(gOverlay, SW_SHOWNA); }
}

void __cdecl OnRaceSelectorShown(void* login) {
    gLogin = reinterpret_cast<BYTE*>(login);
    InterlockedExchange(&gEvanMode, 0);
    EnsureOverlay();
}

__declspec(naked) void RaceSelectEntryHook() {
    __asm {
        mov dword ptr [esi + 0x214], 1
        pushfd
        pushad
        push esi
        call OnRaceSelectorShown
        add esp, 4
        popad
        popfd
        jmp dword ptr [gRaceSelectEntryReturn]
    }
}

__declspec(naked) void CreatePacketRaceHook() {
    __asm {
        pushfd
        cmp dword ptr [gEvanMode], 0
        je normalRace
        popfd
        push 3
        jmp dword ptr [gCreatePacketRacePushReturn]
    normalRace:
        popfd
        push dword ptr [esi + 0x214]
        jmp dword ptr [gCreatePacketRacePushReturn]
    }
}

} // namespace

bool Apply() {
    if (gInstalled) return true;
    if (!BytesMatch(kRaceSelectEntry, kRaceSelectEntryBytes, sizeof(kRaceSelectEntryBytes))) return false;
    if (!BytesMatch(kCreatePacketRacePush, kCreatePacketRacePushBytes, sizeof(kCreatePacketRacePushBytes))) return false;
    Memory::CodeCave(reinterpret_cast<void*>(RaceSelectEntryHook), kRaceSelectEntry, sizeof(kRaceSelectEntryBytes));
    Memory::CodeCave(reinterpret_cast<void*>(CreatePacketRaceHook), kCreatePacketRacePush, sizeof(kCreatePacketRacePushBytes));
    gInstalled = true;
    return true;
}

#else

bool Apply() { return false; }

#endif

} // namespace EverLeafEvanRaceSelect
