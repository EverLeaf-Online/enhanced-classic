# EverLeaf GM Commands and Permissions

This is the maintained command/permission reference for the current EverLeaf server. It is derived from the command registrations in `src/main/java/client/command/CommandsExecutor.java`; that source remains authoritative if this document ever disagrees with code.

Do **not** use `handbook/Commands.txt` as the permission source. That file is inherited lookup/reference material and contains legacy role/monetization labels that do not define current EverLeaf policy.

## Permission model

EverLeaf commands have a numeric minimum rank from **0 through 6**.

- Rank **0** is available to ordinary players through the `@` prefix.
- A GM character may invoke commands with either `@` or `!`; staff should use `!` for staff actions so command intent is obvious in screenshots/logs.
- Before executing a command, the server requires `player.gmLevel() >= command.rank`.
- Characters in the jail map cannot use commands at all.
- A command's package/folder (`gm2`, `gm3`, etc.) is **not** itself the permission check. The rank actually supplied during registration is what matters.

Staff rank names/titles are administrative policy and may change; this guide therefore uses the source-authoritative numeric rank rather than inventing role names.

## Rank 0 — player commands

Registered player commands and aliases:

`help`, `commands`, `droplimit`, `time`, `jobguide`, `credits`, `uptime`, `gacha`, `dispose`, `unstuck`, `everleaf`, `changel`, `equiplv`, `showrates`, `rates`, `online`, `marks`, `verdant`, `progress`, `weeklies`, `weekly`, `gm`, `reportbug`, `points`, `vote`, `whodrops`, `whatdropsfrom`, `joinevent`, `leaveevent`, `ranks`, `str`, `dex`, `int`, `luk`, `enableauth`, `toggleexp`, `mylawn`, `bosshp`, `mobhp`.

Three additional commands are **currently registered at rank 0 despite living in the `gm2` package**:

- `gachalist` — opens the Gachapon reward listing.
- `loot` — loots map items owned by the character or party.
- `mobskill` — applies a selected mob skill to all monsters on the current map.

`mobskill` is not appropriate for ordinary-player access and is tracked as a permission defect in [`../KNOWN_ISSUES.md`](../KNOWN_ISSUES.md). Until the source is corrected, staff should treat player use of `@mobskill` as unintended behavior and preserve evidence if abused.

## Rank 1

- `buffme`
- `goto`

Rank 1 is low-level staff capability but still changes gameplay state. Do not grant it merely to provide cosmetic/status distinction.

## Rank 2

- `recharge`
- `whereami`
- `hide`, `unhide`
- `sp`, `ap`
- `empowerme`, `buffmap`, `buff`
- `bomb`, `dc`
- `cleardrops`, `clearslot`, `clearsavelocs`
- `warp`
- `warphere`, `summon`
- `warpto`, `reach`, `follow`
- `gmshop`, `heal`
- `item`, `drop`
- `level`, `levelpro`
- `setslot`, `setstat`, `maxstat`, `maxskill`, `resetskill`
- `search`
- `jail`, `unjail`
- `job`
- `unbug`
- `id`

These commands can directly modify player state, inventories, stats, levels, skills, location, or visibility. Use them only for support/testing actions with a clear reason and avoid using them to create permanent player advantage.

### Jail

`!jail <playername> [minutes]` defaults to five minutes. A positive custom duration may be supplied. Jailing saves the player's warp location and moves the player to the jail map; issuing jail again while already jailed extends the time. The centralized command executor blocks all command use while the character is in jail.

Use jail only as a temporary containment/support tool. It is not a substitute for a documented moderation decision when a ban or account restriction is appropriate.

## Rank 3

- `debuff`, `fly`, `spawn`, `mutemap`, `checkdmg`, `inmap`
- `reloadevents`, `reloaddrops`, `reloadportals`, `reloadmap`, `reloadshops`
- `hpmp`, `maxhpmp`, `music`
- `monitor`, `monitors`, `ignore`, `ignored`, `pos`
- `togglecoupon`, `togglewhitechat`
- `fame`, `givenx`, `givevp`, `givems`, `giverp`
- `expeds`, `kill`, `seed`, `maxenergy`, `killall`
- `notice`, `rip`
- `openportal`, `closeportal`, `pe`
- `startevent`, `endevent`, `everleafops`, `startmapevent`, `stopmapevent`
- `online2`
- `ban`, `unban`
- `healmap`, `healperson`, `hurt`, `killmap`, `night`, `npc`, `face`, `hair`
- `startquest`, `completequest`, `resetquest`
- `timer`, `timermap`, `timerall`
- `warpmap`, `warparea`

