# EverLeaf Moderation, Bans, and Appeals

This is the maintained staff procedure for moderation actions that affect player access or standing. It supplements [`OPERATIONS_AND_INCIDENTS.md`](OPERATIONS_AND_INCIDENTS.md) and the source-authoritative command reference in [`GM_COMMANDS_AND_PERMISSIONS.md`](GM_COMMANDS_AND_PERMISSIONS.md).

The goal is consistent, reviewable moderation without exposing player-sensitive data or using production commands casually.

## Core principles

- Base material actions on server-side evidence whenever available.
- Preserve the evidence and reason **before** destructive cleanup, restart, rollback, or account mutation when practical.
- Use the least restrictive action that safely contains the issue.
- Separate a temporary containment action from a final moderation decision.
- Never request or record a player's password, PIC/PIN, launcher token, session token, or other private authentication secret.
- Never grant, revoke, or alter GM level as a substitute for normal moderation.
- Do not create public spectacle around moderation cases; disclose only what is operationally necessary.

## Evidence to preserve

For bans, appeals, suspected account compromise, or economy abuse, preserve as applicable:

- UTC/local timestamp and time zone;
- account ID and character ID/IGN needed for investigation;
- world/channel/map;
- relevant server logs;
- transaction, trade, storage, merchant, shop, reward, or command evidence;
- staff commands/actions already taken;
- screenshots/video only as supporting evidence, not the sole authority when server-side evidence exists;
- current release/source SHA for a bug/exploit case;
- reason for the restriction and who approved it.

Do not paste private IP/MAC/session information into public GitHub issues or community channels. Use restricted staff evidence storage where such data is actually necessary.

## Containment choices

### Warning / support intervention

Use when behavior appears accidental, low-impact, or caused by confusion and no persistent-state protection is required.

Record the issue if repeated behavior may later matter.

### Jail

`!jail <IGN> [minutes]` is a temporary in-game containment tool. Current source defaults to five minutes and prevents command use while the character is in jail.

Appropriate uses include briefly stopping disruptive live behavior while staff reviews evidence. Jail is not a permanent sanction and should not be used as a substitute for a documented ban decision.

### Disconnect

A targeted disconnect can stop an active session without changing account ban state. Use it when the session itself must end but the evidence does not yet justify a ban.

### Feature restriction / service containment

For an active exploit or economy-corruption path, prefer disabling/restricting the smallest affected feature when possible. Escalate to broader shutdown only when persistent player/economy state cannot otherwise be protected.

### Ban

Current source syntax:

```text
!ban <IGN> <reason>
```

A descriptive reason is required. For an online target, the current implementation applies character/account ban behavior, attempts IP/MAC restrictions, notifies the target, schedules disconnect, and broadcasts that the character was banned. Offline-name banning uses the server's static character ban path.

Because the implementation may touch multiple restriction mechanisms, do not use `!ban` experimentally on production.

## Ban decision procedure

1. **Classify the incident.** Determine whether it is harassment/disruption, cheating/automation, exploitation, economy abuse, account compromise, impersonation, or another policy/security case.
2. **Preserve evidence.** Capture the minimum evidence necessary to support the action.
3. **Protect persistent state.** If an exploit may still be minting/corrupting state, contain the affected system before spending time on perfect classification.
4. **Check for a technical root cause.** If the behavior depends on a server/client defect, open/track the defect separately from the player moderation case.
5. **Determine scope.** Decide whether the restriction should apply only to the current session, character, account, or related network identifiers based on verified evidence.
6. **Write the reason before executing.** The reason should say what behavior/evidence justified the action, not merely "hacking" or "bad player."
7. **Execute the approved action.** Use the current registered command or controlled administrative path.
8. **Verify state.** Confirm the player is actually restricted and that no accidental unrelated account/state mutation occurred.
9. **Record staff action.** Preserve who acted, when, why, and what evidence was used.
10. **Separate remediation.** If illegitimate items/mesos/currency were created, reconcile those gains as a separate persistent-state task rather than assuming the ban automatically repairs the economy.

## Reason-writing standard

A useful internal ban reason contains:

- observed behavior;
- relevant timestamp/session or transaction reference;
- concise evidence basis;
- whether the case is tied to a known exploit/bug;
- staff identity/action source.

Avoid jokes, insults, speculation, or unnecessary personal information in permanent moderation records.

## Appeals

Appeals should be reviewed by someone other than the original moderator when practical for significant/contested bans.

### Appeal intake

Request only information needed to locate and review the case, such as:

- account/character identifier;
- approximate ban time;
- the player's explanation;
- any relevant screenshot/log the player already possesses.

Never ask the player to send a password, PIC/PIN, token, or other credential to prove ownership.

### Appeal review

1. Locate the original moderation record/evidence.
2. Verify the action against server-side logs/data where available.
3. Check whether later bug fixes or incident findings changed the interpretation of the evidence.
4. Check whether state/economy remediation is still required even if access is restored.
5. Decide: uphold, modify, or reverse.
6. Record the decision and rationale.
7. Communicate only the necessary outcome to the player; do not expose private detection methods, another player's data, or still-exploitable reproduction details.

## Unban procedure

Current source syntax:

```text
!unban <IGN>
```

The command resolves the account from the character name, updates the account's `banned` field, and deletes matching IP/MAC ban rows for the account.

Before unbanning:

1. confirm the appeal/decision is approved;
2. confirm the target IGN/account is correct;
3. record the prior restriction reason and the reason for reversal;
4. determine whether illegitimate gains or corrupted state need separate remediation;
5. execute `!unban <IGN>`;
6. verify login/access behavior through an appropriate test rather than assuming the command corrected every related account problem.

Do not use unban to fix unrelated login/account-recovery failures.

## Economy/exploit cases

A player sanction and a technical/economy response are separate tracks.

For a dupe/exploit case:

- preserve logs and affected identifiers;
- stop the exploit path if still active;
- back up before broad persistent-state changes;
- reproduce on staging/disposable QA, not with normal production players;
- fix the authoritative server-side validation/transaction behavior;
- add regression coverage where practical;
- identify illegitimate gains;
- apply targeted state remediation where safe;
- record whether other accounts may have received transferred gains.

Application rollback does not automatically undo database mutations already committed by the exploit.

## Account compromise

Do not automatically punish the account owner solely because suspicious actions came from the account. Preserve session/network/action evidence and coordinate with the account-recovery procedure.

When compromise is plausible:

- contain access if continued use risks more damage;
- preserve evidence;
- avoid disclosing sensitive session/network data to the claimant;
- verify account ownership through the supported recovery process;
- reset/restore access through approved account tooling, not by asking for the old password;
- investigate economy/item transfers separately.

## Staff misconduct / command abuse

GM commands that create items, NX, mesos, stats, levels, rates, or alter accounts are auditable privileged actions and must never be used to benefit a personal/player account outside an approved test/support/remediation case.

Suspected staff-command abuse should be preserved and reviewed like any other security incident. Do not let the same person erase the only evidence of their own action.

## Closure checklist

A moderation case is closed when:

- access/restriction state matches the approved decision;
- the reason/evidence record is preserved;
- any related exploit/bug is separately tracked;
- any persistent economy/state remediation is complete or explicitly pending;
- the appeal status, if any, is recorded;
- no credentials or unnecessary player-sensitive data were exposed during handling.
