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

## Sizing
- Size from risk first: lose no more than the per-trade risk budget if stopped.
- Never over $10k per trade, over 25% of equity in one name, over $50k deployed in a day, or over 8 names.

## Changelog (the learning-coach appends here — newest on top)
- _(none yet — the bot will record each learned change and each auto-tune step here)_
