#pragma once

#include <string>

namespace DiscordPresence {
    // Starts a best-effort background connection to the local Discord client.
    // No Discord SDK DLL, token, or network credential is required.
    // When the pinned GMS v83 gameplay contracts are available, activity is
    // enriched on the Maple game thread with character, level, job and map ID.
    // Invalid/transitional state fails closed to the generic EverLeaf presence.
    void Start();
    void Stop();

    // Thread-safe cached activity update. Maple game-state getters are never
    // invoked by the Discord IPC worker itself.
    void SetActivity(const std::string& details, const std::string& state);
}
