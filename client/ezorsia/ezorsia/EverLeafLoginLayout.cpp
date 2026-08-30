#include "stdafx.h"
#include "MainMain.h"

void PrepareEverLeafLoginLayout() {
    // EverLeaf ships resolution-specific login frame assets. MapleEzorsia's
    // normal centered-login path keeps the legacy 800x600 presentation in the
    // middle of an HD window. Enable the full-size login layout after
    // MainMain has detected EverLeaf_UI.wz and before UpdateResolution runs.
    if (MainMain::EzorsiaV2WzIncluded || MainMain::CustomLoginFrame) {
        MainMain::bigLoginFrame = true;
    }
}
