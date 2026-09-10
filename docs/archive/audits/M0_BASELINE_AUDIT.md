# M0 Baseline Audit

## Current foundation

Enhanced Classic is forked from Cosmic, a GMS v83 emulator based on HeavenMS.

The upstream project already provides:

- Java 21 server runtime
- Maven wrapper and fat-JAR build
- MySQL database scripts
- GitHub Actions build workflow
- Docker support (optional; not required for this project)
- JavaScript content scripts
- Configurable EXP, meso, drop, boss-drop, quest, fishing, and travel rates

## Immediate findings

### 1. Development rates do not match Enhanced Classic targets

Current Scania defaults are:

- EXP: 10x
- Meso: 10x
- Drop: 10x
- Boss drop: 10x
- Quest multiplier: 5x

Enhanced Classic initial development targets are:

- EXP: 5x
- Meso: 3x
- Drop: 2x
- Boss drop: 2x
- Quest rewards: independently rebalanced rather than blindly stacking a large global multiplier

This is the first gameplay configuration change to land after the baseline build is verified.

### 2. Configuration is not production-safe yet

`config.yaml` currently exposes database host/user/password settings directly and defaults to the MySQL `root` account with a blank password. That is acceptable only as a local placeholder and must not become the deployment pattern.

Required work:

- Environment-variable overrides for DB credentials and public host/IP
- Dedicated least-privilege DB user for deployment
- Safe dev/test/prod configuration strategy
- No committed production credentials

### 3. Automatic registration is enabled

This is convenient for local development but should be reconsidered before a public alpha. Public account creation should eventually be rate-limited and routed through the website/account service or otherwise hardened.

### 4. Rate coupons require a No-P2W review

The base configuration enables rate coupons in the Cash Shop. Enhanced Classic's No-P2W rule means any EXP/drop/meso advantage linked to donations or paid currency must be removed, disabled, or redesigned before launch.

### 5. HP/MP behavior requires a dedicated audit

The base includes several HP/MP and AP-reset related flags. Enhanced Classic's requirement is stronger than merely changing one flag: intended bosses must be survivable by properly progressed characters without legacy HP washing.

The implementation should be based on job progression and encounter requirements, not an arbitrary global HP multiplier.

### 6. CI needed to cover `enhanced-dev`

Upstream CI only built pull requests targeting `master`. The Enhanced Classic branch now has a modified workflow that also builds pushes and pull requests involving `enhanced-dev`, uses current GitHub Actions releases, enables Maven caching, and uses the Maven wrapper for reproducibility.

Forked repositories can require GitHub Actions to be manually enabled before workflows will run. Verify Actions status before treating CI as active.

## M0 execution order

1. Verify GitHub Actions/build execution on `enhanced-dev`.
2. Confirm Maven package succeeds unchanged.
3. Harden configuration and secret handling.
4. Establish Enhanced Classic rate defaults.
5. Disable/review monetization-adjacent power systems such as purchasable rate coupons.
6. Map the HP-washing-related code paths and boss HP requirements.
7. Add smoke/regression tests for login, character persistence, EXP gain, drops, and configuration loading.
8. Prepare a low-storage remote deployment path that does not require Docker locally.

## Definition of M0 complete

M0 is complete when:

- `enhanced-dev` builds reproducibly in CI
- configuration can be deployed without committed secrets
- the server can boot against a clean database
- a test account can enter the world and persist character state
- basic combat/EXP/drop behavior has regression coverage
- Enhanced Classic rate policy is represented in configuration
- no known paid-power mechanism is enabled by default
