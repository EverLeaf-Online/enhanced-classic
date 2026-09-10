#pragma once

#include <string>

namespace DiscordPresence {
    // Starts a best-effort background connection to the local Discord client.
    // No Discord SDK DLL, token, or network credential is required.
    void Start();
    void Stop();

    // Safe to call from game-state hooks once their v83 contracts are verified.
    void SetActivity(const std::string& details, const std::string& state);
}
