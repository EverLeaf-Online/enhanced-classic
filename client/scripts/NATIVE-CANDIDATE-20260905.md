# Native client checkpoint — 2026-09-05

Work took place on the Everleaf Production VM, in an isolated source worktree
based on client-v2-candidate-login-layout-fix commit 0683333c5.
No production service, launcher manifest, or player payload was changed.

The existing clean candidate has 36 files. SHA-256 comparison against the VM's
current production payload found exactly one changed file: UI.wz. The other
35 files match, including EverLeaf.exe, dinput8.dll, EverLeaf_UI.wz and all
content WZ files. No additional/omitted files or donor runtime filenames were found.

The streaming ASCII/UTF-16LE scan found the token 'yuna' in Character.wz,
Map.wz and Sound.wz. Each file is identical to production; these byte matches
are not evidence that visible donor branding was introduced by this candidate.

The installed wz-python reader recognized a version-83 archive header but
returned unreadable directory names using its default/GMS and BMS settings.
Decoded UI branding has therefore NOT been verified, and the donor UI must not
be described as fully rebranded. The checked-in artwork generator also remains
single-screen; connected panorama implementation is outstanding.

An existing numeric Discord application ID is configured for the production
website's Discord login. This can inform client setup, but Rich Presence assets
and behavior have not been verified. No bot token belongs in the client.

Validation: seven package-audit regression tests passed; full package
structural/preservation audit passed. Release readiness remains false pending
decoded UI/panorama work, native Discord integration, and real Windows
startup/login/world/character/channel/map validation.
