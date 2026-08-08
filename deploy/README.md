# Deploying the Quinta55 instance to the VPS

Same caveat as the trading instance's deploy README: this session built
code and deploy artifacts only, with no SSH access to your Cloudflare
VPS. Run these steps yourself, or from a local Claude Code CLI session
with real access to the VPS.

## Before deploying: this instance has no defined workflows yet

Read the TODO at the top of `quinta55/CLAUDE.md`. The directory
structure, isolation boundary, guard code, and CI-testable pieces are
real and finished. The actual business logic (what Research/Build/Review
do day to day) is a placeholder until Diego specifies real Quinta55
Reserve workflows. Deploying this now stands up working infrastructure
with nothing meaningful for it to do yet — which may be fine (per
execution-plan.md Section 7, this instance's real build-out is scoped to
"next leave period," not now) or you may want to hold off until the
workflows are defined.

## 1. Checkout on the VPS

```
sudo mkdir -p /opt/ecosystem
cd /opt/ecosystem
git clone <this repo's URL> quinta55-repo
cd quinta55-repo
```

`quinta55/` inside this checkout is `/opt/ecosystem/quinta55/` from
execution-plan.md Section A, as long as you check out at
`/opt/ecosystem/quinta55-repo` (named to avoid colliding with the
`quinta55/` subdirectory itself).

## 2. Fill in real configuration

```
cp deploy/.env.example deploy/.env
$EDITOR deploy/.env
```

A **different** Telegram bot from the trading instance — see Section 6.

## 3. Build and start the Telegram daemon

```
docker compose build
sudo cp deploy/systemd/quinta55-hermes.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now quinta55-hermes
```

## 4. Run the test suite

```
pip install -r requirements.txt
pytest
```

## 5. Cron

Nothing installed by default — see `deploy/cron/quinta55-crontab` for why,
and add a line once a real cadence exists.

## Isolation checklist (verify on the VPS, not just in the repo)

- Separate container from the trading instance (`docker compose ps`
  should show `quinta55-hermes` and `diego-trading-hermes` as distinct
  containers, distinct images).
- Separate `deploy/.env` — no token/key present in both repos' `.env`
  files.
- Separate Docker volume (`quinta55-data` vs `trading-data`) — confirm
  with `docker volume ls`.
