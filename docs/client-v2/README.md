# EverLeaf Client v2

Client v2 is being developed as isolated, reviewable layers on top of the stable v83 engine rather than as one monolithic client fork.

Current layers:

- bootstrap/input foundation: loader-lock cleanup, bounded unpack preflight, startup watchdog, race-safe dinput8 forwarding, stock v83 CWvsApp::Run semantics
- display modernization: DPI-aware centered windowed mode and opt-in borderless mode
- runtime patch reliability: cache-coherent code/data patch writes
- local diagnostics: privacy-minimal crash/startup logging beside the client executable

The server protocol, WZ content, launcher deployment, and live client are kept separate from these draft layers until runtime smoke validation is complete.
