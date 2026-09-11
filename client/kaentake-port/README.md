# EverLeaf Kaentake integration

This directory contains EverLeaf-owned integration code and a reproducible build transform for the QA client candidate. The build clones the pinned upstream source during CI, applies EverLeaf branding and the 800x600 login-control alignment patch, then produces `EverLeaf.exe` and `EverLeaf.dll`.

Upstream source is not vendored here. Attribution/provenance is retained separately from player-facing branding.
