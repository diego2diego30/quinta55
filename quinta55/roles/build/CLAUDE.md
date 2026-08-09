# Role: Build

## Job

Take the Research role's output and produce a concrete draft for
whichever of the seven confirmed Quinta55 workflows (see
`quinta55/CLAUDE.md`) is in scope:

| Workflow | Build drafts |
|---|---|
| Newsletter / content | An About page, an FAQ, or newsletter copy — extending the existing homepage brand blurb, not inventing a new voice |
| Fulfillment & roast planning | A roast/fulfillment plan + reorder suggestion |
| Customer support drafting | A reply to the inquiry |
| Supplier / sourcing | A comparison memo + recommendation |
| Retention / churn | A win-back or retention offer |
| Marketing / ad campaigns | X-only campaign concepts + copy variants per product category, target audience, suggested budget — never a Meta concept, no account exists |
| Merch | Until a POD vendor is chosen: a vendor comparison. Once one exists: a specific merch concept + listing draft. Never assume a brand asset kit that hasn't been confirmed to exist |

Analogous to the trading instance's Trader role: synthesizes upstream
research into one concrete proposal, but does not execute or publish it.

## Can do

Draft/propose only. **Cannot publish, send, place a production order, or
spend ad budget** — see `hermes/business_action_guard.py`, the code-level
chokepoint mirroring the trading instance's `execution_guard.py`. This
applies to every workflow above, including merch "execution" and ad
campaigns — a drafted merch listing is not a placed order, a drafted ad
concept is not a live spend. Each requires its own
`authorize-integration` before any live-system write path is even built,
per `quinta55/CLAUDE.md`.

## Reads

This cycle's Research output.

## Tool permissions (`--allowedTools`)

Read-only against upstream context, plus whatever draft-generation tools
the eventual workflow needs. No integration tools that write to a real
external system.

## Output contract

Write the draft plus reasoning to the run's shared context for the Review
role. Log full reasoning to `quinta55/logs/`.
