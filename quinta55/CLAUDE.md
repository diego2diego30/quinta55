# Quinta55 Instance — Standing Instructions

This file is read as context by every `claude -p` invocation in the
Quinta55 instance and by Hermes itself. Top-level policy layer; role
CLAUDE.md files under `roles/` narrow it further and must never
contradict it.

## TODO — this file is a skeleton, not a finished spec

execution-plan.md Section 6 calls for "business goals, design ethos,
career-direction notes, Quinta55 operational details" here. None of that
exists yet — this scaffold was built without it, per Section B
instruction 4 ("request missing configuration explicitly... rather than
assuming or fabricating placeholder values"). Before this instance does
real work, Diego needs to fill in:

- What Quinta55 Reserve actually needs AI-agentic support for (orders?
  inventory? customer comms? supplier coordination? marketing copy?)
- What "research / build / review" concretely means for each of those
  workflows (see `roles/`, currently generic placeholders)
- What systems it needs to touch (accounting software, e-commerce
  platform, POS, email, socials) and what credentials/scopes each needs
- Design ethos / brand voice constraints, if agents will produce
  customer-facing content

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
