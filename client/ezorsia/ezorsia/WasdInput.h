#pragma once

#include "INIReader.h"
#include <cstddef>

// Optional Client v2 WASD translation at Maple's own DirectInput message layer.
// This deliberately does not install a global/window keyboard hook. Translation
// requires an active CField stage and also fails closed whenever Maple's focused
// IUIMsgHandler is a CCtrlEdit, so login/PIC/chat text remains normal W/A/S/D.
//
// Keep this header independent of AutoTypes.h. That legacy header defines many
// process globals and cannot safely be included by a second translation unit.
namespace EverLeafWasdInput {
namespace detail {

constexpr DWORD kGetISMessageAddress = 0x0059A306;
constexpr DWORD kWndManInstanceAddress = 0x00BEC20C;
constexpr DWORD kWndManFocusOffset = 0x88;
constexpr DWORD kCtrlEditRttiAddress = 0x00BED5EC;
constexpr DWORD kWvsAppInstanceAddress = 0x00BE7B38;
constexpr DWORD kStageInstanceAddress = 0x00BEDED4;
constexpr DWORD kFieldRttiAddress = 0x00BED758;
constexpr size_t kStageUiHandlerOffset = 4;
constexpr size_t kIsKindOfVtableIndex = 0x48 / sizeof(void*);

struct InputMessage {
    unsigned int message;
    unsigned int wParam;
    int lParam;
};

using GetISMessage_t = int(__fastcall*)(void* pThis, void* edx, InputMessage* pISMsg);
using IsKindOf_t = int(__thiscall*)(void* pThis, void* pRtti);

static GetISMessage_t gGetISMessageOriginal =
    reinterpret_cast<GetISMessage_t>(kGetISMessageAddress);
static bool gEnabled = false;

static_assert(sizeof(InputMessage) == 12, "EverLeaf v83 ISMSG layout drifted");
static_assert(sizeof(void*) == 4, "EverLeaf Client v2 native layer must remain Win32/x86");

inline IsKindOf_t GetIsKindOf(void* handler) {
    if (!handler) {
        return nullptr;
    }
    auto** vtable = *reinterpret_cast<void***>(handler);
    if (!vtable) {
        return nullptr;
    }
    return reinterpret_cast<IsKindOf_t>(vtable[kIsKindOfVtableIndex]);
}

inline bool IsMapleForeground() {
    __try {
        auto* app = *reinterpret_cast<unsigned char**>(kWvsAppInstanceAddress);
        if (!app) {
            return false;
        }
        HWND gameWindow = *reinterpret_cast<HWND*>(app + sizeof(void*));
        return gameWindow && GetForegroundWindow() == gameWindow;
    }
    __except (EXCEPTION_EXECUTE_HANDLER) {
        return false;
    }
}

inline bool IsGameplayField() {
    __try {
        auto* stage = *reinterpret_cast<unsigned char**>(kStageInstanceAddress);
        if (!stage) {
            return false;
        }

        // CStage's first base is IGObj (one pointer), so its IUIMsgHandler
        // subobject starts at +4 in this pinned Win32 v83 client.
        void* stageUi = stage + kStageUiHandlerOffset;
        IsKindOf_t isKindOf = GetIsKindOf(stageUi);
        if (!isKindOf) {
            return false;
        }

        return isKindOf(
            stageUi,
            reinterpret_cast<void*>(kFieldRttiAddress)) != 0;
    }
    __except (EXCEPTION_EXECUTE_HANDLER) {
        // Unknown stage/layout: do not remap menu/login input.
        return false;
    }
}

inline bool IsEditControlFocused() {
    __try {
        auto* wndMan = *reinterpret_cast<unsigned char**>(kWndManInstanceAddress);
        if (!wndMan) {
            return false;
        }

        void* focus = *reinterpret_cast<void**>(wndMan + kWndManFocusOffset);
        if (!focus) {
            return false;
        }

        IsKindOf_t isKindOf = GetIsKindOf(focus);
        if (!isKindOf) {
            // Unknown handler layout: fail closed rather than hijacking typing.
            return true;
        }

        return isKindOf(
            focus,
            reinterpret_cast<void*>(kCtrlEditRttiAddress)) != 0;
    }
    __except (EXCEPTION_EXECUTE_HANDLER) {
        // Any version/layout mismatch disables translation for this message.
        return true;
    }
}

inline unsigned int TranslateWasd(unsigned int key) {
    switch (key) {
    case 'W': return VK_UP;
    case 'A': return VK_LEFT;
    case 'S': return VK_DOWN;
    case 'D': return VK_RIGHT;
    default: return key;
    }
}

inline int __fastcall GetISMessage_Hook(void* pThis, void* edx, InputMessage* pISMsg) {
    const int result = gGetISMessageOriginal(pThis, edx, pISMsg);
    if (!result || !gEnabled || !pISMsg) {
        return result;
    }

    // Maple represents both press/release key events as message 0x100 and keeps
    // release/repeat/modifier state in lParam. Change only wParam so the original
    // key lifecycle remains intact and held movement cannot become stuck.
    if (pISMsg->message != WM_KEYDOWN ||
        !IsMapleForeground() ||
        !IsGameplayField() ||
        IsEditControlFocused()) {
        return result;
    }

    pISMsg->wParam = TranslateWasd(pISMsg->wParam);
    return result;
}

} // namespace detail

inline bool Install(bool enable) {
    if (enable) {
        INIReader settings("config.ini");
        detail::gEnabled = settings.GetBoolean("general", "WASDRemapping", false);
        if (!detail::gEnabled) {
            // Disabled by default: do not install a detour or alter normal input.
            return true;
        }
    }

    if (!detail::gGetISMessageOriginal) {
        return false;
    }

    const bool changed = Memory::SetHook(
        enable,
        reinterpret_cast<void**>(&detail::gGetISMessageOriginal),
        reinterpret_cast<void*>(detail::GetISMessage_Hook));

    if (!enable) {
        detail::gEnabled = false;
    }
    return changed;
}

} // namespace EverLeafWasdInput
