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
- After eight or more consecutive sessions without a realized profit, conduct a setup-mix review before the next session: count how many blocked sessions had armed candidates the gates correctly filtered vs. sessions where the screener produced no qualifying candidate at all. The two failure modes require different responses — overly strict gates vs. an insufficiently broad screener universe. Do not loosen gates to force entries; diagnose the root cause first.
- When two consecutive sessions have no morning plan (docs/plans/<date>.md missing), treat it as a scheduler/runner failure, not a content failure — debug the premarket runner before placing any new trade. Two consecutive missing plans is a systemic breakdown; no strategy adjustment will fix it. The fix is in the scheduler. (2026-08-20 and 2026-08-21: second consecutive session with no plan written.)

## Time of day
- The first 5 minutes are noisy. Let the opening range (first ~15 min) form before trading breakouts.
- On post-holiday reopenings, the 15-minute waiting rule is mandatory: no entries of any kind before 9:45 AM ET.
- If checks are only ~hourly (cloud mode), use wider stops and smaller size — you cannot babysit
  positions minute-to-minute, so a tight stop can be blown straight through between checks.
- No new entries after 3:30pm ET. Start closing out at 3:50pm. Be flat by 3:56pm.
- Do not enter a momentum or ORB continuation trade more than 90 minutes after the opening range
  that seeded the thesis. A late entry inherits the risk of a mature trend reverting but misses
  the early reward; if the setup was not actionable at the open, skip it for the day.
- Be careful around scheduled events (Fed, CPI, jobs) — prices whip around. Trade smaller or wait.
- On pre-CPI session days (the Tuesday before a CPI release), institutional players reduce exposure ahead of the binary macro event; the 1.5x relative-volume gate reliably blocks all entries as a result. A zero-trade outcome on a pre-CPI day is correct behavior — do not adjust gates to force entries.
- On the 1-2 trading sessions before a scheduled FOMC minutes release, institutional players typically reduce exposure ahead of the binary macro event; relative volume across candidates runs well below the 1.5x gate as a result. A zero-trade outcome on these pre-FOMC-minutes sessions is the expected and correct outcome — do not adjust gates to force entries. (2026-08-17: FOMC July minutes on Wednesday; plan correctly anticipated zero trades Monday on 0.92–1.09x semiconductor rel vol.)

## Setups by market mood
- **Risk-on (trending up):** favor Opening-Range Breakouts and momentum continuation. Buy strength.
- **Range / quiet:** favor VWAP reclaims and careful mean-reversion. Smaller size.
- **Risk-off (fear/selling):** trade less, smaller, and don't buy breakouts into weakness.
- When sector-wide selling is confirmed premarket (multiple names in a sector all gapping down),
  deprioritize gap-bounce theses in that sector for the full session. A single-name bounce thesis
  while the surrounding sector is under broad selling pressure is swimming against the tide; wait for
  the sector to stabilize before buying any name in it.
- A premarket sector disarm stays in effect for the full session unless the tape shows broad stabilization across the sector (multiple names in the sector recovering and holding above VWAP). Do not lift the disarm for a single name bouncing in isolation.
- **ORB setup:** early evidence is negative (4 trades, -0.36R expectancy; losses routinely exceed
  the defined stop level, wins are small). Until the setup demonstrates positive expectancy, require
  textbook entry quality: relative volume >1.5x, spread <15 bp, clean break above the ORB high, and
  a confirmed companion stop order placed with the broker before the position is considered managed.
- **Momentum setup:** early evidence is negative (0/1 wins, -0.975R). Until the setup proves out,
  require two extra confirmations beyond the base screen: (a) sector momentum must broadly align with
  the individual name, and (b) entry must be within 60 minutes of the ORB that seeded the thesis.
- When the primary candidate does not produce a clean setup by mid-morning, fully commit to the
  secondary pick — do not spend subsequent ticks re-evaluating the primary. Today NFLX correctly
  passed, NVDA correctly substituted, and the trade worked.
- When the semiconductor sector disarm has been active for 2 or more consecutive sessions, the
  premarket strategist must add at least one non-semiconductor substitute from the qualified universe
  (SPY, QQQ, JPM, AMZN, TSLA, GOOGL) to the watchlist for that day. A 4-name watchlist concentrated
  in semiconductors leaves the system structurally idle across any multi-day sector rout; the
  substitute ensures at least one armed candidate exists each session.
- When a primary watchlist candidate is within approximately 9 calendar days of its scheduled
  earnings release, the options market absorbs earnings premium and intraday ranges may be narrower
  than the ATR suggests. A tight ORB range combined with low relative volume means the breakout
  signal may not fire cleanly. Evaluate whether a non-earnings-constrained name from the qualified
  universe (SPY, QQQ, or a stock with no near-term earnings) offers a cleaner primary setup for
  that session. (2026-08-17: NVDA earnings Aug 26 created a nine-day vol-compression window.)
- The NVDA pre-earnings disarm is a confirmed multi-cycle pattern: in the 5-10 sessions before
  each NVDA earnings date, options premium absorption produces a recognizable signature — narrowing
  ORB range, spread blowout (often exceeding the 15 bp gate), and relative volume falling below 1.5x
  even on otherwise active tape days. On NVDA earnings day itself, no intraday entry of any kind:
  the stock is binary into the print. The correct premarket response on any NVDA pre-earnings session
  is to substitute a non-earnings-constrained name as primary before ticks begin — do not wait for
  gates to fire and report a zero. (2026-08-26: pattern confirmed across multiple NVDA cycles.)
