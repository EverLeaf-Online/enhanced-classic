#pragma once

namespace FrameLimiter {
    // Installs the presentation-only frame limiter. Failure is non-fatal and
    // leaves the stock v83 RenderFrame path untouched.
    bool Install();
}

