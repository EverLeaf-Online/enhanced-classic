#include "pch.h"
#include "hook.h"

namespace {
constexpr uintptr_t kStartupLogoSite = 0x0062EE54;
constexpr size_t kStartupLogoPatchLength = 21;
}

void AttachEverLeafStartupMod() {
    // Skip the stock Nexon/Wizet logo stage.  This hook runs only after the
    // stock v83 image has unpacked and Kaentake begins installing client hooks.
    PatchNop(kStartupLogoSite, kStartupLogoSite + kStartupLogoPatchLength);
    DEBUG_MESSAGE("EverLeaf startup logo skip applied");
}
