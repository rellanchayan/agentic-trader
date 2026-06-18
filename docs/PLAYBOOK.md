# PLAYBOOK — the living rulebook the trader reads every day

This is the bot's memory of "how we trade well." The intraday brain reads it on every tick and the
morning strategist reads it before planning. The learning-coach adds to it each night. Keep it short and
made of **rules to follow**, not stories.

> Seed version. The bot will grow this over time from real experience (the changelog at the bottom
> records every change). Lines here are starting principles, not yet battle-tested.

## Discipline (most important)
- Protect the downside first. Manage open positions before hunting new trades.
- When unsure, do nothing. A missed trade costs nothing; a forced trade costs money.
- A real reason is required for every trade. No reason, no trade.
- After two losing trades in a row, slow down and be extra selective.
- Never re-enter a name you just exited unless a brand-new setup triggers.
- Never flip-flop inside the spread (buying and selling pennies apart).

## Time of day
- The first 5 minutes are noisy. Let the opening range (first ~15 min) form before trading breakouts.
- If checks are only ~hourly (cloud mode), use wider stops and smaller size — you cannot babysit
  positions minute-to-minute, so a tight stop can be blown straight through between checks.
- No new entries after 3:30pm ET. Start closing out at 3:50pm. Be flat by 3:56pm.
- Be careful around scheduled events (Fed, CPI, jobs) — prices whip around. Trade smaller or wait.

## Setups by market mood
- **Risk-on (trending up):** favor Opening-Range Breakouts and momentum continuation. Buy strength.
- **Range / quiet:** favor VWAP reclaims and careful mean-reversion. Smaller size.
- **Risk-off (fear/selling):** trade less, smaller, and don't buy breakouts into weakness.

## Entries & exits
- Enter with marketable limit orders so we fill fast but never worse than our price.
- Set the stop at a level that means "the idea was wrong," not just a random number. Honor it instantly.
- Take profit at the target; don't get greedy and give back a winner.
- A typical good trade risks a few hundred dollars to make more than it risks (aim for wins ≥ 1.5R).
- Flatten limits must be set near the current bid at the time of submission, never from a cached or
  stale price. A stale flatten limit will miss the market entirely and leave a position open into the
  close. If the first pass fails to fill, the next pass must re-quote fresh before submitting.

## Sizing
- Size from risk first: lose no more than the per-trade risk budget if stopped.
- Never over $10k per trade, over 25% of equity in one name, over $50k deployed in a day, or over 8 names.

## Infrastructure
- If premarket healthcheck returns 401 Unauthorized, abort the full trading day immediately. Do not
  attempt ticks against a broken API — the loss-stop baseline is never captured, quotes are stale,
  and any order submission will fail silently or with bad data. Log the failure and wait for the
  connection to recover before the next session.

## Changelog (the learning-coach appends here — newest on top)
- 2026-06-18: No tuning. Tuner frozen (only 3 days of history; need 5). 2 round-trips (NVDA win
  +1.36R, MSFT loss -2.803R). Net P&L: +$24.75. ORB setup expectancy across all 3 days of history
  is -0.721R — negative, but not yet enough data to act on. Observation: the MSFT loss was nearly
  3R against a 1.36R winner; asymmetric loss-to-win ratio is the main drag. Until we have 5+ days
  of history the tuner is locked. Watch whether ORB expectancy improves or stays negative.
- 2026-06-17: No tuning. Tuner frozen (only 2 days of history; need 5). No intraday entries today;
  premarket was not run so no day plan was set. Day P&L: -$55.35 from an orphaned overnight GOOGL
  position (inherited, not a new entry). First flatten pass failed: limit was stale at $350.21
  while GOOGL was trading ~$370+ — this is a bug; flatten limits must be set near the current bid,
  not a cached or stale value. Second flatten pass correctly used a marketable limit and filled at
  avg $371.12 (above limit $367.67). Ended flat. Fill rate 50% (1 of 2 passes). Rule added below
  in the flatten section about stale limits.
- 2026-06-16: No tuning. Tuner frozen (only 1 day of history; need 5). Today was a no-trade day —
  Alpaca paper API returned 401 Unauthorized all session. Zero trades, zero P&L, no evidence to
  act on. Operational lesson added to Infrastructure section above.
