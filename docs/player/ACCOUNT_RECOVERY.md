# EverLeaf Account Recovery and Support

This guide documents the **current** EverLeaf account-recovery flow. It does not promise an automated password-reset email system that the current code does not provide.

## Current recovery flow

Use the official EverLeaf website recovery page:

```text
https://everleafms.online/recover
```

The form accepts either:

- an account username of at least 3 characters, or
- a valid account email address.

After submission, the site intentionally returns the same success response whether or not the supplied account details exist. This prevents the recovery form from being used to discover valid usernames/email addresses.

A duplicate pending request using the same supplied username/email within roughly one day is not inserted again.

## What happens after submission

Recovery requests enter the staff CMS recovery queue with one of three states:

- `pending`
- `resolved`
- `rejected`

The current implementation is a **staff-reviewed recovery queue**. It is not a self-service password-reset-token system and does not automatically email a reset link.

Submitting the form therefore means "send this recovery request for staff review," not "my password is already reset."

## What to provide

Use your normal account username or account email in the recovery form. If staff asks for additional context through an official support channel, useful non-secret information can include:

- character names on the account;
- approximate account creation/use period;
- approximate last successful login;
- description of the problem (forgotten password, suspected compromise, account-access issue, etc.);
- relevant support ticket/recovery-request context.

## Never send these to staff

Do **not** send:

- your current or old password;
- PIC/PIN values;
- launcher/session tokens;
- authentication cookies;
- private SSH/API keys or unrelated personal credentials.

EverLeaf staff should not need those secrets to review a recovery request.

## Suspected compromised account

If you believe someone else accessed your account:

1. Submit the recovery request promptly.
2. State through the official support channel that compromise is suspected.
3. Provide the approximate time you last had normal access and any unusual character/item/meso activity you noticed.
4. Do not publicly post IP addresses, account credentials, exploit details, or screenshots containing secrets.
5. Avoid continuing to share the client/account with anyone while the case is being reviewed.

Staff should treat account ownership/access recovery separately from economy/item remediation. Restoring account access does not automatically restore items/currency transferred during a compromise.

## If the account was banned

The recovery form is not the ban-appeal system. A banned account must be handled through the moderation/appeal process so the underlying restriction and evidence are reviewed rather than bypassed as a password problem.

## If the launcher/game will not log in

A login failure is not automatically an account-recovery problem. Before submitting repeated recovery requests:

- use the official EverLeaf Launcher rather than launching the raw game EXE;
- let the launcher finish update/repair validation;
- note the exact login/client error;
- check whether the website/account surface itself is working;
- report a client/launcher issue if the credentials are known but the managed client cannot connect.

See [`INSTALLATION_AND_SUPPORT.md`](INSTALLATION_AND_SUPPORT.md) for launcher/client troubleshooting.

## Staff handling boundary

The CMS recovery queue records request state and staff status changes. Staff should verify requests using available account/server evidence and an approved recovery procedure; they should not ask for the claimant's existing password as proof.

The public recovery response remains deliberately generic so staff should also avoid telling an unauthenticated third party whether a specific username/email exists.

## Current limitation

EverLeaf does not currently expose a fully automated email-token reset flow in the documented production implementation. Until such a system is deliberately implemented, tested, and deployed, this staff-reviewed queue is the supported recovery path.