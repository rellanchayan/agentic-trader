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
- Do not enter a momentum or ORB continuation trade more than 90 minutes after the opening range
  that seeded the thesis. A late entry inherits the risk of a mature trend reverting but misses
  the early reward; if the setup was not actionable at the open, skip it for the day.
- Be careful around scheduled events (Fed, CPI, jobs) — prices whip around. Trade smaller or wait.

## Setups by market mood
- **Risk-on (trending up):** favor Opening-Range Breakouts and momentum continuation. Buy strength.
- **Range / quiet:** favor VWAP reclaims and careful mean-reversion. Smaller size.
- **Risk-off (fear/selling):** trade less, smaller, and don't buy breakouts into weakness.
- When sector-wide selling is confirmed premarket (multiple names in a sector all gapping down),
  deprioritize gap-bounce theses in that sector for the full session. A single-name bounce thesis
  while the surrounding sector is under broad selling pressure is swimming against the tide; wait for
  the sector to stabilize before buying any name in it.

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
- Source market hours from the Alpaca /clock endpoint at the start of every premarket run, before
  writing the day plan. Never infer market hours from the calendar date or from assumptions about
  holiday schedules — early closes and schedule deviations appear in the clock response, not in
  calendar logic. An incorrect close-time assumption will corrupt every time-of-day rule in the plan.
- If docs/day_plan.md does not exist at 9:30 AM ET, treat it as a HALT condition and do not run
  any tick cycles. A missing plan means the premarket phase did not complete, the watchlist is
  unknown, the loss-stop baseline was not captured, and there is no record of market context or
  candidate setups. A session without a plan is an invisible session that cannot be reviewed or
  learned from. The premarket phase must write docs/day_plan.md every trading day — even if the
  only entry is "no setups qualify today."
- The tick loop must write at least one entry to the intraday log on every cycle it runs, even if
  that entry only records "tick HH:MM — no action — reason: [X]." A session that shows zero intraday
  log entries must be treated as a suspected broken or non-running tick loop, not a confirmed
  no-trade decision. The two outcomes look identical from the outside; only the log can distinguish
  them. Two consecutive sessions with no intraday log (2026-06-26 and 2026-06-29) despite non-trivial
  premarket setups is a strong signal the loop is not running. Verify the tick loop is actually
  being scheduled and executing before the next trading session.

## Changelog (the learning-coach appends here — newest on top)
- 2026-07-02: No tuning. Tuner was eligible ("ok to tune", 13 days of history, drawdown 0.01%) but
  no rule fired — parameters left unchanged. Today was a no-trade day: 0 trades, 0 round-trips,
  $0.00 realized P&L, account equity $999,662.83. A day plan was written (progress), but it was
  built on an incorrect market-hours assumption (expected 1 PM early close; market ran normal hours).
  The tick loop had one visible log entry at 13:39 ET for the entire session — one entry across a
  full session is not a reviewable audit trail; the existing rule requires one entry per cycle, not
  per session. Two rules added tonight: (1) Infrastructure — always source market hours from the
  Alpaca /clock endpoint before writing the day plan, never from calendar assumptions. (2) Setups —
  when sector-wide selling is confirmed premarket, deprioritize gap-bounce theses in that sector for
  the full session. The third lesson (tick loop must log every pass) was already in the playbook; no
  duplicate added. Sample still 9 trades across 13 days; both tracked setups remain negative
  expectancy (ORB -0.721R, momentum -0.975R). No parameter has ever been changed; all settings
  remain at their defaults.
- 2026-07-01: No tuning. Tuner was eligible ("ok to tune", 12 days of history, drawdown 0.01%) but
  no rule fired — parameters left unchanged. This is the correct call. Today is the fourth
  consecutive session with no day plan and no intraday log written (2026-06-26, 2026-06-29,
  2026-06-30, 2026-07-01). Account equity $999,661.12, $0 realized P&L, ended flat. Four
  consecutive empty sessions is an infrastructure failure, not a trading signal. Tuning parameters
  against a scheduler that is not running is tuning against silence: the inputs to every tunable
  rule (fill rate, entry quality, stop placement) have had zero new observations for four days.
  Any change made tonight would be calibrated to nothing. The sample remains 9 total trades over
  12 days (0.75 trades/day). Both tracked setups stay in negative expectancy: ORB -0.721R (2
  trades), momentum -0.975R (1 trade). Nine trades is not enough to separate bad parameters from
  bad luck or from a broken execution loop — all three explanations are consistent with the data.
  The tuner will stay hands-off until the tick loop is confirmed running on every session and at
  least one clean winning round-trip appears in fresh history. The immediate priority is not
  parameter tuning; it is verifying that premarket runs and writes docs/day_plan.md and that the
  tick loop executes and writes at least one line to the intraday log every session.
- 2026-06-30: No tuning. Tuner was eligible ("ok to tune", 11 days of history, drawdown 0.01%) but
  no rule fired — parameters left unchanged. This is the correct call. Zero trades today for the
  third consecutive session (2026-06-26, 2026-06-29, 2026-06-30), all ending flat with $0 realized
  P&L. The statistics that back this decision: 9 total trades over 11 days (0.82 trades/day), win
  rate 22%, avg win +0.60R, avg loss -1.46R. Both tracked setups are in negative expectancy: ORB
  -0.721R (2 trades), momentum -0.975R (1 trade). With only 9 total trades across 11 sessions, there
  is not enough evidence to distinguish bad parameters from bad luck or from a broken execution loop.
  Adjusting any parameter on this sample would be chasing noise. The three consecutive no-trade
  sessions are concerning for a different reason: no trades means no new evidence about entry quality
  or stop placement, and no evidence means the tuner has nothing real to act on — every evening it
  will reach the same conclusion until live round-trips resume. The tuner should stay hands-off until
  the tick loop is confirmed running, day plans are being written, and at least one clean winning
  round-trip appears in the history to demonstrate positive expectancy is achievable.
