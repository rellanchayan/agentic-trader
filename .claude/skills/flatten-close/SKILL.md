---
name: flatten-close
description: End-of-day close-out. Sells everything so we hold nothing overnight. Runs in escalating passes near 3:55pm ET. Paper trading only.
allowed-tools: Bash(bash code/run_phase.sh *), Bash(python3 code/*), Read, Edit(state/**), Edit(docs/intraday/**)
---

# Flatten / Close

Run this near the close (scheduled at 3:50, 3:53, and 3:56 PM New York time) so the account ends the
day FLAT — zero positions overnight. This bot never holds overnight.

## Steps
First (cloud) pull the latest saved state: `bash code/cloud_sync.sh pull`. Then use the
**position-flattener** agent. In one invocation, run the escalating passes in order, checking
after each and stopping as soon as we're flat:
```bash
python3 code/flatten.py --aggression 1
python3 code/flatten.py --verify        # if is_flat → stop here
python3 code/flatten.py --aggression 2
python3 code/flatten.py --verify        # if is_flat → stop here
python3 code/flatten.py --aggression 3
python3 code/flatten.py --verify
```
Each pass first cancels all working orders, then sells every position with marketable SELL limits
(LIMIT + DAY — never market orders), priced more aggressively on each later pass so leftovers fill.
This routine is scheduled to fire twice (≈3:53 and ≈3:57 PM ET) as a safety net; the every-2-minute
`/tick` also flattens once it enters the close window, so usually little is left to do here.

- After aggression 3, if `--verify` still shows positions, do NOT hide it. Log a clear WARNING in
  `docs/intraday/<today>.md` and note it so the next morning's `/premarket` clears it.
- When flat, append a line to `docs/intraday/<today>.md` confirming we ended the day flat.

Finally, save state (cloud): `bash code/cloud_sync.sh push flatten`.

Honesty: only say "flat" when `--verify` shows zero positions.
