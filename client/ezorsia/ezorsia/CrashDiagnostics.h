#pragma once

namespace CrashDiagnostics {
    // Creates/refreshes the local EverLeafClient.log for this launch and installs
    // an unhandled-exception observer. Nothing is uploaded or transmitted.
    void Install();

    // Records a coarse startup/runtime phase using string literals only. This is
    // intentionally account-agnostic and must never receive player-identifying data.
    void SetPhase(const char* phase);

    // Adds a timestamped local diagnostic event to EverLeafClient.log.
    void LogEvent(const char* eventText);
}

