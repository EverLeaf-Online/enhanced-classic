#include "stdafx.h"
#include "MainMain.h"

namespace {
    // EverLeaf always ships its HD UI overlay in the managed client package.
    // Select the full-size login-frame path from process startup so the legacy
    // 800x600 login presentation is not centered inside a black HD viewport.
    struct EverLeafLoginLayoutDefaults {
        EverLeafLoginLayoutDefaults() {
            MainMain::bigLoginFrame = true;
        }
    } gEverLeafLoginLayoutDefaults;
}