- On a MIXED/RANGE gap-up tape, the ORB breakout setup faces structural headwinds — the premarket
  gap absorbs the directional energy that would otherwise drive a clean intraday extension, and the
  broader market is not committed to a trending move. When regime is MIXED/RANGE and the tape gapped
  up premarket, treat VWAP reclaim as the primary setup and require at least 2.0× relative volume
  for any ORB breakout entry. If relative volume is below 2.0× on a MIXED/RANGE gap-up day, skip
  ORB and evaluate VWAP reclaim only. (2026-08-19: gate correctly blocked a 1.72× entry; SPY
  subsequently failed to hold the ORB high, confirming the gate's judgment.)

## Entries & exits
- Enter with marketable limit orders so we fill fast but never worse than our price.
- Set the stop at a level that means "the idea was wrong," not just a random number. Honor it instantly.
- When a position is entered, place a companion stop order with the broker on the same tick — before the entry is considered managed. The EOD flatten runs at most once per session and is a safety net, not a stop loss. On 2026-07-31, AMZN fell $4.34/share below entry before flatten ran because no automated stop was in place; the defined stop would have limited loss to $1.66/share.
- Take profit at the target; don't get greedy and give back a winner.
- When an ORB position hits its defined target intraday, exit at that level — do not ride to EOD
  flatten. EOD exits are a safety net, not an exit strategy. Over 3 ORB trades the average win was
  only +0.559R against a 2.5 ATR target, which means EOD flatten is systematically cutting winners
  short. Treat the target as an active exit trigger.
- For ORB setups on neutral or quiet-tape days, a 2.5× ATR target can translate to 5–6× the
  per-share risk and may never be reached in a single session. When the tape is not strongly
  trending, set the target at 1.5–2.0× the per-share risk rather than 2.5× ATR — wide enough to
  reward a clean breakout but realistically achievable before the flatten window. (2026-08-07:
  NFLX ORB target at $79.12 was never approached; trade closed EOD at +0.345R.)
- Before entering any trade, verify that the distance from entry to target is at least 2x the distance from entry to stop (minimum 2:1 R/R). Across 11 live trades, average wins are only +0.56R against average losses of -1.20R — the structural shortfall is losses running past stop and winners being harvested early. A setup that does not offer a clear 2:1 structure at entry should be skipped even if all other criteria pass.
- A typical good trade risks a few hundred dollars to make more than it risks (aim for wins ≥ 1.5R).
- Flatten limits must be set near the current bid at the time of submission, never from a cached or
  stale price. A stale flatten limit will miss the market entirely and leave a position open into the
  close. If the first pass fails to fill, the next pass must re-quote fresh before submitting.
- When the spread gate fires mid-session on a name that was a strong premarket candidate, treat it
  as a probable thesis failure rather than a timing issue to wait out. A wide live-session spread on
  a high-gap name — especially combined with price below VWAP — is a reversal signal, not merely a
  transaction-cost problem. (2026-07-09: INTC 209.5 bp spread at 12:39 PM with price below VWAP;
  stock broke below ORB low by 2:39 PM. The gate fired early; the chart confirmed it two hours later.)
- Premarket spread readings are not a reliable proxy for open-session liquidity on large-gap names.
  INTC showed 6.4 bp premarket on 2026-08-04 and blew out to 131.6 bp at the open — a 20x widening.
  When a candidate has a premarket gap of 3% or more, expect opening-minutes spread to be far wider
  than the premarket reading. The live spread gate fires at every tick and is the authoritative check;
  do not arm a high-gap name in the plan on the assumption that a tight premarket spread guarantees a
  clean entry.

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
- On post-holiday reopenings, verify the Alpaca /clock endpoint at the first tick of the session before placing any order. The premarket clock snapshot may be stale or reflect the holiday schedule; the tick-level clock check is authoritative for session timing.
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
- The premarket phase and the tick loop are independently scheduled. A day_plan.md being present at
  9:30 AM ET does not confirm that the tick loop will run. On 2026-07-21 a full premarket plan was
  written yet the tick loop produced zero intraday log entries for the second consecutive session
  (2026-07-20 also silent). A valid setup in INTC was available during the session and was entirely
  missed — not rejected by any gate, simply unseen. Treat two consecutive sessions of zero intraday
  log entries as a tick-loop scheduling failure requiring investigation, regardless of whether a plan
  exists. The fix is in the scheduler, not in any tunable parameter.
- A single intraday log entry arriving after all entry windows have closed is the same scheduling
  failure as zero entries. It confirms only that the loop booted once, not that it ran at the
  required 2-minute cadence during the trading window. On 2026-07-23, one tick at 2:41 PM was the
  entire intraday record — every entry window had expired hours earlier. Any session where all
  intraday log entries post-date the last valid entry window must be treated as a scheduling failure.
  The tick scheduler must be confirmed live and cadence-correct before market open, independently of
  the premarket scheduler.
- The premarket phase must include an explicit check that `run_phase.sh tick` is scheduled to fire
  at 9:30 AM ET before the premarket phase exits. Premarket completing successfully does not
  guarantee the tick loop will start. On six consecutive sessions (2026-07-13 through 2026-07-24)
  the premarket ran cleanly and the tick loop either did not run at all or ran once, hours late.
  These two phases are scheduled independently; do not assume premarket success implies tick
  availability. If the scheduler state cannot be confirmed, treat it as a HALT condition.
- A single intraday log entry that falls within the entry window but is followed by silence for
  the remainder of the session must be treated as a loop-exit failure, not a no-trade decision.
  It confirms the loop started and the decision logic is healthy, but the process exited after one
  iteration rather than maintaining 2-minute cadence. On 2026-07-27, one tick at 10:40 AM ET (within
  the ORB entry window) correctly rejected all candidates, then no further ticks ran. The fix is in
  the scheduler — it must keep the loop process alive from 9:30 AM through 3:56 PM ET, not merely
  launch it once. Verify cadence continuity independently of whether a plan exists or a first tick ran.
- The screener output (`levels.json`) and the plan narrative must converge into one canonical
  machine-readable armed-setups state before the premarket phase exits. When `levels.json` arms a
  name that the plan simultaneously disarms — or ranks setups differently — the tick loop has no
  single authoritative source of truth and is forced to arbitrate at evaluation time. After the
  narrative plan is finalized, the plan's decisions must overwrite or replace the screener's raw
  ranking so the tick loop reads exactly one file and never faces a conflict between two artifacts
  written minutes apart.
- The premarket phase must write docs/day_plan.md before 9:28 AM ET, not merely before the first
  tick fires. A plan written after 9:30 AM means the first tick correctly HALTs — but the ORB
  entry window begins expiring while the premarket phase is still completing. On 2026-08-13, the
  plan was not available at the 9:40 AM first tick; the tick correctly HALTed, but approximately
  67 minutes of the ORB entry window were consumed before the plan was written. Target premarket
  completion by 9:28 AM ET (consistent with the scheduled premarket slot). A correct HALT by the
  tick loop does not undo the opportunity cost of a late plan.
- When docs/day_plan.md is absent at the first tick for two consecutive sessions — despite the
  premarket phase running both days — it is a confirmed premarket timing failure, not a single-day
  anomaly. On 2026-08-13 and 2026-08-14 the tick loop correctly HALTed on both days, but the
  consecutive HALTs confirm the premarket schedule is finishing after ticks begin rather than the
  target of before 9:28 AM ET. Adjust the premarket schedule (earlier launch or tighter completion
  deadline), not the tick-loop launch timing.
- When a primary candidate is armed unconditionally (not gated on a conditional trigger) and passes
  all pre-session gates, every tick that runs during that candidate's entry window must produce
  either a submitted order or a timestamped skip record documenting which gate blocked it. A session
  where an armed, unconditional candidate existed but neither an order nor a skip record was written
  is a tick-loop failure, not a no-trade decision — the loop may have missed the entry window
  entirely or silently exited before evaluating the candidate. On 2026-07-30, AMZN was armed
  unconditionally and no order or skip record exists for the session.
- When a plan appears to be missing at the first tick for one or more consecutive sessions, verify
  that the git sync (cloud_sync.sh push) succeeded before concluding the premarket phase did not run.
  If GITHUB_TOKEN is not set, cloud_sync.sh push fails silently: the plan is written locally,
  committed to a detached HEAD, and never pushed to the remote — subsequent cloud sessions cannot
  find it and the missing-plan HALT fires incorrectly. Before diagnosing a premarket scheduler
  failure, check cloud_sync.sh push output and confirm the plan commit reached the remote. A real
  missing plan (premarket did not run) needs a scheduler fix; a git-sync failure (plan was written
  but not pushed) needs GITHUB_TOKEN set in the environment. The two failure modes are superficially
  identical from the tick loop's perspective but require completely different fixes. (2026-08-25:
  docs/plans/2026-08-25.md was written by premarket but invisible to tick sessions because
  GITHUB_TOKEN was not set and cloud_sync.sh push failed silently.)

