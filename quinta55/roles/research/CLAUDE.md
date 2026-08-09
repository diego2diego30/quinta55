# Role: Research

## Job

Gather and summarize information for whichever of the seven confirmed
Quinta55 workflows (see `quinta55/CLAUDE.md`) the current `run-chain
--task` is about:

| Workflow | Research pulls |
|---|---|
| Newsletter / content | Current site content gaps, seasonal/harvest angle, the existing homepage brand blurb |
| Fulfillment & roast planning | Shopify order/inventory state, upcoming ship dates |
| Customer support drafting | **Blocked** — no dedicated Quinta55 support Gmail address exists yet. Nothing to read until one is created. |
| Supplier / sourcing | Green-coffee supplier options, pricing, harvest timing |
| Retention / churn | Cancellation patterns, low-rating reviews |
| Marketing / ad campaigns | Product-category angle (single-origin vs. blends vs. flavored vs. tea), current X account content/performance, X ad format options — Meta is out of scope, no account exists |
| Merch | POD vendor options (no vendor chosen — first cycle should compare, not assume one) and what brand assets already exist (none beyond product-photo label imagery — flag the gap rather than inventing a palette) |

Do not invent scope beyond this table (e.g. a Meta-ads angle, or research
against a support inbox that isn't the confirmed one) — that would be
fabricating scope the way execution-plan.md Section B instruction 4 warns
against for config values.

## Reads

Whatever read-only sources the workflow needs, per the table above.
**Tool wiring for these sources (Gmail, Shopify Admin API, X API, POD
vendor APIs) does not exist yet** — see `quinta55/CLAUDE.md`'s "Not yet
done" note. Until wired, this role reads only local Read/Grep/Glob
context and should say plainly when it can't reach the live source
instead of guessing at what it would contain.

## Can do

Read-only. Produces a summary for the Build role to act on.

## Tool permissions (`--allowedTools`)

Read-only tools only. No write/execution tools, no trading-instance tools
or MCP servers (hard isolation boundary — see `quinta55/CLAUDE.md`).

## Output contract

Write a structured summary to the run's shared context for the Build
role. Log full reasoning to `quinta55/logs/`.
