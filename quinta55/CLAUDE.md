# Quinta55 Instance — Standing Instructions

This file is read as context by every `claude -p` invocation in the
Quinta55 instance and by Hermes itself. Top-level policy layer; role
CLAUDE.md files under `roles/` narrow it further and must never
contradict it.

## Business context (defined 2026-08-09)

Quinta55 Reserve sells coffee (single-origin, blends, flavored, sample
packs) and tea direct-to-consumer at quinta55reserve.com — Shopify,
one-time-purchase only, no active subscriptions yet. 71 products, no
blog/About page/FAQ currently live. Brand voice seed (from the homepage,
nothing more formal exists): estate-sourcing story — "Quinta" estates,
ethically grown, roasted to order, honoring growers and the roasting
process.

**Confirmed workflows this instance supports** — see `roles/*/CLAUDE.md`
for the concrete Research/Build/Review scope of each:

1. Newsletter / content (About page, FAQ, newsletter copy — the highest
   near-term-value workflow given the current content gap)
2. Fulfillment & roast planning
3. Customer support drafting — **blocked**: support will be handled via
   Gmail, but no dedicated Quinta55 support address exists yet (must be
   its own address, not Diego's personal Gmail, per the isolation
   boundary below). Nothing for Research to read until that address is
   created.
4. Supplier / sourcing research
5. Retention / churn
6. Marketing / ad campaigns — **X only, no Meta** (no Meta ad account
   exists or is planned)
7. Merch — genuinely undecided on everything: no POD vendor chosen (not
   even a leaning), no existing brand asset kit (logo file / palette /
   fonts) beyond what's visible on product photos. First merch cycle
   should be vendor research + a starter asset-kit compilation, not a
   finished listing — do not assume a vendor to move faster.

**Not yet done:** the role CLAUDE.md files below describe workflow
*scope and gates*. The actual tool wiring (Gmail MCP, Shopify Admin API,
X API, a POD vendor's API) is separate infrastructure work — today
`ROLE_ALLOWED_TOOLS` in `hermes/orchestrator.py` only grants local
Read/Grep/Glob, so no role can yet reach any of these systems. Wiring
those is Section 4-equivalent work, not covered by this spec.

## What this instance is

A second, independently deployed Hermes instance for Quinta55 Reserve
(the family coffee business) and general Diego, Inc. work — deployed per
execution-plan.md Section 7 timeline as "next leave period" work, not the
current Aug 2026 leave window. This scaffold exists now only because
Diego asked for both instances architected together; treat the
directory/container/credential separation as final, but treat the
workflow content inside `roles/` as a draft to be replaced once real
business requirements exist.

## Isolation boundary (do not cross)

- Nothing under `/opt/ecosystem/quinta55/` is readable from, writable by,
  or referenced by the Trading instance (a separate repo:
  `diego2diego30/diego-inc`), and vice versa.
- No personal/admin content (Poke's domain) belongs here.
- No trading credential, account state, or trading strategy detail may
  appear anywhere in this tree, in `quinta55/logs/`, or in
  `quinta55/memory/` — see execution-plan.md Section 6.

## No live business-system writes until confirmed

Mirrors execution-plan.md Section B instruction 2 (written for trading,
but the "real business-system writes" clause is explicit and applies
here): agents in this instance may research, draft, and propose, but must
not write to a real accounting system, e-commerce platform, or any other
live business system until Diego has reviewed the specific integration
and explicitly authorized it. `hermes/business_action_guard.py` is the
code-level chokepoint for this — treat a refusal from it as final, the
same way the trading instance treats `execution_guard` refusals.

## Reasoning logs

Every chain run writes one log entry per role to `quinta55/logs/`, same
format as the trading instance (`hermes/logging_utils.py`) — not just the
final output.

## Memory discipline

`MEMORY.md` is the auto-memory index. Only durable, cross-cycle facts
belong there. No trading content, ever. Per Section 6, review additions
periodically rather than trusting silent accumulation.
