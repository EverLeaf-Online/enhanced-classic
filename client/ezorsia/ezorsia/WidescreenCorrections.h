#pragma once

#include "Client.h"
#include "Memory.h"

namespace WidescreenCorrections {
namespace detail {
constexpr DWORD kCWndHorizontalLowerBound = 0x009DFCF3;
constexpr DWORD kCWndVerticalLowerBound = 0x009DFE6B;
constexpr DWORD kLimitedViewDarkHeight = 0x0055B885;

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
    if (!ReadInt(kCWndHorizontalLowerBound, horizontalLower) ||
        !ReadInt(kCWndVerticalLowerBound, verticalLower) ||
        !ReadInt(kLimitedViewDarkHeight, limitedViewHeight)) {
        return false;
    }

    // These are the exact values written by the inherited HD patch immediately
    // before this correction runs. Refuse to patch an unexpected client layout.
    return horizontalLower == Client::m_nGameHeight &&
           verticalLower == Client::m_nGameWidth &&
           limitedViewHeight == Client::m_nGameWidth;
}
} // namespace detail

inline bool Apply() {
    if (!detail::MatchesInheritedWrongValues()) {
        std::cout << "EverLeaf Client v2: widescreen correction preflight mismatch; leaving values unchanged" << std::endl;
        return false;
    }

    // CWnd::OnMoveWnd lower screen bounds are signed displacements. The legacy
    // patch swaps axes and drops the negative sign. Keep the independently
    // validated upper bounds untouched and repair only the two lower operands.
    Memory::WriteInt(
        detail::kCWndHorizontalLowerBound,
        static_cast<unsigned int>(-Client::m_nGameWidth)
    );
    Memory::WriteInt(
        detail::kCWndVerticalLowerBound,
        static_cast<unsigned int>(-Client::m_nGameHeight)
    );

    // CField_LimitedView::Init creates/draws a dark overlay. The third operand is
    // the rectangle height, but the inherited patch writes screen width into it.
    Memory::WriteInt(
        detail::kLimitedViewDarkHeight,
        static_cast<unsigned int>(Client::m_nGameHeight)
    );

    std::cout << "EverLeaf Client v2: applied verified CWnd/LimitedView widescreen corrections" << std::endl;
    return true;
}
} // namespace WidescreenCorrections
