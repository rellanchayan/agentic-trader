# The Strategy (plain English)

This explains *how* the bot decides to trade. It is written for someone new to trading, so it defines
things as it goes. For word definitions, see `GLOSSARY.md`.

## The idea
Buy stocks that are showing strength at a meaningful price level, with a clear point where we admit
we're wrong (the stop) and a clear point to take profit (the target). Keep losses small, let winners
pay for them, and never bet the farm on one trade. Close everything by the end of the day.

## What we trade
Only liquid large-cap stocks and big ETFs (like SPY/QQQ). "Liquid" means lots of shares trade, so we
can get in and out without moving the price. Each morning we narrow a big list down to ~5–10 names that
are actually moving today.

## The four setups
A "setup" is a specific, repeatable situation we know how to trade.

1. **Opening-Range Breakout (ORB).** The first ~15 minutes after the open form a high and a low (the
   "opening range"). If the price then breaks clearly above that high, on strong volume, buyers are in
   control — we buy, with a stop just under the range.

2. **VWAP reclaim.** VWAP is the average price of the day weighted by volume — a "fair value" line. If
   a strong stock dips below VWAP and then climbs back above it, that's a bullish sign — we buy, with a
   stop just back below VWAP.

3. **Momentum continuation.** A stock trending up all morning takes a small breather (a pullback) and
   then resumes. We buy the resumption, with a stop under the pullback low.

4. **Mean-reversion (only on quiet, range-bound days).** When the market is going nowhere and a price
   gets stretched far from VWAP, it often snaps back. We fade the extreme back toward VWAP — small size,
   and never on a strong trend or news day.

The bot picks the best setup (or none) each tick based on the day's mood from the morning plan.

## How big each trade is
Two caps, whichever is smaller:
- **Risk cap:** we decide how many dollars we're willing to lose if the stop is hit (a few hundred), and
  size so a stop-out costs no more than that. shares = risk_dollars ÷ (entry − stop).
- **Money cap:** never spend more than $10,000 on one trade. shares = $10,000 ÷ price.

On top of that: never more than 25% of the account in one name, never more than $50,000 deployed in a
day, never more than 8 positions at once.

## Why only limit orders
A **market order** says "fill me at any price" — on a fast-moving stock that can fill far worse than you
expect (called "slippage"). A **limit order** says "fill me at this price or better, never worse." We use
limits priced to fill quickly ("marketable limits") so we still get in fast, but with a price ceiling.

## How stops and targets work here
Normally a stop is an automatic order, but those are *market* orders, which we ban. So instead **the
2-minute brain is the stop**: every tick it checks each holding against its stop and target levels, and
sells with a limit order the moment a level is hit. The trade-off is small (we check every 2 minutes, not
every second), which is fine for liquid large-caps.

## Why we go flat every night
Day traders close out by the end of the day so an overnight news event can't blow up the account while
we sleep. Every morning we start fresh from cash. It also keeps our scorekeeping clean — each day is one
complete, measurable result.

## Avoiding over-trading
The fastest way to lose as a day trader is to trade too much. The bot is limited to 20 trades a day, must
have a real reason for every trade, won't re-enter a name it just exited without a new signal, and slows
down after two losing trades in a row.
