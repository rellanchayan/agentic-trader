---
name: tick
description: The every-2-minutes trading loop. Runs a fast safety gate, and if clear, decides what to buy/sell/hold right now. Paper trading only.
allowed-tools: Bash(bash code/run_phase.sh *), Bash(python3 code/*), Read, Edit(state/**), Edit(docs/intraday/**)
---

# Tick

This runs every 2 minutes while the market is open. Keep it lean and fast.

## Step 1 — the safety gate (always)
First (cloud) pull the latest saved state, then run the gate:
```bash
bash code/cloud_sync.sh pull
bash code/run_phase.sh tick
```
This runs `preflight.py` (cheap, no thinking) and prints a JSON verdict. Read it and branch on the
verdict:

- **EXIT** (market closed / `.HALT_TRADING` present / loss-stop already active / Alpaca unreachable):
  do NOTHING. Append one short line to `docs/intraday/<today>.md` saying why (e.g., "12:00 — skipped,
  market closed"). Stop here. (If `.HALT_TRADING` exists, never delete it.)

- **FLATTEN** (today's loss reached −$3,000 — the loss-stop just tripped): immediately run the close-out
  hard, then stop for the day:
  ```bash
  python3 code/flatten.py --aggression 3
  python3 code/flatten.py --verify
  ```
  Log it clearly in `docs/intraday/<today>.md` ("LOSS-STOP hit, flattening, halted for the day"). The
  day-stop is now active, so later ticks will EXIT on their own.

- **PROCEED**: the gate also already built `state/day/<today>/tick_context.json`. Continue to Step 2.

## Step 2 — decide and act (only on PROCEED)
Act as the **intraday-trader** — follow the steps in `.claude/agents/intraday-trader.md` exactly:
read the context snapshot + `docs/PLAYBOOK.md` + `docs/plan/<today>.md`, manage existing positions
first (stops/targets), then look for the best new entry, size it, write the order file, run BOTH
guards (`constitution.py --check` and `daytrade_guard.py --check`), and only submit if both PASS.

Always finish by logging the tick (one row in `state/day/<today>/intraday_log.jsonl`, one plain line
in `docs/intraday/<today>.md`, and the full record in `state/day/<today>/ticks/<HHMMSS>.json`) — even
when you decide to do nothing.

## Before you stop (every branch)
Save state so the next run remembers this one: `bash code/cloud_sync.sh push tick`.

Then stop. You will wake again next interval. Never claim a fill — only `--reconcile` confirms fills.
