# Quinta55 / Diego, Inc. — Business Instance

Second, independently deployed Hermes instance under the Diego, Inc.
umbrella — see [`docs/execution-plan.md`](docs/execution-plan.md), the
authoritative spec, particularly Section A ("Quinta55") and Section 6.

This repo is **fully separate** from the trading instance
([`diego-inc`](https://github.com/diego2diego30/diego-inc)): own
directory tree, own Hermes process/container, own credentials, own
Telegram bot. Nothing here is readable from there, and nothing there is
readable from here.

## Status

**Scaffold only — read the TODO in [`quinta55/CLAUDE.md`](quinta55/CLAUDE.md)
before treating this as ready to run for real.** The isolation boundary,
guard code, and role-separation *pattern* are built and tested. The
actual Quinta55 Reserve business workflows are not — those need Diego's
input on what the business actually needs (order handling? supplier
comms? inventory? content?), which execution-plan.md Section 7 scopes to
"next leave period," not the current build.

- **Business-system writes:** not implemented.
  `hermes/business_action_guard.publish_or_send` always raises
  `NotImplementedError`, mirroring the trading instance's
  `execution_guard.execute_live_order`.
- **Roles:** generic `research` / `build` / `review` placeholders per
  Section 7's "research/build/review roles rather than bull/bear/trader."

## Layout

```
quinta55/            # context read by every claude -p role invocation
  CLAUDE.md            # instance-wide standing instructions (+ TODO)
  MEMORY.md
  memory/
  roles/{research,build,review}/CLAUDE.md
  logs/

hermes/               # orchestrator: config, state, business-write guard,
                       # chain runner, Telegram bridge, CLI entrypoints
tests/                # guard + authorization-state coverage
deploy/               # Dockerfile, compose, systemd, cron, .env.example, runbook
docs/execution-plan.md   # the governing spec, verbatim
```

## Quickstart (local dev, no VPS needed)

```
pip install -r requirements.txt
pytest
```

## What's still missing (do not fabricate — see execution-plan.md Section B instruction 4)

- Real Quinta55 Reserve workflow definitions (what this instance is
  actually for, concretely).
- Real Telegram bot token for this instance (separate from trading's).
- Whatever business-system credentials each future integration needs.
- A run on the actual VPS.
