---
name: premarket
description: Run the once-a-day morning routine before the open — health check, capture the starting baseline, screen today's names, and write the day's plan. Paper trading only.
allowed-tools: Bash(bash code/run_phase.sh *), Bash(python3 code/*), Read, Edit(state/**), Edit(docs/**), WebSearch, WebFetch
---

# Premarket

Run this once each morning, shortly before the 9:30 AM New York open. It sets up the day. It does
NOT place any orders.

## Steps

0. (Cloud) Pull the latest saved state so this run sees yesterday's learning and any earlier
   output: `bash code/cloud_sync.sh pull` (no-op when running locally).

1. Run the deterministic setup:
   ```bash
   bash code/run_phase.sh premarket
   ```
   This: checks the paper account is reachable, reconciles anything left over, captures today's
   starting equity as the loss-stop **baseline** (`state/day/<today>/open_baseline.json`), clears
   yesterday's day-stop, refreshes positions, and builds a first-draft shortlist into
   `state/day/<today>/levels.json`.
   - If the health check fails (Alpaca down), STOP. Write a one-line note in `docs/plan/<today>.md`
     saying data is unavailable and that the day should not trade. Do not fake a plan.

2. If we are unexpectedly holding anything from a prior day (the morning re-flatten), clear it:
   `python3 code/flatten.py --aggression 2` then `python3 code/flatten.py --verify`.

3. Use the **premarket-strategist** agent to research the morning and write `docs/plan/<today>.md`
   (market mood, big events today, today's names, which setups are armed, the hard limits restated).

4. Use the **day-screener** agent to sanity-check and finalize `state/day/<today>/levels.json`
   (5–10 liquid, moving names with their key levels).

Finally, save state (cloud): `bash code/cloud_sync.sh push premarket`.

Done. The `/tick` routine takes over once the market opens.
