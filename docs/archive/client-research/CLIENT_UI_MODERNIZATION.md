# EverLeaf client UI modernization

## Compatibility model

EverLeaf keeps the v83 network/client contract and backports later classic UI behavior where it is safe.

### Character-family selector

| Family | Preview | Creation | Wire identity |
| --- | --- | --- | --- |
| Cygnus Knights | visible | enabled | v83 race 0 |
| Explorer | visible | enabled | v83 race 1 |
| Aran | visible | enabled | v83 race 2 |
| Evan | visible | enabled after client selector backport | v84-style race 3, mapped by EverLeaf server type 3 |
| Dual Blade | visible/locked | disabled | not sent; v95 requires Explorer sub-job 1 |
| Resistance | visible/locked | disabled | not sent; requires later runtime/protocol support |

The server capability gate remains authoritative even if a modified client bypasses a visual lock.

## Evan compatibility

The v83 packet already transports a single race integer. EverLeaf routes race 3 through the stable Explorer appearance/name dialog while preserving the race field, allowing the existing server Evan creator to receive type 3 without changing the v83 wire format. Types above 3 remain server-rejected.

## UI surfaces

1. Login layout and input styling — active on the modernization branch.
2. World selection and channel presentation — preserve 20-channel support, modernize compatible art/layout.
3. Character selection — refresh panels/buttons while preserving PIC/character-handoff behavior.
4. Character-family selector — backport Evan slot; show future families locked.
5. Character creation — reuse native family-specific v83/v84-compatible dialogs where possible.
6. Common gameplay UI — selectively backport compatible Basic/UIWindow/StatusBar/Guild/CashShop assets after visual/runtime validation.

No UI package is published until the exact Windows client candidate boots and the affected login/creation flow passes validation.
