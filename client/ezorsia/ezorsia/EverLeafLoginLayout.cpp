#include "stdafx.h"
#include "MainMain.h"

namespace {
    // EverLeaf currently ships the existing UI overlay but not a complete
    // full-size replacement login-frame asset set. Keep only the historical
    // large-frame positioning hint; forcing ownLoginFrame without matching WZ
    // assets causes duplicated/clipped login layers at HD resolutions.
    struct EverLeafLoginLayoutDefaults {
        EverLeafLoginLayoutDefaults() {
            MainMain::bigLoginFrame = true;
        }
    } gEverLeafLoginLayoutDefaults;
}
