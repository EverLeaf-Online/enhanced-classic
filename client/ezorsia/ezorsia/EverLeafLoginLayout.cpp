#include "stdafx.h"
#include "MainMain.h"

namespace {
    // EverLeaf always ships its branded HD UI overlay in the managed client
    // package. Force the client onto the custom full-size login-frame path from
    // process startup so it does not fall back to the stock v83 presentation.
    // MainMain later re-detects EverLeaf_UI.wz and enables CustomLoginFrame; the
    // persistent own/big flags below select the correct rendering branch.
    struct EverLeafLoginLayoutDefaults {
        EverLeafLoginLayoutDefaults() {
            MainMain::ownLoginFrame = true;
            MainMain::bigLoginFrame = true;
        }
    } gEverLeafLoginLayoutDefaults;
}
