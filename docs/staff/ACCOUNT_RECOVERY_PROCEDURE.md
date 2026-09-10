# EverLeaf Staff Account Recovery Procedure

This procedure documents how staff should handle the current website recovery queue. The public-facing behavior is documented in [`../player/ACCOUNT_RECOVERY.md`](../player/ACCOUNT_RECOVERY.md).

## Current system behavior

The website `/recover` form accepts a username or valid email and creates a CMS `account_recovery_requests` row with status `pending`. Duplicate pending requests matching the supplied username/email within the previous day are suppressed. The public page deliberately returns the same success response regardless of whether an account exists so it cannot be used for account enumeration.

The admin CMS exposes recovery requests by status and permits transitions among:

- `pending`
- `resolved`
- `rejected`

Status changes are written to the CMS audit log as `recovery.update` actions.

The current code does **not** send an automated password-reset token/email. Staff review is therefore part of the supported flow.

## Intake

1. Open the authenticated CMS recovery queue.
2. Work from `pending` requests.
3. Identify the request by its queue ID plus the supplied username/email.
4. Do not tell an unauthenticated requester whether a supplied username/email exists until ownership has been sufficiently established.
5. Do not ask for the claimant's password, PIC/PIN, session token, launcher token, authentication cookie, or unrelated private credential.

## Verification

Use the minimum reliable account/server evidence available. Depending on the case this can include:

- the account record matching the submitted username/email;
- character names/IDs associated with the account;
- approximate account/character history the claimant can reasonably know;
- prior support/recovery context;
- server-side login/account evidence when compromise is alleged.

Do not treat publicly visible character/ranking information as sufficient proof of account ownership by itself.

For suspected compromise, preserve relevant login/session/economy evidence under the moderation/incident procedures before making broad state changes.

## Resolution choices

### Resolve

Mark `resolved` only after the supported account-access action has actually been completed and staff has a record of what was done.

The queue status itself does not change game credentials; it only records recovery workflow state.

### Reject

Mark `rejected` when ownership cannot be sufficiently established, the request is clearly unrelated/invalid, or the requested action would improperly bypass a moderation restriction.

A ban appeal is not a password-recovery request. Route banned accounts through [`MODERATION_AND_APPEALS.md`](MODERATION_AND_APPEALS.md).

### Keep pending

Leave `pending` while evidence/review is incomplete. Do not mark resolved simply to clean the queue.

## Password/access changes

Use only the approved current administrative/account-management path. Never set a known/shared staff password on a player account or send a plaintext password through public chat.

If the available production tooling does not yet provide a safe supported credential-reset action, do not improvise a direct SQL mutation merely to close the ticket. Escalate the tooling gap and keep the request pending/rejected as appropriate.

## Compromised-account cases

1. Preserve relevant evidence.
2. Contain ongoing unauthorized access when necessary.
3. Verify ownership separately from the suspicious session/activity.
4. Restore account access through the approved credential path.
5. Investigate transferred items/mesos/currencies separately; restoring login access does not automatically repair economy state.
6. If cheating/exploitation is involved, keep moderation and technical exploit work as separate records.

## Privacy and communication

- Never disclose another account's email, IP/MAC, session details, or private activity to a claimant.
- Never confirm account existence merely because somebody submits a recovery form.
- Communicate the outcome and next action without exposing internal detection/security details.
- Keep unnecessary personal information out of GitHub/public logs.

## Audit trail

For material recovery cases, preserve:

- recovery queue ID;
- reviewer;
- decision time;
- verification basis (without unnecessary sensitive data);
- account-access action performed;
- whether compromise/economy/moderation follow-up exists.

The CMS status transition is automatically audit-logged, but staff should still retain enough case context to explain why the transition was appropriate.

## Future self-service recovery

If EverLeaf later implements verified email-token password reset, this document must be re-audited against that deployed flow. Until then, do not tell players that the current `/recover` request automatically sends or completes a password reset.