- 2026-06-29: No tuning. Tuner was technically eligible (10 days of history, drawdown 0.01%, freeze
  status returned "ok to tune") but no rule fired — parameters left unchanged. This is correct: the
  evidence for any specific parameter adjustment is absent, because the problem is not the parameters
  — it is that trades are not being placed at all. Zero trades today despite a strong RISK-ON setup
  (NVDA +5.4% premarket, ceasefire catalyst), account equity $999,661.14, ended flat. This is the
  second consecutive session with no intraday log written. A missing intraday log is a critical
  diagnostic gap: without it, there is no way to distinguish a disciplined no-trade call from a
  broken tick loop that ran silently and found nothing. Both outcomes look identical from the outside.
  The tick loop must write at least one line to the intraday log on every cycle it runs — even if
  that line is only "tick at HH:MM, no action, reason: [X]." A session that shows zero log entries
  must be treated as a suspected broken loop, not a confirmed no-trade decision. Rule added to
  Infrastructure section below. The tuning ledger has no entries (no parameter has ever been
  changed); all settings remain at their defaults. The freeze will stay lifted as long as the last-3-
  days window is not net-negative, but there is nothing to tune until live trades generate real
  evidence about entry quality and stop placement.
- 2026-06-26: No tuning. Tuner frozen (last 3 days net-negative — not optimizing during a losing
  streak). Zero trades today: 0 round-trips, $0 P&L, ended flat, loss stop not hit. Account equity
  $999,757.32 (-0.02% total return). The no-trade call was correct. The tuner's own status report
  confirms why: win rate 22% across 9 sessions, avg loss -1.46R vs avg win +0.60R, and both active
  setups (ORB -0.721R, momentum -0.975R) are in negative expectancy territory. The last three
  calendar days show a loss (-$64.44 on 2026-06-24), a day with one unfilled entry and $0 P&L
  (2026-06-25), and today's zero. The tuner is right to stay frozen. Doing nothing on a day when
  there is no qualifying setup is disciplined, not passive — a forced trade into a losing-expectancy
  pattern would have made things worse. The freeze will lift when the last-3-days window turns
  net-positive; that requires at minimum one clean winning round-trip. Until then: preserve capital,
  enforce the premarket plan requirement, and do not loosen entry standards to "find" a trade.
- 2026-06-24: No tuning. Tuner frozen (last 3 days net-negative — not optimizing during a losing
  streak). One trade today: AMZN momentum continuation, stopped at VWAP, -$64.44, -0.975R. This
  is the seventh consecutive session without a premarket day plan; that structural failure remains
  the dominant problem — without a plan, the tick loop is operating blind and will keep entering
  late or marginal setups. Today's entry at 12:35 PM was 2+ hours after the ORB that seeded the
  thesis; a morning plan with a time-of-day filter ("no new momentum entries after 11:00 AM ET on
  a thesis more than 90 minutes old") would have blocked this trade entirely. The one positive:
  stop discipline was exact at -0.975R, not worse. No parameter changes made; the tuner correctly
  declines, and there is nothing to tune until the premarket pipeline reliably writes a day plan.
- 2026-06-23: No tuning. Tuner eligible (6 days of history, drawdown 0.01%, not in a losing streak)
  but no rule fired — parameters unchanged. Zero trades today, sixth consecutive no-trade session.
  No journal and no docs/day_plan.md were written (sixth consecutive session without a plan). The
  reported Sharpe of -65.93 is an artifact of near-zero but slightly negative equity drift against
  effectively zero variance — not a meaningful signal; ignore it. The tuner correctly declines to
  act: without trades there is no new evidence about entry quality, stop placement, or sizing, and
  there is nothing to tune. The only lever that matters right now is fixing the premarket pipeline
  so it reliably writes a day plan. Until that happens, every evening's tuner run will reach the
  same conclusion.
- 2026-06-22: No tuning. Tuner eligible (5 days of history, drawdown 0.01%, not in a losing streak)
  but no rule fired — parameters unchanged. Zero trades today for the fifth time in six sessions.
  No docs/day_plan.md was written (fifth consecutive session without a plan). The premarket phase
  reset the day_stop correctly but did not produce a plan or any watchlist, so the tick loop had
  nothing to act on. ORB expectancy is -0.721R across 2 trades — negative but too few trades to
  justify a parameter change. The core problem is not the parameters: it is that premarket is not
  completing its job. Until the day plan is being written reliably, tuning ORB or sizing settings
  has no leverage — there is nothing to tune for. Fix the premarket pipeline first.
- 2026-06-19: No tuning. Tuner frozen (only 4 days of history; need 5). Zero trades today for the
  second time in five sessions. No day plan was written — fourth consecutive session without a
  docs/day_plan.md. The premarket phase appears to have run partially (day_stop reset correctly)
  but did not produce the plan document. A session with no plan and no trades is an invisible
  session: it cannot be reviewed, and the tick loop's behavior during the day cannot be verified.
  Rule added to Infrastructure: missing day plan at open = HALT condition, no ticks should run.
  Tuner needs one more day of history before it is eligible to act.
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
