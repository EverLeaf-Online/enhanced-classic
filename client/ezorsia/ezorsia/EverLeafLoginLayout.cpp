#include "stdafx.h"
#include "Client.h"
#include "MainMain.h"
#include "Memory.h"

namespace {
    using UpdateResolution_t = void(*)();
    UpdateResolution_t gUpdateResolution = &Client::UpdateResolution;

    void UpdateResolution_Hook() {
        // EverLeaf ships resolution-specific login frame assets. MapleEzorsia's
        // default path treats them as an 800x600-style centered frame unless
        // bigLoginFrame is enabled. Flip the layout mode immediately before the
        // normal resolution patch runs so the login presentation uses the full
        // configured HD viewport instead of leaving the unused black surround.
        if (MainMain::EzorsiaV2WzIncluded || MainMain::CustomLoginFrame) {
            MainMain::bigLoginFrame = true;
        }

        gUpdateResolution();
    }

    struct EverLeafLoginLayoutBootstrap {
        EverLeafLoginLayoutBootstrap() {
            Memory::SetHook(
                true,
                reinterpret_cast<void**>(&gUpdateResolution),
                reinterpret_cast<void*>(&UpdateResolution_Hook));
        }
    } gEverLeafLoginLayoutBootstrap;
}