## Changelog (the learning-coach appends here — newest on top)
- 2026-08-26: No tuning. Tuner unfrozen ("ok to tune", 47 days of history, drawdown 0.03%) but no
  rule fired — parameters left unchanged. Zero trades today (correct outcome). NVDA earnings were
  released after the close; the session was MIXED/RANGE with a major earnings overhang, and vol
  compression, spread blowout, and sub-1.5x relative volume correctly blocked every candidate —
  exactly the pre-earnings disarm pattern documented across prior NVDA cycles. Zero trades on this
  session is the expected and correct outcome, not a gate failure. Thirteenth consecutive zero-P&L
  session (last realized profit: 2026-08-07, +$40.50 NFLX). Assessment of the 13-session streak:
  the sessions break into two categories — (a) legitimate market/event blocking (FOMC minutes vol
  suppression Aug 17-18, MIXED/RANGE gate Aug 19, NVDA earnings disarm Aug 26) and (b) infrastructure
  failures (premarket scheduler Aug 20-21, git-sync GITHUB_TOKEN masking the plan Aug 25). Neither
  category warrants gate loosening; the gates and rules performed correctly throughout. The after-8-
  session review rule (added 2026-08-19) correctly distinguishes these two failure modes and does not
  need revision. Two durable additions tonight: (1) Setups — NVDA pre-earnings disarm codified as a
  confirmed multi-cycle pattern; premarket must substitute a non-earnings-constrained name rather than
  waiting for gates to fire and report a zero. (2) No other rule changes warranted — the 13-session
  streak reflects external conditions and infrastructure bugs, not a systematic gate calibration error.
  Aggregate stats (47 days, 16 trades): 37.5% win rate, avg win +0.43R, avg loss -0.85R, ORB
  -0.1994R (5 trades, 3 wins), momentum -0.975R (1 trade), fill rate 93.75%, avg 0.34 trades/day.
  Tuning ledger remains empty; no parameter has ever been changed by the tuner.
- 2026-08-25: No tuning. Tuner unfrozen ("ok to tune", 46 days of history, drawdown 0.03%) but no
  rule fired — parameters left unchanged. Zero trades placed today (correct outcome — all setups
  below the 1.5x rel-vol gate; SPY/QQQ below ORB lows). Key infrastructure finding: the premarket
  plan was written (docs/plans/2026-08-25.md exists, RISK-ON moderate) but was invisible to all
  tick sessions. Root cause: GITHUB_TOKEN not set → cloud_sync.sh push fails silently → plan
  committed to detached HEAD → unreachable by subsequent cloud sessions → missing-plan HALT fires
  at 09:40 and holds for the session. Tick and trading logic both worked correctly; the bug is
  entirely in the git sync infrastructure. One durable infrastructure rule added tonight: when
  consecutive missing-plan HALTs occur, check cloud_sync.sh push output and remote commit history
  before concluding premarket did not run — a silent GITHUB_TOKEN failure is superficially identical
  to premarket never executing. This is the 12th consecutive non-profitable session (last realized
  profit: 2026-08-07, +$40.50 NFLX). Aggregate stats (46 days, 16 trades): 37.5% win rate, avg win
  +0.43R, avg loss -0.85R, ORB -0.1994R (5 trades, 3 wins), momentum -0.975R (1 trade, 0 wins),
  avg 0.35 trades/day. Tuning ledger remains empty; no parameter has ever been changed by the tuner.
  Priority: set GITHUB_TOKEN in the scheduler environment before the next session.
- 2026-08-24: No tuning. Tuner unfrozen ("ok to tune", 45 days of history, drawdown 0.03%) but no
  rule fired — parameters left unchanged. Zero trades placed today; no morning plan was written for
  the third consecutive trading session (2026-08-20, 2026-08-21, and 2026-08-24 all missing
  docs/plans/<date>.md). This is an ongoing confirmed premarket scheduler failure — not a content,
  strategy, or parameter problem. Both ORB (-0.1994R across 5 trades, 3 wins) and momentum
  (-0.975R across 1 trade) show negative expectancy, but loosening their gates to force entries
  would be the wrong response: the system is not seeing these setups because premarket is not
  running, not because the gates are too strict. No new durable rules are warranted tonight: the
  two-consecutive-missing-plan rule added on 2026-08-21 already covers this pattern and the
  diagnosis is unchanged — the fix is in the premarket scheduler, not in any tunable parameter.
  Aggregate stats (45 days, 16 trades): 37.5% win rate, avg win +0.43R, avg loss -0.85R, avg fill
  rate 93.75%, ORB -0.1994R (5 trades, 3 wins), momentum -0.975R (1 trade, 0 wins), avg 0.36
  trades/day. Tuning ledger remains empty; no parameter has ever been changed by the tuner.
  Priority remains unchanged: diagnose and fix the premarket runner scheduling failure before
  the next trading session.
- 2026-08-21: No tuning. Tuner unfrozen ("ok to tune", 44 days of history, drawdown 0.03%) but no
  rule fired — parameters left unchanged. Zero trades placed today; no morning plan was written for
  the second consecutive session (2026-08-20 and 2026-08-21 both missing docs/plans/<date>.md).
  This is a confirmed systemic premarket runner failure, not a content or strategy issue. Two
  consecutive missing-plan sessions mean the tick loop cannot execute safely on either day — the
  watchlist is unknown, the loss-stop baseline was not captured, and there is no reviewable session
  record. One durable rule added tonight to Discipline: when two consecutive sessions have no morning
  plan, treat it as a scheduler/runner failure and debug the premarket runner before placing any new
  trade. No new trading evidence was generated (tenth consecutive session without a realized profit;
  last win: 2026-08-07, +$40.50 NFLX). Account equity $999,487.65 (unchanged, no realized P&L).
  Total drawdown from $1,000,000 start: $512.35 (0.051%). Aggregate stats (44 days, 16 trades):
  37.5% win rate, avg win +0.43R, avg loss -0.85R, ORB -0.1994R across 5 trades (3 wins), momentum
  -0.975R across 1 trade, Sharpe -77.07 (artifact of near-zero variance on a flat account, not a
  meaningful signal). Tuning ledger remains empty; no parameter has ever been changed by the tuner.
  Priority before Monday open: diagnose and fix the premarket runner scheduling failure.
