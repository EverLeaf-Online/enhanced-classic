#pragma once

#include <windows.h>
#include <iostream>
#include "Memory.h"

namespace EverLeafEvanRaceSelect {

inline constexpr int kRaceExplorer = 1;
inline constexpr int kRaceEvan = 3;
inline constexpr int kRaceSelectStep = 3;
inline constexpr int kCreateCharacterStep = 4;
inline constexpr std::size_t kLoginStepOffset = 0x168;
inline constexpr std::size_t kLoginRaceOffset = 0x214;

// Exact GMS v83 functions, verified against EverLeaf's unpacked v83 localhost.
inline constexpr DWORD kCLoginUpdateAddress = 0x005F4C16;
inline constexpr DWORD kCLoginChangeStepAddress = 0x005F53C0;
inline constexpr DWORD kCLoginSendNewCharPacketAddress = 0x005F7E7A;

using CLoginUpdate_t = void(__thiscall*)(void*);
using CLoginChangeStep_t = void(__thiscall*)(void*, int);
using CLoginSendNewCharPacket_t = void(__thiscall*)(void*);

inline CLoginUpdate_t g_CLoginUpdate = reinterpret_cast<CLoginUpdate_t>(kCLoginUpdateAddress);
inline CLoginChangeStep_t g_CLoginChangeStep = reinterpret_cast<CLoginChangeStep_t>(kCLoginChangeStepAddress);
inline CLoginSendNewCharPacket_t g_CLoginSendNewCharPacket = reinterpret_cast<CLoginSendNewCharPacket_t>(kCLoginSendNewCharPacketAddress);

inline void* g_login = nullptr;
inline HWND g_button = nullptr;
inline bool g_evanCreationActive = false;
inline ATOM g_buttonClass = 0;

inline int& LoginStep(void* login) {
    return *reinterpret_cast<int*>(reinterpret_cast<unsigned char*>(login) + kLoginStepOffset);
}

inline int& LoginRace(void* login) {
    return *reinterpret_cast<int*>(reinterpret_cast<unsigned char*>(login) + kLoginRaceOffset);
}

inline void LayoutButton(HWND button) {
    if (!button) return;
    HWND parent = GetParent(button);
    if (!parent) return;

    RECT rc{};
    if (!GetClientRect(parent, &rc)) return;
    const int width = rc.right - rc.left;
    const int height = rc.bottom - rc.top;

    // Stock v83's three race tabs are centered over the book. Put Evan directly
    // to the right of Aran while scaling the anchor with the client resolution.
    const int x = width / 2 + 205;
    const int y = height / 2 - 255;
    const int w = 96;
    const int h = 34;
    SetWindowPos(button, HWND_TOP, x, y, w, h, SWP_NOACTIVATE);
}

inline LRESULT CALLBACK EvanButtonWndProc(HWND hwnd, UINT msg, WPARAM wParam, LPARAM lParam) {
    switch (msg) {
    case WM_ERASEBKGND:
        return 1;
    case WM_PAINT: {
        PAINTSTRUCT ps{};
        HDC dc = BeginPaint(hwnd, &ps);
        RECT rc{};
        GetClientRect(hwnd, &rc);

        const bool hover = (GetWindowLongPtr(hwnd, GWLP_USERDATA) != 0);
        HBRUSH bg = CreateSolidBrush(hover ? RGB(244, 224, 170) : RGB(229, 204, 143));
        FillRect(dc, &rc, bg);
        DeleteObject(bg);

        HPEN border = CreatePen(PS_SOLID, 1, RGB(107, 77, 38));
        HGDIOBJ oldPen = SelectObject(dc, border);
        HGDIOBJ oldBrush = SelectObject(dc, GetStockObject(HOLLOW_BRUSH));
        Rectangle(dc, rc.left, rc.top, rc.right, rc.bottom);
        SelectObject(dc, oldBrush);
        SelectObject(dc, oldPen);
        DeleteObject(border);

        SetBkMode(dc, TRANSPARENT);
        SetTextColor(dc, RGB(88, 53, 25));
        HFONT font = CreateFontA(-17, 0, 0, 0, FW_BOLD, FALSE, FALSE, FALSE,
            DEFAULT_CHARSET, OUT_DEFAULT_PRECIS, CLIP_DEFAULT_PRECIS,
            CLEARTYPE_QUALITY, DEFAULT_PITCH | FF_DONTCARE, "Arial");
        HGDIOBJ oldFont = SelectObject(dc, font);
        DrawTextA(dc, "EVAN", -1, &rc, DT_CENTER | DT_VCENTER | DT_SINGLELINE);
        SelectObject(dc, oldFont);
        DeleteObject(font);
        EndPaint(hwnd, &ps);
        return 0;
    }
    case WM_MOUSEMOVE: {
        if (GetWindowLongPtr(hwnd, GWLP_USERDATA) == 0) {
            SetWindowLongPtr(hwnd, GWLP_USERDATA, 1);
            TRACKMOUSEEVENT tme{ sizeof(tme), TME_LEAVE, hwnd, 0 };
            TrackMouseEvent(&tme);
            InvalidateRect(hwnd, nullptr, FALSE);
        }
        return 0;
    }
    case WM_MOUSELEAVE:
        SetWindowLongPtr(hwnd, GWLP_USERDATA, 0);
        InvalidateRect(hwnd, nullptr, FALSE);
        return 0;
    case WM_LBUTTONUP:
        if (g_login && LoginStep(g_login) == kRaceSelectStep) {
            g_evanCreationActive = true;
            LoginRace(g_login) = kRaceEvan;
            ShowWindow(hwnd, SW_HIDE);
            // Use Nexon's own login-step transition. Step 4 is character appearance
            // creation; CLogin::Update is bridged below so Evan reuses Explorer's
            // compatible appearance UI while retaining race 3 on the wire.
            g_CLoginChangeStep(g_login, kCreateCharacterStep);
        }
        return 0;
    }
    return DefWindowProcA(hwnd, msg, wParam, lParam);
}

inline void EnsureButton() {
    if (g_button && IsWindow(g_button)) return;

    HWND maple = FindWindowA("MapleStoryClass", nullptr);
    if (!maple) return;

    if (!g_buttonClass) {
        WNDCLASSEXA wc{};
        wc.cbSize = sizeof(wc);
        wc.lpfnWndProc = EvanButtonWndProc;
        wc.hInstance = GetModuleHandleA("dinput8.dll");
        wc.hCursor = LoadCursor(nullptr, IDC_HAND);
        wc.lpszClassName = "EverLeafEvanRaceButton";
        g_buttonClass = RegisterClassExA(&wc);
        if (!g_buttonClass && GetLastError() != ERROR_CLASS_ALREADY_EXISTS) {
            std::cerr << "EverLeaf Evan race selector: failed to register button class." << std::endl;
            return;
        }
    }

    g_button = CreateWindowExA(
        WS_EX_TOPMOST,
        "EverLeafEvanRaceButton",
        "Evan",
        WS_CHILD,
        0, 0, 96, 34,
        maple,
        nullptr,
        GetModuleHandleA("dinput8.dll"),
        nullptr);

    if (!g_button) {
        std::cerr << "EverLeaf Evan race selector: failed to create button." << std::endl;
        return;
    }

    LayoutButton(g_button);
    ShowWindow(g_button, SW_HIDE);
}

inline void SetButtonVisible(bool visible) {
    EnsureButton();
    if (!g_button) return;
    LayoutButton(g_button);
    ShowWindow(g_button, visible ? SW_SHOWNOACTIVATE : SW_HIDE);
}

inline void __fastcall CLoginUpdateHook(void* pThis, void*) {
    g_login = pThis;

    int step = LoginStep(pThis);
    if (step == kRaceSelectStep) {
        // Returning/backing out of Evan creation should restore the stock selector
        // to a valid native race before it draws its three built-in entries.
        if (g_evanCreationActive) {
            g_evanCreationActive = false;
            LoginRace(pThis) = kRaceExplorer;
        }
        SetButtonVisible(true);
        g_CLoginUpdate(pThis);
        return;
    }

    SetButtonVisible(false);

    // v83 has creation UI constructors only for races 0/1/2. Evan's server
    // appearance payload is identical to Explorer's, so borrow Explorer rendering
    // only for CLogin::Update. Race 3 is restored immediately afterward.
    const bool bridgeEvan = g_evanCreationActive && LoginRace(pThis) == kRaceEvan;
    if (bridgeEvan) LoginRace(pThis) = kRaceExplorer;
    g_CLoginUpdate(pThis);
    if (bridgeEvan) LoginRace(pThis) = kRaceEvan;
}

inline void __fastcall CLoginSendNewCharPacketHook(void* pThis, void*) {
    // Fail-safe: even if packet generation is reached from inside a bridged UI
    // update, Evan creation must always serialize discriminator 3.
    if (g_evanCreationActive) LoginRace(pThis) = kRaceEvan;
    g_CLoginSendNewCharPacket(pThis);
}

inline bool Install() {
    // These functions are hooked only after Themida has unpacked the executable,
    // matching the rest of Ezorsia's v83 hooks.
    const bool update = Memory::SetHook(
        true,
        reinterpret_cast<void**>(&g_CLoginUpdate),
        reinterpret_cast<void*>(&CLoginUpdateHook));
    const bool send = Memory::SetHook(
        true,
        reinterpret_cast<void**>(&g_CLoginSendNewCharPacket),
        reinterpret_cast<void*>(&CLoginSendNewCharPacketHook));

    if (!update || !send) {
        std::cerr << "EverLeaf Evan race selector: failed to install login hooks." << std::endl;
        return false;
    }

    std::cout << "EverLeaf Evan race selector: enabled v83 fourth-race bridge (race 3)." << std::endl;
    return true;
}

} // namespace EverLeafEvanRaceSelect
