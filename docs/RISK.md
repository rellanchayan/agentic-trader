# Risk & Guardrails — every safety rule and what trips it

Day trading can lose money fast. This bot is wrapped in layers of hard limits. Most are enforced in code
(not just suggestions), so even a bad config or a confused decision can't break them.

## The hard money limits (enforced in `code/constitution.py`)
| Limit | Value | What trips it |
|---|---|---|
| Per trade | ≤ $10,000 | a single BUY order bigger than $10k is rejected |
| Per day deployed | ≤ $50,000 | total BUY dollars today + this order over $50k is rejected |
| Per name | ≤ 25% of equity | a BUY that pushes one ticker over 25% of the account is rejected |
| Open positions | ≤ 8 | a BUY of a 9th different name is rejected |
| Trades per day | ≤ 20 | the 21st order of the day is rejected |
| Trades per week | ≤ 50 | the 51st order of the week is rejected |
| Order type | LIMIT + DAY only | any market order or non-DAY order is rejected |
| Instruments | stocks + plain ETFs | options/shorts/crypto/leveraged/inverse/vol products are rejected |
| Buying power | must cover the order | a BUY bigger than available buying power is rejected |
| Reason | required | an order with no real reason is rejected |

## The day-state limits (enforced in `code/daytrade_guard.py` + `code/preflight.py`)
| Limit | What it does |
|---|---|
| **Daily loss-stop: −$3,000** | when today's loss hits $3,000, the bot flattens and stops for the day (hard-floored in `code/daypnl.py` — config can't loosen it) |
| **No new entries after 3:30pm ET** | late-day entries are blocked; we're winding down |
| **Flatten window after 3:50pm ET** | no new BUYs once we start closing out |
| **PDT / $25k floor** | if equity nears $26,000, new BUYs are blocked to stay clear of pattern-day-trader limits |
| **Stale quote block** | a BUY priced off a quote older than ~30 seconds is rejected |
| **Wide spread block** | a BUY in a name with a spread wider than the limit is rejected |

## The two stop switches
- **`.HALT_TRADING`** — a file you (a human) create to stop everything. The bot never deletes it. Trading
  resumes only when you remove it. Use the `/halt` skill or just create the file.
- **`state/day_stop.json`** — the automatic daily loss-stop. Turns on at −$3,000, resets next morning.

## Flat by the close
Every day ends with zero positions (`/flatten-close`). Overnight risk is therefore zero. If the final
close-out can't fully fill (no market orders allowed), the leftover is logged loudly and cleared at the
next open — never hidden.

## The auto-tuner can't run wild
The nightly learning step changes at most **one** setting, by a **small** step, within **hard bounds**
(`state/param_bounds.json`), and **freezes entirely** if we just hit the loss-stop, are on a 3-day losing
streak, or are in a drawdown over 5%. Every change is logged in `state/tuning_ledger.jsonl` and reversible
(`tuner.py --revert <id>` or `--reset`). The inviolable limits live in code, so the tuner can never reach
them.

## What this does NOT protect against
- **Bad fills / thin data:** the free IEX data feed is a small slice of the market; quotes can lag. We
  mitigate with liquid names + a stale-quote block, but a paid feed would be more faithful.
- **Strategy being wrong:** guardrails cap losses; they don't guarantee profits. Judge the bot over many
  days on risk-adjusted results, not one lucky or unlucky day.
- **This is paper money.** Real money has more friction (worse fills, fees, emotions). Treat strong paper
  results as necessary but not sufficient before ever considering real money.
