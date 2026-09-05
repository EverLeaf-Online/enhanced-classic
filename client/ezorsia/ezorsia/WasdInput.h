#pragma once

#include "INIReader.h"

// Optional Client v2 WASD translation at Maple's own DirectInput message layer.
// This deliberately does not install a global/window keyboard hook. Translation
// requires an active CField stage and also fails closed whenever Maple's focused
// IUIMsgHandler is a CCtrlEdit, so login/PIC/chat text remains normal W/A/S/D.
namespace EverLeafWasdInput {
namespace detail {

constexpr DWORD kGetISMessageAddress = 0x0059A306;
constexpr DWORD kWndManInstanceAddress = 0x00BEC20C;
constexpr DWORD kWndManFocusOffset = 0x88;
constexpr DWORD kCtrlEditRttiAddress = 0x00BED5EC;
constexpr DWORD kWvsAppInstanceAddress = 0x00BE7B38;
constexpr DWORD kStageInstanceAddress = 0x00BEDED4;
constexpr DWORD kFieldRttiAddress = 0x00BED758;

using GetISMessage_t = int(__fastcall*)(void* pThis, void* edx, ISMSG* pISMsg);
static GetISMessage_t gGetISMessageOriginal =
    reinterpret_cast<GetISMessage_t>(kGetISMessageAddress);
static bool gEnabled = false;

static_assert(sizeof(ISMSG) == 12, "EverLeaf v83 ISMSG layout drifted");

inline bool IsMapleForeground() {
    __try {
        auto* app = *reinterpret_cast<CWvsApp**>(kWvsAppInstanceAddress);
        return app && app->m_hWnd && GetForegroundWindow() == app->m_hWnd;
    }
    __except (EXCEPTION_EXECUTE_HANDLER) {
        return false;
    }
}

inline bool IsGameplayField() {
    __try {
        auto* stage = *reinterpret_cast<CStage**>(kStageInstanceAddress);
        if (!stage) {
            return false;
        }

        // CStage inherits IGObj first and IUIMsgHandler second. static_cast keeps
        // the correct +4 multiple-inheritance adjustment before calling IsKindOf.
        auto* stageUi = static_cast<IUIMsgHandler*>(stage);
        if (!stageUi || !stageUi->vfptr) {
            return false;
        }

        auto* vtable = reinterpret_cast<IUIMsgHandlerVtbl*>(stageUi->vfptr);
        if (!vtable->IsKindOf) {
            return false;
        }

        return vtable->IsKindOf(
            stageUi,
            reinterpret_cast<CRTTI*>(kFieldRttiAddress)) != 0;
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

        auto* focus = *reinterpret_cast<IUIMsgHandler**>(wndMan + kWndManFocusOffset);
        if (!focus || !focus->vfptr) {
            return false;
        }

        auto* vtable = reinterpret_cast<IUIMsgHandlerVtbl*>(focus->vfptr);
        if (!vtable->IsKindOf) {
            // Unknown handler layout: fail closed rather than hijacking typing.
            return true;
        }

        return vtable->IsKindOf(
            focus,
            reinterpret_cast<CRTTI*>(kCtrlEditRttiAddress)) != 0;
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

inline int __fastcall GetISMessage_Hook(void* pThis, void* edx, ISMSG* pISMsg) {
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