Rank 3 includes moderation, currency mutation, map-wide actions, event controls, reloads, quest mutation, packet tooling, and bans. Treat it as a privileged operational rank.

### Ban / unban

Current source syntax:

- `!ban <IGN> <reason>` — reason is required and should be descriptive.
- `!unban <IGN>`

The online-target ban path applies account ban state and attempts network/MAC restrictions before disconnecting the player. The unban path clears account ban state and removes matching IP/MAC ban rows. Moderation policy and evidence requirements are documented in [`MODERATION_AND_APPEALS.md`](MODERATION_AND_APPEALS.md).

### Events

- `!startevent` creates a joinable event on the staff member's current map and broadcasts `@joinevent` instructions. Current implementation defaults to 50 participants.
- `!endevent` closes the channel event to further joins by clearing the channel's active event reference.

Use the full procedure in [`EVENT_OPERATIONS.md`](EVENT_OPERATIONS.md); merely starting/ending the join gate does not prove map cleanup, rewards, or event-script safety.

## Rank 4

- `servermessage`
- `proitem`, `seteqstat`
- `exprate`, `mesorate`, `droprate`, `bossdroprate`, `questrate`, `travelrate`, `fishrate`
- `itemvac`, `forcevac`
- `zakum`, `horntail`, `pinkbean`, `pap`, `pianus`, `cake`
- `playernpc`, `playernpcremove`, `pnpc`, `pnpcremove`
- `pmob`, `pmobremove`
- `qabot`, `qabotops`

Rank 4 can alter global rates, create powerful/custom items, manipulate persistent NPC/mob content, invoke boss helpers, and operate QA bots. Production use should be rare and documented.

Rate commands must not be used casually on production. The public baseline belongs in configuration and the master checklist, not in an undocumented temporary command change.

## Rank 5

- `debug`
- `set`
- `showpackets`
- `showmovelife`
- `showsessions`
- `iplist`

Rank 5 is diagnostic/debug access. Packet/session/IP output can contain sensitive operational or player information; do not paste it into public channels or issues without redaction.

## Rank 6 — highest registered command tier

- `setgmlevel`
- `warpworld`
- `saveall`
- `dcall`
- `mapplayers`
- `getacc`
- `shutdown`
- `clearquestcache`, `clearquest`
- `supplyratecoupon`
- `spawnallpnpcs`, `eraseallpnpcs`
- `addchannel`, `addworld`, `removechannel`, `removeworld`
- `devtest`

Rank 6 includes staff-rank mutation, shutdown, mass disconnect, world/channel topology changes, account lookup, quest-cache operations, and other server-wide controls. Restrict it to operators who are authorized to administer production.

`shutdown` or topology-changing commands should not replace the maintained systemd/release procedures. For normal production restart, rollback, backup, and restore, use [`RECOVERY_AND_RESTORE.md`](RECOVERY_AND_RESTORE.md).

## Operational rules

1. Use the lowest privilege needed for a staff function.
2. Never grant GM rank as a player reward, donation benefit, or convenience entitlement.
3. Do not use item/NX/meso/stat/rate commands to create undocumented player advantage.
4. Preserve reason/evidence for bans, economy corrections, destructive inventory/stat changes, and incident-response actions.
5. Prefer maintained deployment/recovery workflows over in-game server-control commands for infrastructure operations.
6. Treat packet/session/IP debugging output as sensitive.
7. Re-audit this document whenever `CommandsExecutor.java` registration changes.

## Verification source

As of 2026-09-10, the command dispatcher registers levels 0–6 in `CommandsExecutor`, enforces the numeric minimum rank centrally, recognizes `@` for players and `@`/`!` for GMs, and blocks command use in jail. This document intentionally reflects **registered source behavior**, including defects, rather than legacy handbook group labels.