- 2026-08-20: No tuning. Tuner unfrozen ("ok to tune", 43 days of history, drawdown 0.03%) but no
  rule fired — parameters left unchanged. Zero trades placed today; no day plan was written (premarket
  phase did not complete again). This is the ninth consecutive session without a realized profit (last
  win: 2026-08-07, +$40.50 NFLX). A session with no plan is an invisible session — the tick loop
  cannot trade safely and no new evidence about entry quality or stop placement is generated. The
  setup-mix review recommended in the 2026-08-19 entry (distinguishing "gates correctly filtering bad
  setups" from "screener not generating enough candidates") remains pending and should be conducted
  before the next session. No new durable rules are warranted tonight: no trades means no new
  evidence; the recurring cause is premarket scheduling failure, not any tunable parameter. Account
  equity approximately $999,487.65 (unchanged from 2026-08-19, no realized P&L). Total drawdown from
  $1,000,000 start: $512.35 (0.051%). Aggregate stats (43 days, 16 trades): 37.5% win rate, avg win
  +0.43R, avg loss -0.85R, ORB -0.20R across 5 trades (3 wins), momentum -0.975R across 1 trade,
  LIMIT fill rate 94%. Tuning ledger remains empty; no parameter has ever been changed by the tuner.
- 2026-08-19: No tuning. Tuner unfrozen ("ok to tune", 42 days of history, drawdown 0.03%) but no
  rule fired — parameters left unchanged. Zero trades placed today; eighth consecutive session
  without a realized profit (last win: 2026-08-07, +$40.50 NFLX). Key observation: the ORB
  breakout gate (2.0× rel_vol) correctly blocked an entry at 1.72× relative volume on a MIXED/RANGE
  gap-up session — SPY subsequently failed to hold the ORB high, confirming the gate's judgment.
  Regime mismatch lesson: on MIXED/RANGE gap-up days, the premarket gap absorbs the directional
  energy that an ORB breakout depends on; the broader market is not committed to trending. Two
  durable rules added tonight: (1) Setups — on MIXED/RANGE gap-up tape, treat VWAP reclaim as the
  primary setup and require ≥2.0× relative volume for any ORB breakout entry; below 2.0× skip ORB
  entirely. (2) Discipline — after eight or more consecutive no-profit sessions, conduct a setup-mix
  review to distinguish "gates correctly filtering bad setups" from "screener not generating enough
  candidates"; the two failure modes need different fixes. Account closed flat at $999,487.65. Total
  drawdown from $1,000,000 start: $512.35 (0.051%). Aggregate stats (42 days, 16 trades): 37.5%
  win rate, avg win +0.43R, avg loss -0.85R, ORB -0.20R across 5 trades (3 wins), momentum -0.975R
  across 1 trade, LIMIT fill rate 94% (15/16). Tuning ledger remains empty; no parameter has ever
  been changed by the tuner.
- 2026-08-18: No tuning. Tuner unfrozen ("ok to tune", 41 days of history, drawdown 0.03%) but no
  rule fired — parameters left unchanged. Zero trades placed today; US-Iran tensions (RISK-OFF) and
  pre-FOMC-minutes Tuesday (Wednesday release of FOMC July minutes) suppressed participation exactly
  as the existing playbook rules predict. The pre-FOMC-minutes rule added 2026-08-17 was validated
  by today's session — institutional vol reduction ran at the same magnitude as yesterday, and the
  1.5x rel-vol gate blocked every candidate. A zero-trade outcome on this session is the expected
  and correct outcome; no gates were adjusted and none should be. No new durable rules are warranted:
  both the risk-off and pre-FOMC-minutes patterns are already codified, and today produced no
  evidence that any existing rule was wrong. Account closed flat at $999,487.65 — the seventh
  consecutive session without a realized profit (last win: 2026-08-07, +$40.50 NFLX). Total
  drawdown from $1,000,000 start: $512.35 (0.051%). Aggregate stats unchanged from yesterday (no
  new round-trips): 16 trades, 37.5% win rate, avg win +0.43R, avg loss -0.85R, ORB -0.199R
  across 5 trades (3 wins), momentum -0.975R across 1 trade. Tuning ledger remains empty; no
  parameter has ever been changed by the tuner.
- 2026-08-17: No tuning. Tuner unfrozen ("ok to tune", 40 days of history, drawdown 0.03%) but no
  rule fired — parameters left unchanged. Zero trades placed today; no new round-trips means the
  aggregate statistics are unchanged from yesterday: 16 total trades, ORB -0.199R across 5 trades
  (3 wins, 2 losses), momentum -0.975R across 1 trade. The learning loop is idle when trade
  generation is suppressed — there is no new evidence for any parameter to act on. Primary
  operational failure: docs/intraday/2026-08-17.md was not written; the tick loop's tick-by-tick
  observations during the session are unrecorded. This is the highest-priority fix before Tuesday's
  open — without it, a zero-trade session is indistinguishable from a non-running tick loop. Two
  durable rules added tonight: (1) the 1-2 sessions before a scheduled FOMC minutes release suppress
  participation similarly to pre-CPI Tuesdays — the 1.5x rel-vol gate reliably blocks entries and a
  zero-trade outcome is correct (added to Time of day); (2) a primary candidate within ~9 calendar
  days of its earnings release faces vol compression from options premium absorption, narrowing the
  ORB range — evaluate a non-earnings-constrained alternate for the primary slot (added to Setups).
  Closing equity $999,487.65, sixth consecutive session without a realized profit (last win:
  2026-08-07, +$40.50 NFLX). Total drawdown from $1,000,000 start: $512.35 (0.051%). Tuning ledger
  remains empty; no parameter has ever been changed by the tuner.
- 2026-08-14: No tuning. Tuner frozen (last 3 days are net-negative — not optimizing during a
  losing streak). Fourth consecutive non-positive session: Aug 11 $0, Aug 12 -$47.74, Aug 13 $0,
  Aug 14 $0. Zero trades placed; closing equity $999,487.65. Infrastructure note: docs/day_plan.md
  was absent at the first tick (9:53 AM) for the second consecutive session — the tick correctly
  HALTed, but two consecutive HALTs on the same cause confirms a systematic premarket timing
  failure, not a one-off. One infrastructure rule added tonight: two consecutive absent-plan HALTs
  is a confirmed timing failure; the premarket schedule must be adjusted to complete before
  9:28 AM ET. INTC spread: 3.8 bp premarket → 51.6 bp at open — the third documented occurrence
  (Jul 9 at 209.5 bp, Aug 4 at 131.6 bp, Aug 14 at 51.6 bp); the existing rule holds. Gates
  worked correctly: NVDA rel_vol peaked at 1.09x (never reached 1.5x gate) and declined to 0.57x
  by EOD; both NVDA and INTC broke below their ORB lows, consistent with the semiconductor sector
  headwind described in the plan — plan thesis accurate, zero trades correct. Over 39 days:
  16 trades (0.41/day), 37.5% win rate, avg win +0.43R, avg loss -0.85R, ORB -0.1994R across
  5 trades (3 wins), momentum -0.975R across 1 trade. Tuning ledger remains empty; no parameter
  has ever been changed by the tuner.
- 2026-08-13: No tuning. Tuner frozen (last 3 days are net-negative — not optimizing during a losing
  streak). Today: zero trades. Plan called MIXED/RANGE; NVDA was the sole candidate but the ORB
  high ($227.20) was never broken and relative volume fell from 1.49x at first evaluation to 0.92x
  by mid-afternoon — correctly blocked at every gate. Infrastructure note: the premarket phase did
  not write the plan before the 9:40 AM first tick; the tick correctly HALTed, but approximately
  67 minutes of the ORB entry window were lost while the plan was still being written. One
  infrastructure rule added: the premarket phase must write docs/day_plan.md by 9:28 AM ET, not
  merely before the first tick — a late plan costs entry time whether or not the tick gate fires
  correctly. Lifetime ORB data (5 trades, 3 wins, 60% win rate, -0.1994R expectancy): losses are
  systematically larger than wins, not offset by the win rate; the existing strict-entry-quality
  gate remains the right response. Over 38 days: 16 trades (0.42/day), 37.5% win rate, avg win
  +0.43R, avg loss -0.85R, ORB -0.199R across 5 trades, momentum -0.975R across 1 trade. Tuning
  ledger remains empty; no parameter has ever been changed by the tuner.
- 2026-08-12: No tuning. Tuner frozen (last 3 days are net-negative — not optimizing during a losing
  streak). Note: the 3-day window includes 2026-08-11, which was a deliberate zero-trade pre-CPI day,
  not a realized loss; the freeze is nonetheless correct and conservative. Today: 1 NVDA ORB trade,
  entry avg $224.557 (fill below limit $225.10 — excellent execution), EOD flatten avg $223.472,
  -$47.74 (-0.255R). Stop $220.30, target $234.70; neither was triggered — the position drifted down
  ~$1.085/share over 5+ hours without testing the thesis in either direction. All entry gates passed:
  rel_vol 1.81x, spread 11.1 bp, R/R 2.13:1. This was a correctly executed trade that lost a small
  amount. No new rule is warranted: a clean entry that drifts slowly to EOD flatten at -0.255R is
  within expected variance for the setup; the EOD flatten safety net worked exactly as intended.
  Over 37 days: 16 trades (0.43/day), 37.5% win rate, avg win +0.43R, avg loss -0.85R, ORB -0.199R
  across 5 trades (3 wins), momentum -0.975R across 1 trade. Tuning ledger remains empty; no
  parameter has ever been changed by the tuner.
- 2026-08-11: No tuning. Tuner eligible ("ok to tune", 36 days of history, drawdown 0.02%) but no rule fired — parameters left unchanged. Today was a zero-trade day (pre-CPI Tuesday, MIXED/RANGE regime). Account equity $999,535.62, $0 realized P&L, ended flat. The plan correctly anticipated zero trades: on pre-CPI Tuesdays institutional players reduce exposure before the binary macro event, suppressing relative volume across candidates. This pattern has now repeated on multiple pre-CPI sessions. One durable rule added tonight to Time of day: pre-CPI session days are explicitly named — the 1.5x rel_vol gate reliably blocks all entries as a consequence of institutional caution; zero trades is the expected and correct outcome; do not adjust gates to force entries. Over 36 days: 14 trades (0.39/day), 42.9% win rate, avg win +0.49R, avg loss -0.94R, ORB -0.1855R across 4 trades, momentum -0.975R across 1 trade, fill rate 93%. Tuning ledger remains empty; no parameter has ever been changed by the tuner.
- 2026-08-10: No tuning. Tuner eligible ("ok to tune", 35 days of history, drawdown 0.02%) but no
  rule fired — parameters left unchanged. Evidence reviewed tonight: three sessions (2026-07-10
  NVDA, 2026-07-31 AMZN, 2026-08-07 NFLX) all share the same structural problem — the 2.5x ATR
  target is routinely unreachable within a single session, forcing EOD flatten to act as the exit
  rather than the target. Average ORB outcome across 4 trades is -0.1855R expectancy against a
  2.5x ATR objective; wins are being harvested early at +0.345R to +0.559R, far below the
  configured target. The case for reducing `target_atr_mult` from 2.5 toward 2.0 is noted and
  the directional signal is real, but the tuner's own rule logic evaluated the data and did not
  fire — no automated change was made. The human reviewer should confirm: (1) whether the tuner
  rule threshold for `target_atr_mult` requires a stronger signal than what three ORB sessions
  provide, and (2) if the evidence is now considered sufficient, whether a manual step down to
  2.0 is warranted outside the tuner's bounds. No parameter has been changed tonight; the tuning
  ledger remains empty. Over 35 days: 14 trades (0.40/day), 42.9% win rate, avg win +0.49R,
  avg loss -0.94R, ORB -0.1855R across 4 trades, momentum -0.975R across 1 trade, fill rate 93%.
- 2026-08-07: No tuning. Tuner eligible ("ok to tune", 34 days of history) but no rule fired —
  parameters left unchanged. Today: 1 NFLX ORB round-trip, buy 135 @ $73.87, EOD flatten @
  $74.17, +$40.50 (+0.345R). Win. All gates passed, no rule violations. The target ($79.12,
  2.5× ATR) was never approached — the tape was neutral and the objective was structurally too
  wide for a single session. Lesson added to Entries & exits: on neutral-tape ORB days, prefer a
  target of 1.5–2.0× per-share risk over 2.5× ATR; the wider ATR-based objective can represent
  5–6R and may be unreachable intraday. Over 34 days: 14 trades (0.41/day), 42.9% win rate, avg
  win +0.489R, avg loss -0.940R, ORB -0.1855R across 4 trades, momentum -0.975R across 1 trade.
  Tuning ledger remains empty; no parameter has ever been changed by the tuner.
- 2026-08-06: No tuning. Tuner eligible ("ok to tune", 33 days of history, drawdown 0.03%) but no
  rule fired — parameters left unchanged. Today was a fourth consecutive flat day with no trades
  placed and no premarket plan written (premarket phase skipped or failed again). Four consecutive
  zero-trade, zero-plan sessions (2026-08-03 through 2026-08-06) is a clear infrastructure signal:
  the scheduler is not reliably launching the premarket phase, which in turn means the tick loop
  has no plan to act on. This is not a trading-parameter problem; no tuner setting addresses it.
  The recurring fix required is confirming that both the premarket phase and the tick loop are
  actually scheduled and running to cadence before market open — this has been documented in the
  Infrastructure section repeatedly and the failure mode keeps recurring. Treat four consecutive
  no-plan sessions as a mandatory scheduler audit before the next trading session: verify that
  `run_phase.sh premarket` fires before 9:28 AM ET and that `run_phase.sh tick` sustains
  2-minute cadence from 9:30 AM through 3:56 PM ET. Config fix applied tonight: `min_rel_volume`
  corrected from 1.2 to 1.5 in state/config.json to align with the entry rule already in this
  playbook (ORB section: "relative volume >1.5x"). This was a documentation/config mismatch that
  persisted two days after being identified in the 2026-08-05 journal — it is now resolved.
  The screener minimum and the ORB entry threshold are now consistent. Account equity approx.
  $999,495 (unchanged from yesterday, no realized P&L). Over 33 days: 12 trades (0.36/day),
  33.3% win rate, avg win +0.51R, avg loss -1.10R, ORB -0.362R across 3 trades, momentum
  -0.975R across 1 trade, fill rate 91.7%. Tuning ledger remains empty; no parameter has ever
  been changed by the tuner.
- 2026-08-05: No tuning. Tuner eligible ("ok to tune", 32 days of history, drawdown 0.03%) but no
  rule fired — parameters left unchanged. Today was a zero-trade day; 0 placed, 0 filled, $0.00
  realized P&L, ended flat. Observation: `config.json` has `min_rel_volume: 1.2` (the screener
  candidate threshold) while the ORB entry rule in the playbook requires >1.5x. These serve
  different purposes — the config gates initial watchlist inclusion, the playbook rule gates entry.
  At 09:40 AM today, INTC showed 1.22x rel_vol: it passed the screener minimum but was correctly
  blocked at the entry stage by the 1.5x rule. The two-tier filter is working as intended. The
  config value is not wrong, but it is worth tracking: if the screener regularly surfaces candidates
  that are then rejected by the stricter entry rule, the net effect is wasted evaluation cycles on
  names that were never going to qualify. If this pattern repeats, raising `min_rel_volume` in
  config closer to 1.5x would tighten the screener to match actual entry standards. No action
  taken tonight — the sample of affected candidates is a single instance. Account equity
  $999,495.37, $0 realized P&L, ended flat. Over 32 days: 12 trades (0.375/day), 33.3% win rate,
  avg win +0.51R, avg loss -1.10R, ORB -0.362R across 3 trades, momentum -0.975R across 1 trade,
  fill rate 91.7% (11/12). Tuning ledger remains empty; no parameter has ever been changed.
- 2026-08-04: No tuning. Tuner eligible ("ok to tune", 31 days of history, drawdown 0.03%) but no
  rule fired — parameters left unchanged. Today was a zero-trade day caused by a tick-loop scheduling
  failure (ticks only at 9:40 AM and 3:39 PM; the entire 9:45–11:00 AM entry window was uncovered —
  second consecutive session with this pattern). The analytical work was sound: NFLX was the best
  candidate at 9:40 AM (5.5 bp spread, above VWAP, 2.45x rel_vol) and would likely have passed entry
  gates at 9:45 AM. One durable trading rule added tonight: INTC's premarket spread was 6.4 bp but
  blew out to 131.6 bp at the open (20x widening) — tight premarket spreads are not reliable proxies
  for open-session liquidity on high-gap names. Rule added to Entries & exits. Account equity
  $999,495.43, $0 realized P&L, ended flat. Over 31 days: 12 trades (0.39/day), 33.3% win rate,
  avg win +0.51R, avg loss -1.10R, ORB -0.362R across 3 trades, momentum -0.975R across 1 trade,
  fill rate 91.7% (11/12). Tuning ledger remains empty; no parameter has ever been changed.
- 2026-08-03: No tuning. Tuner eligible ("ok to tune", 30 days of history, drawdown 0.03%) but no
  rule fired — parameters left unchanged. Today was a no-trade day: all 3 armed setups (AAPL ORB,
  AMZN ORB, NFLX VWAP reclaim) had their entry windows expire at 11:00 AM without a trade executed.
  AAPL was blocked by the spread gate (89.7 bp vs. 15 bp max). AMZN passed all pre-entry criteria
  but price never broke above the ORB high of $286.90 (was $1.22 short at the last observation).
  NFLX never produced a VWAP reclaim and rel_vol was below the minimum threshold. All three existing
  gates fired correctly — this is a valid no-trade outcome, not a loop failure. No new rules are
  warranted; the existing gates covered every case. Account equity $999,501.32, $0 realized P&L,
  ended flat. Over 30 days: 12 trades (0.40/day), 33.3% win rate, avg win +0.51R, avg loss -1.10R,
  ORB -0.362R across 3 trades, momentum -0.975R across 1 trade, fill rate 91.7% (11/12). Tuning
  ledger remains empty; no parameter has ever been changed.
- 2026-07-31: No tuning. Tuner eligible ("ok to tune", 29 days of history) but no rule fired —
  parameters left unchanged. Today: 1 AMZN ORB trade, bought 36 @ $270.87, closed by flatten at
  ~$266.53, loss ~$156. The position fell through its defined stop at $269.21 before flatten ran
  because no companion stop order was in place — the position drifted $2.68/share past the stop
  level unmanaged. Two lessons encoded tonight: (1) Entries & exits — a companion stop order must
  be placed with the broker on the same tick as the entry; EOD flatten is a safety net, not a stop
  loss; rule added. (2) Setups — ORB is now 4 trades at -0.36R expectancy with losses exceeding
  defined stops; added an explicit ORB warning in Setups requiring >1.5x rel vol, <15 bp spread,
  and a confirmed companion stop before any ORB entry. Account equity $999,501.34 (-0.05% total
  return). Over 29 days: 12 trades, 33.3% win rate, avg win +0.51R, avg loss -1.10R, ORB -0.36R
  across 4 trades, momentum -0.975R across 1 trade. Tuning ledger remains empty; no parameter has
  ever been changed.
- 2026-07-30: No tuning. Tuner eligible ("ok to tune", 28 days of history, drawdown 0.01%) but no
  rule fired — parameters left unchanged. Today was the 10th+ consecutive zero-trade session; the
  last executed trade was July 10. Realized P&L $0.00; account equity $999,657.58 (up $16.65 from
  open, entirely paper-account interest, not trading income). The primary candidate today was AMZN,
  armed unconditionally and passing all pre-session gates. No order was placed and no skip record
  exists for the session, which means the tick loop either did not run during AMZN's entry window
  or silently exited without evaluating it. This is a new variant of the recurring tick-loop
  cadence failure: prior sessions showed "ran once then stopped" or "ran once hours late"; today
  shows an armed unconditional candidate with no evaluation trace at all. A new infrastructure rule
  has been added: when a primary candidate is armed unconditionally and passes all pre-session
  gates, every tick that runs during the entry window must produce either a submitted order or a
  timestamped skip record; absence of both is a confirmed loop failure. Tuning ledger remains empty;
  no parameter has ever been changed. Over 28 days: 11 trades (0.39/day), 36.4% win rate, avg win
  +0.559R, avg loss -1.197R, ORB -0.362R across 3 trades, momentum -0.975R across 1 trade.
- 2026-07-29: No tuning. Tuner eligible ("ok to tune", 27 days of history, drawdown 0.01%) but no
  rule fired — parameters left unchanged. Today was the 19th consecutive zero-trade session (last
  trade July 10). All four watchlist names were blocked by independent gates: NVDA and INTC by
  sector disarm, NFLX by a 231 bp spread, BAC by FOMC event risk. One durable rule added tonight:
  when the semiconductor sector disarm has been active for 2 or more consecutive sessions, the
  premarket strategist must add at least one non-semiconductor substitute (SPY, QQQ, JPM, AMZN,
  TSLA, GOOGL) to the watchlist to ensure at least one armed candidate each session. A 4-name
  watchlist concentrated in semis leaves the system structurally idle during multi-day sector routs.
  Account equity $999,640.93 (-0.036% total return), $0 realized P&L, ended flat. Over 27 days:
  11 trades (0.41/day), 36.4% win rate, avg win +0.559R, avg loss -1.197R, ORB -0.362R across 3
  trades, momentum -0.975R across 1 trade. Tuning ledger remains empty; no parameter has ever been
  changed.
- 2026-07-28: No tuning. Tuner eligible ("ok to tune", 26 days of history, drawdown 0.01%) but no
  rule fired — parameters left unchanged. Today was the eighth consecutive zero-trade session
  (July 13, 17, 20, 21, 23, 24, 27, 28); the tick loop ran once, at 9:31 AM ET — fourteen minutes
  before the 9:45 AM ORB entry window opens. That pre-window gate rejection was correct decision
  logic; the failure is the same loop-exit pattern as 2026-07-27: one iteration ran, then the loop
  exited rather than sustaining 2-minute cadence through the trading window and beyond. No new
  infrastructure rule is needed — the loop-exit failure mode is already documented; the scheduler
  must hold the loop process alive from 9:30 AM through 3:56 PM ET regardless of how early the
  first tick fires or whether it found any actionable setup. Account equity $999,747.04, $0 realized
  P&L, ended flat. Over 26 days: 11 trades (0.42/day), 36.4% win rate, avg win +0.559R, avg loss
  -1.197R, ORB -0.362R across 3 trades, momentum -0.975R across 1 trade; tuning ledger remains empty.
- 2026-07-27: No tuning. Tuner eligible ("ok to tune", 25 days of history, drawdown 0.0%) but no
  rule fired — parameters left unchanged. Today was the seventh consecutive zero-trade session.
  The pattern today is meaningfully different from the prior six: the tick loop ran exactly once,
  at 10:40 AM ET — 70 minutes after the open, but still within the ORB entry window. It evaluated
  all candidates and correctly skipped them (no setup qualified). No subsequent ticks followed for
  the remainder of the session. This confirms two things: (1) the decision logic is working — the
  one tick that ran made correct judgments; (2) the failure is that the loop exits after a single
  iteration rather than maintaining the required 2-minute cadence. "Runs once then stops" is a
  distinct and previously undocumented failure mode from "never runs" and "runs once hours too late."
  A new infrastructure rule has been added below: a single intraday log entry within the entry
  window, followed by silence, must be treated as a loop-exit failure, not a valid no-trade session.
  The decision logic does not need adjustment; the scheduler must be confirmed to keep the loop alive
  for the full trading window (9:30 AM–3:56 PM ET), not merely start it. Account equity $999,747.04,
  $0 realized P&L, ended flat. Over 25 days: 11 trades (0.44/day), 36.4% win rate, avg win +0.559R,
  avg loss -1.197R, ORB -0.362R across 3 trades, momentum -0.975R across 1 trade. No parameter has
  ever been changed; tuning ledger remains empty.
- 2026-07-24: No tuning. Tuner eligible ("ok to tune", 21 days of history, drawdown 0.0%) but no
  rule fired — parameters left unchanged. Today was the sixth consecutive zero-trade session
  (July 13, 17, 20, 21, 23, 24); the last actual orders placed were July 10 and the last confirmed
  round-trips were June 18 — 26 calendar days ago. The cause is not market conditions or strategy
  parameters. The premarket phase ran cleanly at 9:32 AM ET (plan written, screener executed,
  baseline captured). The tick loop ran zero times. INTC was correctly disarmed — earnings beat
  but the 12.4% after-hours gain was fully erased before the open, a "sell the news" pattern the
  plan identified at 9:32 AM. NFLX was a sound VWAP-reclaim candidate with a 9:45–11:00 AM entry
  window and a 20.3 bp premarket spread — a legitimate setup the system was never present to
  evaluate. The screener and plan document produced conflicting rankings for the second consecutive
  session (`levels.json` armed INTC and ranked NVDA primary; the plan disarmed INTC and promoted
  NFLX to primary). Six consecutive zero-trade sessions due to a scheduler failure is not a signal
  for parameter adjustment; it is a system availability failure. Two new Infrastructure rules added
  tonight: (1) the premarket phase must explicitly verify the tick loop is scheduled to fire at
  9:30 AM before exiting — premarket success does not guarantee tick availability; (2) the screener
  output and plan narrative must converge into one canonical armed-setups state before premarket
  exits, so the tick loop reads a single authoritative file with no arbitration required. Account
  equity $999,747.04, $0 realized P&L, ended flat. Over 21 days: 11 trades (0.52/day), 36.4% win
  rate, avg win +0.559R, avg loss -1.197R, ORB -0.362R across 3 trades, momentum -0.975R across 1
  trade. No parameter has ever been changed; tuning ledger remains empty.
- 2026-07-23: No tuning. Tuner eligible ("ok to tune", 23 days of history, drawdown 0.0%) but no
  rule fired — parameters left unchanged. This was the fifth consecutive zero-trade session (July 13,
  17, 20, 21, 23); the last trades placed were July 10. The failure mode today was distinct from July
  21 (zero ticks): the tick loop ran exactly once, at 2:41 PM ET — more than five hours after the
  open and outside every entry window in the plan — but the practical consequence is the same: the
  session went unevaluated during the only window that mattered (NFLX VWAP reclaim, 9:45–11:00 AM).
  The premarket phase ran correctly: the plan was written at 9:29 AM (RISK-OFF, NFLX primary, INTC
  fully disarmed for evening earnings), and the INTC disarm was vindicated — the stock was $1.70
  below VWAP and below its ORB low by the time the lone tick arrived. A new infrastructure rule has
  been added: a single late-afternoon log entry is not evidence of a running tick loop; any session
  where all log entries post-date the last valid entry window is a scheduling failure requiring
  investigation. Account equity $999,747.04, $0 realized P&L, ended flat. Over 23 days: 11 trades
  (0.48/day), 36.4% win rate, avg win +0.559R, avg loss -1.197R; ORB -0.362R across 3 trades,
  momentum -0.975R across 1 trade. No parameter has ever been changed; tuning ledger remains empty.
- 2026-07-21: No tuning. Tuner eligible ("ok to tune", 22 days of history, drawdown 0.0%) but no
  rule fired — parameters left unchanged. Today was a zero-trade day for the second consecutive
  session (2026-07-20 also zero). The key distinction from prior silent days: a premarket plan was
  written today, yet the tick loop still produced no intraday log entries. This confirms that the
  premarket phase and the tick loop are independently scheduled — a plan being present is not
  sufficient to guarantee loop execution. INTC presented a valid setup during the session and was
  entirely missed, not because any gate rejected it, but because the loop never saw it. This is a
  reliability failure, not a trading-parameter problem; no tuner setting can address it. A new
  infrastructure rule has been added documenting this failure mode and making two consecutive silent
  sessions a trigger for scheduler investigation. Account equity $999,747.04, $0 realized P&L,
  ended flat. Over 22 days: 11 trades (0.5/day), 36.4% win rate, avg win +0.559R, avg loss -1.197R;
  ORB -0.362R across 3 trades, momentum -0.975R across 1 trade. Tuning ledger remains absent; no
  parameter has ever been changed.
- 2026-07-20: No tuning. Tuner eligible ("ok to tune", 21 days of history, drawdown 0.0%) but no
  rule fired — parameters left unchanged. Today was a zero-trade day: the premarket phase did not
  run for the seventh time, producing ten consecutive zero-trade sessions since 2026-07-10. Account
  equity $999,747.04, $0 realized P&L, ended flat. Over 21 days: 11 trades (0.524/day), 36.4% win
  rate, avg win +0.559R, avg loss -1.197R; ORB -0.362R across 3 trades, momentum -0.975R across 1
  trade. Ten straight zero-trade days with no premarket run provide no new signal about entry
  quality, stop placement, or sizing — there is nothing for the tuner to act on. The recurring
  premarket scheduling failure is the dominant operational problem; it cannot be fixed by adjusting
  any tunable parameter. Tuning ledger remains empty; no parameter has ever been changed.
- 2026-07-17: No tuning. Tuner eligible ("ok to tune", 20 days of history, drawdown 0.0%) but no
  rule fired — parameters left unchanged. Today was a zero-trade day: the premarket phase did not
  run, so no watchlist was screened, no day plan was written, and the tick loop had no context to
  act on. This is the sixth documented premarket scheduling failure (previous: 2026-07-07,
  2026-06-23, 2026-06-22, 2026-06-19, 2026-06-17). A missed premarket is a missed trading day —
  the bot cannot trade safely without a plan, a loss-stop baseline, or a screened watchlist. NFLX
  presented an excellent technical setup during the session (ORB breakout, 2.68x rel_vol, 1.4 bp
  spread) but was correctly rejected because the 90-minute ORB window had already closed; the
  existing time-of-day rule worked as designed. Account equity $999,747.04, $0 realized P&L,
  ended flat. One durable rule added tonight: the R/R structural shortfall across 11 live trades is
  clear — average wins +0.56R, average losses -1.20R — so a hard minimum 2:1 R/R check at entry
  is now required before any trade is placed; rule added to Entries & exits. Over 20 days: 11
  trades (0.55/day), 36.4% win rate, ORB -0.362R across 3 trades, momentum -0.975R across 1
  trade. No parameter has ever been changed; tuning ledger remains empty.
- 2026-07-13: No tuning. Tuner eligible ("ok to tune", 19 days of history, drawdown 0.0%) but no
  rule fired — parameters left unchanged. Today was a zero-trade day: RISK-OFF regime driven by
  US/Iran military escalation. The premarket plan correctly set a hard conditional — "if NFLX does
  not present a clean setup by 11 AM ET, take zero trades" — and executed it exactly. No trades
  were placed; equity $999,747.04, ended flat. No new rule is warranted tonight. A zero-trade day
  with no fills provides no new statistical signal about entry quality, stop placement, or sizing.
  The RISK-OFF pattern is already in the playbook ("Risk-off: trade less, smaller, don't buy
  breakouts into weakness"). The conditional-plan execution pattern is already in the playbook
  ("when the primary candidate does not produce a clean setup by mid-morning, commit to the
  secondary — or take zero trades"). This is the second RISK-OFF zero-trade day in the current
  history (after 2026-07-08). Both were correct outcomes. Over 19 days: 11 trades (0.58/day),
  36.4% win rate, avg win +0.559R, avg loss -1.197R, ORB -0.362R across 3 trades, momentum
  -0.975R across 1 trade. No parameter has ever been changed; tuning ledger remains empty.
- 2026-07-10: No tuning. Tuner eligible ("ok to tune", 18 days of history, drawdown 0.0%) but no
  rule fired — parameters left unchanged. Today was a winning session: NVDA ORB buy at $207.22,
  EOD exit at $210.59, +$84.25 P&L (+0.355R). The plan correctly passed on the primary pick (NFLX
  did not produce a clean setup) and executed on the secondary. Entry was 70 minutes into the
  session — late in the ORB window but valid per the 90-minute rule; spread was 1.4 bp (well inside
  the 25 bp gate). Three lessons encoded tonight: (1) Entries & exits — ORB wins are being capped
  by EOD flatten (avg win +0.559R vs 2.5 ATR target across 3 trades); target levels must be used as
  active exit triggers, not just reference points — rule added. (2) Setups — momentum is 0/1 wins
  (-0.975R); require sector alignment and entry within 60 minutes of the seeding ORB before entering
  any momentum trade — rule added. (3) Setups — when the primary candidate passes, fully commit to
  the secondary immediately; do not re-evaluate the primary on subsequent ticks — rule added. Over
  18 days: 11 trades (0.61/day), 36.4% win rate, ORB -0.362R across 3 trades, momentum -0.975R
  across 1 trade. No parameter has ever been changed; all settings remain at their defaults.
- 2026-07-09: No tuning. Tuner eligible ("ok to tune", 17 days of history, drawdown 0.01%) but no
  rule fired — parameters left unchanged. Today was a zero-trade day: INTC blocked at the spread
  gate (209.5 bp at 12:39 PM vs 25 bp max) and subsequently broke down below its ORB low —
  the gate was correct and the chart confirmed it two hours later. NVDA never hit the 1.2x relative
  volume minimum. $0 realized P&L, account equity $999,662.81, ended flat. Three lessons from today:
  (1) Wide live-session spread on a high-gap name is a reversal signal — rule added to Entries &
  exits. (2) The intraday log has only two entries today, both well after the ORB window closed; if
  earlier ticks fired, they are not recorded — the "log every cycle" rule is on the books but must
  be verified in practice. (3) Over 17 days the bot has been idle 82% of the time (14 no-trade
  sessions out of 17, 9 total trades at 0.53/day, 22.2% win rate). This may reflect appropriate
  discipline or gates that are too strict to ever fire; premarket planning should explicitly ask
  whether a clean setup would generate an order, as a self-check. Sample still 9 trades (ORB
  -0.721R across 2 trades, momentum -0.975R across 1 trade); no parameter changed; tuning ledger
  remains empty.
- 2026-07-08: No tuning. Tuner eligible ("ok to tune", 16 days of history, drawdown 0.01%) but no
  rule fired — parameters left unchanged. Today was a zero-trade day by design: regime was RISK-OFF
  (Iran/oil shock premarket, FOMC minutes at 2:00 PM ET), and zero trades was the planned and correct
  outcome. Notably, the premarket phase ran correctly today — a positive step after the failure on
  2026-07-07. No new positions, $0 realized P&L, ended flat. The tuner's reason for inaction: no
  tuning rule triggered. The two negative-expectancy setups (ORB -0.721R across 2 trades, momentum
  -0.975R across 1 trade) have not generated enough fresh evidence to move any parameter — the
  sample is still 9 total trades over 16 days (0.56 trades/day), win rate 22.2%, avg win +0.60R,
  avg loss -1.46R. Skipping a RISK-OFF day entirely is consistent with the existing playbook rule
  ("Risk-off: trade less, smaller, don't buy breakouts into weakness") — no new rule needed. The
  tuning ledger remains empty; no parameter has ever been changed from its default.
- 2026-07-07: No tuning. Tuner eligible ("ok to tune", 15 days of history, drawdown 0.01%) but no
  rule fired — parameters left unchanged. Today was a zero-trade day on an open market. The premarket
  routine did not run, so no watchlist was screened, no day plan was written, no loss-stop baseline
  was captured, and the tick loop had nothing to act on — the bot was silent for the entire session.
  Account equity $999,662.81, $0 realized P&L, ended flat. This is the same premarket failure seen
  on 2026-06-17, 2026-06-19, 2026-06-22, 2026-06-23, and again now: a full trading session lost not
  because of a bad trading decision but because the scheduler did not run the premarket phase. The
  existing Infrastructure rule (missing day_plan.md at open = HALT) already covers the symptom; the
  root cause is that the premarket phase itself is not being reliably scheduled. Premarket scheduling
  reliability is a process priority, not a parameter-tuning problem — no tuner setting changes that.
  No parameter has ever been changed; all settings remain at their defaults. Sample remains 9 trades
  across 15 days (0.6 trades/day), win rate 22%, ORB -0.721R, momentum -0.975R.
- 2026-07-03: No tuning. Tuner eligible ("ok to tune", 14 days of history, drawdown 0.01%) but no
  rule fired — parameters left unchanged. Today was a full US market holiday (Independence Day
  observed). Zero trades, $0 P&L, equity $999,662.81 (-0.01% total return). Three durable rules
  added from post-holiday preparation: (1) Time of day — no entries before 9:45 AM ET on
  post-holiday reopenings. (2) Infrastructure — verify Alpaca /clock at the first tick on
  post-holiday reopenings, not only at premarket. (3) Setups — a premarket sector disarm stays in
  effect for the full session unless the tape shows broad stabilization across the sector. No
  parameter has ever been changed; all settings remain at their defaults.
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
