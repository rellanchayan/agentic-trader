# How It Works (plain English)

This bot is a day trader that runs itself. You do not have to do anything during the day. Here is the
whole thing in simple terms.

## The big picture

A day trader does three things: pick what to watch, trade it during the day, and review at night. Then
repeat tomorrow, a little smarter. This bot does exactly that, automatically, with paper money.

It runs in **four parts** each weekday:

```
   MORNING (≈9:28am ET)        ALL DAY (every 2 min)        CLOSE (≈3:55pm ET)      NIGHT (≈4:30pm ET)
   ┌───────────────┐           ┌───────────────┐            ┌──────────────┐        ┌───────────────┐
   │  /premarket   │ ───────▶  │     /tick     │ ────────▶  │ /flatten-    │ ─────▶ │ /postmarket-  │
   │ plan the day  │  repeats  │ buy/sell/hold │            │   close      │        │    learn      │
   └───────────────┘  ~195x    └───────────────┘            │ sell it all  │        │ journal+learn │
                                                            └──────────────┘        └───────────────┘
```

## 1. Morning — `/premarket`
Before the 9:30am open, the bot:
- logs in to the paper account and checks it's healthy,
- writes down today's starting money (the "baseline") — this is what the daily loss-stop measures from,
- reads the news and decides the market's **mood** (confident "risk-on" or fearful "risk-off"),
- picks the handful of liquid, moving stocks to watch today and notes their key price levels,
- writes a clear plan to `docs/plan/<date>.md`.

## 2. All day — `/tick` (every 2 minutes)
This is the trader's brain. Every 2 minutes it:
1. runs a **fast safety check** first (is the market open? are we halted? did we hit the daily loss
   limit?). If anything is off, it does nothing and waits for the next tick. This costs almost nothing.
2. if all clear, it looks at live prices and decides, fresh, what to do **right now**: protect or sell
   what we hold (hit a stop or a target?), and maybe buy a new setup. It places **limit orders** only.
3. it writes down what it did and why, every single time — even when it does nothing.

It thinks fresh each tick (no fixed script), but it always follows the rules and the playbook.

## 3. Close — `/flatten-close`
Near 3:55pm the bot **sells everything** so we hold nothing overnight. It does this in a few escalating
passes so even stubborn positions get sold. Being flat overnight means a surprise gap can't hurt us.

## 4. Night — `/postmarket-learn`
After the close the bot:
- gets the **true** results from Alpaca (never guessing),
- writes an honest journal: what we made or lost, every trade, what worked, what didn't, lessons,
- lets the **auto-tuner** make at most one small, safe, reversible setting change — and only if there's
  real evidence and we're not on a losing streak,
- updates the **playbook** (`docs/PLAYBOOK.md`) with what it learned.

## Where to look
- **Today's plan:** `docs/plan/<date>.md`
- **What it's doing right now:** `docs/intraday/<date>.md`
- **Each trade, explained:** `docs/trades/<date>.md`
- **The honest nightly review:** `docs/journal/<date>.md`
- **The rules it's learned:** `docs/PLAYBOOK.md`
- **The settings:** `state/config.json` (and the hard limits it can never cross: `state/param_bounds.json`)

## How to stop it
Create a file named `.HALT_TRADING` in the project folder (or run the `/halt` skill). While that file
exists, the bot places no orders. Only you can remove it.
