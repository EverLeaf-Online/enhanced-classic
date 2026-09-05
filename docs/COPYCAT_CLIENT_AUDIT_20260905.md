# Copycat/Yuna client audit — 2026-09-05

This document records the read-only full-folder audit of the client snapshot supplied by the EverLeaf project owner. It is a reference/donor analysis only. No copycat binary is trusted or shipped by EverLeaf Client v2.

## Snapshot identity

- Source directory audited: `/home/ubuntu/everleafms copycat`
- Regular files: 65
- Bytes hashed/scanned: 8,501,506,573
- PE files parsed: 36
- WZ files: 17
- Full raw snapshot was preserved separately and all eight split archive parts passed SHA-256 verification.
- `YunaMS.exe` SHA-256: `7e1bfc08d1cb4b066d7d0c9f6dc0f350a0d3358f1288068d437b88a7c38ae3df`
- The separately supplied `EverleafMS.exe` is byte-identical to that `YunaMS.exe`.

## Architecture finding

The snapshot is not a newer MapleStory engine. It is the 2010 v83 executable plus a modern native extension stack and much newer WZ content.

Important correction from the full audit: `dinput8.dll` is not the primary Yuna loader. The audited `ijl15.dll` imports both `yunams.dll` and `yunamsw.dll`, making the modified/proxy IJL module the loader/injection bridge. Yuna's own crash strings identify the components as Loader/Injection (`ijl15.dll`), Main Code (`yunams.dll`) and Widget Code (`yunamsw.dll`).

`dinput8.dll` is a separate third-party raw-input/window wrapper. Its version metadata identifies Emulator Nexus BC2 0.8.0.0 and it imports raw-input/window-hook APIs. EverLeaf must keep its own source-built dinput proxy/bootstrap instead of adopting this chain.

The snapshot also contains an x86 D3D8-to-D3D9 wrapper (`d3d8.dll`) and a D3D9/Discord widget module (`yunamsw.dll`). This separation is useful as an architectural reference for a future source-built `EverLeafOverlay.dll`, but the opaque binaries themselves are not donor code.

## PE/runtime observations

`YunaMS.exe` is PE32/x86, image base `0x400000`, COFF Characteristics `0x012F`, with LARGE_ADDRESS_AWARE already set on disk. ASLR and NX are not enabled on the old executable. The August 2026 Yuna DLLs are x86 and do carry ASLR/NX.

This confirms that EverLeaf's inherited runtime `0x0040013E` "4 GB" write is too late to establish process creation policy. The same applies to attempts to rewrite the embedded UAC manifest to `asInvoker` after process creation. Client v2 now strips those inherited runtime writes during its deterministic source transform; PE/UAC policy belongs to the pre-launch/package layer.

The copycat folder also contains x64 `*_cor3.dll`/WPF runtime files and debug CRT files next to the x86 game. These appear to be patcher/runtime debris rather than Maple engine dependencies. They should not be added to the managed EverLeaf client without a proven dependency.

## Loader/patcher quality

The supplied launcher path is a set of command/registry scripts rather than a signed managed updater:

- `Iniciar EverleafMs.cmd` starts `EverleafMS.exe` directly.
- `Instalar-Parche.cmd` kills existing game processes and copies EXE/DLL/config files without cryptographic verification.
- `RUN_FIXES.reg` clears multiple Wizet/Yuna registry locations.
- `FixModifierKeys.bat` changes the user's global Windows Accessibility keyboard-repeat registry values and requires sign-out/reboot.
- `version.data` is an opaque 16-byte token after Base64 decoding.

EverLeaf's signed manifest, bounded download, repair validation and one-time launch ticket remain the preferred trust/update model.

## Native feature matrix

### Already covered or actively implemented in Client v2

