#pragma once

#include <string>

namespace DiscordPresence {
void Start();
void Stop();
void SetActivity(const std::string& details, const std::string& state);
}
