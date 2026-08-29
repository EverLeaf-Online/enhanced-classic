# EverLeaf disposable QA stack

This stack is the runtime target for EverLeaf's QA agents. It is deliberately separate from production.

## Isolation guarantees

- Uses a dedicated Docker Compose project: `everleaf-qa`.
- Uses its own MySQL container and named volume: `everleaf-qa-db`.
- Never reads production MySQL credentials.
- Game/login/channel ports bind to `127.0.0.1` only by default.
- QA DB binds to `127.0.0.1` only.
- Production services (`everleaf.service`, web, Discord, backups) are not referenced.
- Runtime tester still refuses `environment=production` and non-`qa_` accounts.
- Destroying the QA database requires a second explicit reset token.

The game container keeps its normal internal MapleStory ports (8484 and 7575-7582), while the host exposes isolated QA ports 18484 and 17575-17582. This avoids collisions with production.

## First install on the QA host

From a clone/worktree of the `qa-agent-hub` branch:

```bash
cp deploy/qa/.env.qa.example deploy/qa/.env.qa
```

Generate a strong random password and place it only in `.env.qa` as `EVERLEAF_QA_DB_ROOT_PASSWORD`. The real `.env.qa` must remain uncommitted.

Start the disposable stack:

```bash
chmod +x deploy/qa/qa-stack.sh
deploy/qa/qa-stack.sh up
```

Check it:

```bash
deploy/qa/qa-stack.sh status
deploy/qa/qa-stack.sh logs qa-game
deploy/qa/qa-stack.sh ports
```

## QA accounts

`config.yaml` has automatic registration enabled. Only accounts beginning with `qa_` should be used with the runtime harness. Recommended initial accounts:

- `qa_runner` — persistence/progression/world tests
- `qa_peer` — second client for trade/concurrency tests
- `qa_storage` — storage/shop conservation scenarios

Do not reuse production usernames/passwords. These accounts exist only inside `everleaf-qa-db`.

## Connecting a Windows QA client

Nothing is publicly exposed by default. Use an SSH tunnel or temporarily add a firewall-restricted binding for the tester machine. Do not open the QA ports to the Internet.

Because `config.yaml` advertises `127.0.0.1`, an SSH-tunnel/local-client arrangement is the safest initial mode. A later dedicated QA client configuration can advertise a private/VPN address if needed.

## Runtime harness

First validate a scenario without executing actions:

```bash
python3 tools/qa/everleaf_runtime_qa.py run --environment staging --account qa_runner --adapter tools/qa/adapters/qa-staging.example.json --scenario reconnect --mode persistence --json build/runtime-qa.json
```

A real action requires both `--allow-actions` and a deliberately exported arming token:

```bash
export EVERLEAF_QA_RUNTIME=I_UNDERSTAND_STAGING_ONLY
```

Do not persist that token in `.env.qa`.

## Resetting the disposable DB

Normal `down` preserves QA data. A destructive reset is intentionally double-gated:

```bash
export EVERLEAF_QA_RESET=I_UNDERSTAND_QA_DATA_WILL_BE_DELETED
deploy/qa/qa-stack.sh reset
```

This removes only the `everleaf-qa` Compose volumes. It does not reference production paths or services.

## Production boundary

Never change the runtime tester environment from `staging`, `disposable`, or `local-qa` to production. Never point the QA adapter at `/opt/everleaf/current`, production MySQL, or real player accounts. Promotion of a QA finding into a production change remains a separate reviewed deployment step.