- Resolution/widescreen modernization
- Centered framed window
- Borderless window mode
- Reversible Alt+Enter borderless toggle
- Foreground/background presentation FPS caps while preserving the stock game-logic tick
- Fast visual startup/logo removal without globally deleting stock init sleeps
- Local privacy-minimal crash/startup logging
- Safe Win32/Winsock hook boundary
- Race-safe dinput bootstrap
- Focus-safe, field-only WASD remapping (opt-in, PR #359)
- Widescreen UI correction work
- Signed launcher/repair and one-time launch ticket

### Safe high-value parity targets

These are appropriate to reproduce in EverLeaf-owned source after address/protocol validation:

1. Local minidump/crash evidence and bounded freeze diagnostics; never auto-upload.
2. Expanded quickslot presentation/cache, preserving the v83 server's existing 8-entry quickslot wire format unless protocol work explicitly changes it.
3. Cooldown timer labels/quickslot cooldown presentation.
4. Buff timer overlays.
5. Local session tracker: DPS/DPM, EXP/min/hour, mesos/min/hour, kills/min/hour.
6. Latency/server-time/system HUD with opt-in presentation.
7. Item-slot tooltip labels.
8. Equipment/inventory slot locking where local-only protection is sufficient; server/storage paths require server cooperation.
9. Screenshot naming/folder support.
10. Custom cursor / player-on-top / selected transparency controls.
11. Monster Book search and quest-journal sorting where v83 structures can be safely extended.
12. Client-scoped modifier-key compatibility instead of changing global Windows Accessibility registry settings.
13. Optional source-built overlay module after renderer readiness, isolated from core bootstrap.

### Requires server/protocol/WZ coordination

Do not treat these as client-only toggles:

- 18 character slots
- Transmog
- Expanded map transfer
- Maker disassembly changes
- Storage manager actions
- Pet-loot behavior that changes server semantics
- Receive-EXP toggles
- Expedition management/party rearrangement
- Alliance/guild/Discord chat bridge behavior
- Quest-window redesign requiring modified UI resources
- Any quickslot expansion that changes the on-wire `CQuickslotKeyMappedMan` payload

### Reject / do not reproduce

- DLL expiry/kill switch
- Login/character-select WZ hash access gates
- Process/thread anti-cheat scanning
- debugger/tool detection sweeps
- machine registry flags / access-revoked state
- antivirus-exclusion instructions
- global Accessibility keyboard registry edits
- unsigned copy-over patch scripts
- patched/proxy IJL loader chain
- opaque Yuna binaries or Yuna endpoint dependencies
- original Yuna/copycat URLs, vote URLs or server IPs

## WZ donor inventory vs current Cosmic baseline

Every audited copycat WZ hash differs from EverLeaf's pinned Cosmic v0.14 baseline. Several files are dramatically larger, indicating a much newer/more expansive content set rather than a small branded v83 pack.

| WZ | Current Cosmic bytes | Copycat bytes | Approx. size ratio | Copycat SHA-256 |
|---|---:|---:|---:|---|
| Character.wz | 206,267,331 | 2,099,231,493 | 10.2x | `7c415cfaf7e6c06274a110b139e560d4c952b7bbba6de922111dc5e90a1e44ac` |
| Item.wz | 18,397,440 | 359,768,199 | 19.6x | `77a838fa84e1c44d735a8a27f96e34a4421c7f76d2d61fc8e0620c48889f4c43` |
| Map.wz | 638,428,788 | 2,121,837,009 | 3.3x | `c835a1940f6b075ef47010cd0b560e429673910b4194e764b081c560a938c45b` |
| Mob.wz | 479,990,067 | 1,627,265,345 | 3.4x | `2b3604f5211493205798733c62fe3316da3b2ad2625d55a861a3946489e1fcbb` |
| Npc.wz | 53,498,512 | 110,656,254 | 2.1x | `2c001924a291e7e212af942c1995189f8012055d7761b95e2dd356603dd294f3` |
| Quest.wz | 5,993,452 | 6,313,526 | 1.1x | `409d1952ae11b3140f3448fc47bb8a3b41e618e5b5a12e09952bc22228740947` |
| Reactor.wz | 54,348,491 | 64,550,107 | 1.2x | `39404c2892533af9abddceadf88391bdc3ade32b761617c29002b5f821701176` |
| Skill.wz | 76,505,373 | 128,023,821 | 1.7x | `6e58f52847146c716e29fcdf96e0daa31b3c891595852ceeaf99e71ec4542905` |
| String.wz | 3,561,285 | 9,972,546 | 2.8x | `a81b0cdd6cafa48613a433efe06b00ef674404a1c134dafa7ac71faee51dff11` |
| UI.wz | 28,315,281 | 37,470,637 | 1.3x | `cf0c8c141287c9ea846ef23c752893be914dcf7e4b8137668cddfebd4ff99a61` |

Other copycat WZs include `Sound.wz` 1,727,589,670 bytes, `Effect.wz` 153,700,328 bytes, `Morph.wz` 10,069,003 bytes, and `TamingMob.wz` 915 bytes. `List.wz` is only 44 bytes, which is a strong warning that the pack has different loader/data assumptions from EverLeaf's current baseline.

### WZ migration rule

Do **not** wholesale replace EverLeaf's current managed WZ set. EverLeaf's server XML is currently pinned to matching Cosmic map/NPC data, so a blind `Map.wz`/`Npc.wz` replacement can create missing, floating or buried NPCs and other client/server parity failures.

Use the preserved copycat snapshot as a donor/reference set:

1. Extract XML/content inventories from both sets.
2. Diff IDs and subtrees by WZ domain.
3. Selectively backport desired maps/mobs/items/skills/UI resources.
4. Import/update matching server XML/scripts/data in the same batch.
5. Round-trip/repack WZ and verify hashes.
6. Client-load test every imported map/resource before publication.

## Endpoint/branding coupling

The modified `yunams.dll` is only slightly different from its `backup-before-wzcheck` copy and adds copycat URLs, while still retaining original Yuna URLs/IPs and vote references. `yunamsw.dll` also retains Yuna endpoints. This is incomplete endpoint/brand decoupling and another reason not to ship the binaries.

## Direction

EverLeaf Client v2 should remain:

`managed v83 EXE + EverLeaf-owned native bootstrap/core + signed launcher/repair + selectively modernized WZ/UI + optional EverLeaf-owned overlay`

The full copycat snapshot is valuable primarily as (a) a feature/address-behavior reference and (b) a newer WZ donor set. It should not become EverLeaf's runtime binary dependency.
