#include "stdafx.h"
#include "EvanRaceSelectPatch.h"

namespace EverLeafEvanRaceSelect {

// The stock selector remains the authoritative UI. The previous child-window
// overlay was triggered by a stock selection update (including hover), and
// neither replaced the stock controls nor followed their transition lifecycle.
// Do not install those hooks. Evan compatibility routing remains in Client.cpp;
// exposing a fourth choice requires integration with the stock UI controls.
bool Apply() {
    return false;
}

} // namespace EverLeafEvanRaceSelect
