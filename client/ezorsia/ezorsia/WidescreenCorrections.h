#pragma once

#include "Client.h"
#include "Memory.h"
#include "CrashDiagnostics.h"

namespace WidescreenCorrections {
namespace detail {
constexpr DWORD kCWndHorizontalLowerBound = 0x009DFCF3;
constexpr DWORD kCWndVerticalLowerBound = 0x009DFE6B;
constexpr DWORD kLimitedViewDarkHeight = 0x0055B885;
constexpr DWORD kHorizontalWidthOperand = 0x004D59B3;
constexpr DWORD kLoginDialogVerticalAnimate = 0x0060F79C;
constexpr DWORD kLoginDialogVerticalPosition = 0x0060F7A5;

inline bool ReadInt(DWORD address, int& value) {
    __try {
        value = *reinterpret_cast<int*>(address);
        return true;
    }
    __except (EXCEPTION_EXECUTE_HANDLER) {
        return false;
    }
}

inline bool MatchesInheritedWrongValues() {
    int horizontalLower = 0;
    int verticalLower = 0;
    int limitedViewHeight = 0;
    int horizontalWidth = 0;
    int loginVerticalAnimate = 0;
    int loginVerticalPosition = 0;

    if (!ReadInt(kCWndHorizontalLowerBound, horizontalLower) ||
        !ReadInt(kCWndVerticalLowerBound, verticalLower) ||
        !ReadInt(kLimitedViewDarkHeight, limitedViewHeight) ||
        !ReadInt(kHorizontalWidthOperand, horizontalWidth) ||
        !ReadInt(kLoginDialogVerticalAnimate, loginVerticalAnimate) ||
        !ReadInt(kLoginDialogVerticalPosition, loginVerticalPosition)) {
        return false;
    }

    return horizontalLower == Client::m_nGameHeight &&
           verticalLower == Client::m_nGameWidth &&
           limitedViewHeight == Client::m_nGameWidth &&
           horizontalWidth == Client::m_nGameHeight &&
           loginVerticalAnimate == (Client::m_nGameHeight / 2) - 201 &&
           loginVerticalPosition == (Client::m_nGameHeight / 2) - 181;
}
} // namespace detail

inline bool Apply() {
    if (!detail::MatchesInheritedWrongValues()) {
        CrashDiagnostics::LogEvent("widescreen correction preflight mismatch; values unchanged");
        std::cout << "EverLeaf Client v2: widescreen correction preflight mismatch; leaving values unchanged" << std::endl;
        return false;
    }

    Memory::WriteInt(
        detail::kCWndHorizontalLowerBound,
        static_cast<unsigned int>(-Client::m_nGameWidth)
    );
    Memory::WriteInt(
        detail::kCWndVerticalLowerBound,
        static_cast<unsigned int>(-Client::m_nGameHeight)
    );
    Memory::WriteInt(
        detail::kLimitedViewDarkHeight,
        static_cast<unsigned int>(Client::m_nGameHeight)
    );
    Memory::WriteInt(
        detail::kHorizontalWidthOperand,
        static_cast<unsigned int>(Client::m_nGameWidth)
    );
    Memory::WriteInt(
        detail::kLoginDialogVerticalAnimate,
        static_cast<unsigned int>((Client::m_nGameHeight / 2) - 150)
    );
    Memory::WriteInt(
        detail::kLoginDialogVerticalPosition,
        static_cast<unsigned int>((Client::m_nGameHeight / 2) - 130)
    );

    CrashDiagnostics::LogEvent("verified widescreen axis corrections applied");
    std::cout << "EverLeaf Client v2: applied verified widescreen axis corrections" << std::endl;
    return true;
}
} // namespace WidescreenCorrections
