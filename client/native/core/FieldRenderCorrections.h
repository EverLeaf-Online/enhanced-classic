#pragma once

#include "Client.h"
#include "Memory.h"
#include "CrashDiagnostics.h"
#include "FieldGridWeather.h"

#include <windows.h>
#include <iostream>

// Low-risk field/render corrections selectively adapted from Kaentake's pinned
// GMS v83 resolution work. Immediate operands live here; owner-level grid and
// weather-call behavior is delegated to FieldGridWeather so both stay coherent
// across startup and live resolution changes.
namespace FieldRenderCorrections {
namespace detail {

// CMapLoadable::TransientLayer_Weather. EverLeaf already updates the surrounding
// width/height operands, but these three extents were still left at stock 800x600.
constexpr DWORD kWeatherHalfWidthMinus10 = 0x0064059B; // 0x00640599 + 2
constexpr DWORD kWeatherBottomMinus10 = 0x006405BC;    // 0x006405BA + 2
constexpr DWORD kWeatherHalfHeight = 0x006406FC;       // 0x006406FA + 2

// CField_LimitedView::Init, m_pLayerDark RelMove Y immediate. The inherited HD
// patch only writes -height/2. Kaentake additionally subtracts the vertical
// center adjustment `(height - 600) / 2`, which keeps the dark layer aligned on
// resolutions taller than the original 600px viewport.
constexpr DWORD kLimitedViewDarkY = 0x0055BB30; // 0x0055BB2F + 1

constexpr int kStockWeatherHalfWidthMinus10 = 390;
constexpr int kStockWeatherBottomMinus10 = 590;
constexpr int kStockWeatherHalfHeight = 300;

inline bool ReadInt(DWORD address, int& value) {
    __try {
        value = *reinterpret_cast<int*>(address);
        return true;
    }
    __except (EXCEPTION_EXECUTE_HANDLER) {
        return false;
    }
}

inline int CorrectLimitedViewDarkY() {
    const int halfHeight = Client::m_nGameHeight / 2;
    const int verticalAdjustment = (Client::m_nGameHeight - 600) / 2;
    return -halfHeight - verticalAdjustment;
}

inline bool MatchesExpectedPreState() {
    int weatherHalfWidth = 0;
    int weatherBottom = 0;
    int weatherHalfHeight = 0;
    int limitedViewDarkY = 0;

    if (!ReadInt(kWeatherHalfWidthMinus10, weatherHalfWidth) ||
        !ReadInt(kWeatherBottomMinus10, weatherBottom) ||
        !ReadInt(kWeatherHalfHeight, weatherHalfHeight) ||
        !ReadInt(kLimitedViewDarkY, limitedViewDarkY)) {
        return false;
    }

    const int correctWeatherHalfWidth = (Client::m_nGameWidth / 2) - 10;
    const int correctWeatherBottom = Client::m_nGameHeight - 10;
    const int correctWeatherHalfHeight = Client::m_nGameHeight / 2;
    const int inheritedLimitedViewY = -(Client::m_nGameHeight / 2);
    const int correctLimitedViewY = CorrectLimitedViewDarkY();

    const bool weatherHalfWidthKnown =
        weatherHalfWidth == kStockWeatherHalfWidthMinus10 ||
        weatherHalfWidth == correctWeatherHalfWidth;
    const bool weatherBottomKnown =
        weatherBottom == kStockWeatherBottomMinus10 ||
        weatherBottom == correctWeatherBottom;
    const bool weatherHalfHeightKnown =
        weatherHalfHeight == kStockWeatherHalfHeight ||
        weatherHalfHeight == correctWeatherHalfHeight;
    const bool limitedViewKnown =
        limitedViewDarkY == inheritedLimitedViewY ||
        limitedViewDarkY == correctLimitedViewY;

    return weatherHalfWidthKnown && weatherBottomKnown &&
           weatherHalfHeightKnown && limitedViewKnown;
}

} // namespace detail

inline void ApplyCurrent() {
    Memory::WriteInt(
        detail::kWeatherHalfWidthMinus10,
        static_cast<unsigned int>((Client::m_nGameWidth / 2) - 10));
    Memory::WriteInt(
        detail::kWeatherBottomMinus10,
        static_cast<unsigned int>(Client::m_nGameHeight - 10));
    Memory::WriteInt(
        detail::kWeatherHalfHeight,
        static_cast<unsigned int>(Client::m_nGameHeight / 2));
    Memory::WriteInt(
        detail::kLimitedViewDarkY,
        static_cast<unsigned int>(detail::CorrectLimitedViewDarkY()));

    // RuntimeResolution already calls this function after every accepted mode
    // change and in its best-effort rollback path, so keep MakeGrid's vertical
    // center state synchronized here as well.
    FieldGridWeather::ApplyCurrent();
}

inline bool Apply() {
    if (!detail::MatchesExpectedPreState()) {
        CrashDiagnostics::LogEvent("field render correction preflight mismatch; values unchanged");
        std::cout << "EverLeaf Client v2: field render correction preflight mismatch; leaving values unchanged" << std::endl;
        return false;
    }

    ApplyCurrent();

    // Owner-level grid/weather hooks are optional and independently preflighted.
    // A mismatch must not undo the already-verified immediate corrections.
    if (!FieldGridWeather::Install()) {
        CrashDiagnostics::LogEvent("field grid/weather owner hooks unavailable; immediate corrections remain active");
    }

    CrashDiagnostics::LogEvent("verified field render corrections applied");
    std::cout << "EverLeaf Client v2: applied verified field render corrections" << std::endl;
    return true;
}

} // namespace FieldRenderCorrections
