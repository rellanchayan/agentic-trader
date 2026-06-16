---
name: postmarket-learn
description: After the close, reconcile fills, write the honest journal and P&L, then let the auto-tuner make one small, safe, reversible improvement. Paper trading only.
allowed-tools: Bash(bash code/run_phase.sh *), Bash(python3 code/*), Read, Edit(state/**), Edit(docs/**)
---

# Postmarket / Learn

Run this once after the close (about 4:30 PM New York time). It records the day truthfully and lets
the bot learn a little.

## Steps

0. (Cloud) Pull the latest saved state: `bash code/cloud_sync.sh pull` (no-op locally).

1. Finalize the numbers and confirm we ended flat:
   ```bash
   bash code/run_phase.sh postmarket
   python3 code/flatten.py --verify
   ```
   This reconciles every order against Alpaca, snapshots equity, and writes the honest day summary to
   `state/runs/<today>-summary.json`. If `--verify` is not flat, flag it loudly in the journal.

2. Use the **journal-writer** agent to write `docs/journal/<today>.md` (result, plan vs reality, every
   trade, what worked, discipline check, 2–3 lessons) and update `docs/trades/<today>.md`. All numbers
   come from the tools — never typed from memory, never hiding a loss.

3. Use the **learning-coach** agent to run the gated auto-tuner and update the playbook:
   ```bash
   python3 code/tuner.py --status
   python3 code/tuner.py --run
   ```
   The tuner does nothing unless there's real evidence and we're not in a losing streak. If it changed
   a setting, it logged a reversible row to `state/tuning_ledger.jsonl`; record the lesson and the
   change in `docs/PLAYBOOK.md`.

Finally, save state (cloud): `bash code/cloud_sync.sh push postmarket`.

That's the full daily cycle: plan → trade through the day → flatten → learn. Tomorrow it repeats.
