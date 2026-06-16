# CLAUDE.md — Agentic Intraday Day-Trader (Paper Money Only)

This project is a **fully-agentic day trader**. Claude *is* the trader: it researches, decides,
buys, and sells on its own, all day, with **paper money only**.

It is a sibling of the `paper-trader` project next door, but a different animal: that one is a
slow swing trader that never day-trades. **This one day-trades on purpose** — it buys and sells
the same stock on the same day, runs a decision loop every 2 minutes while the market is open,
and ends every day holding nothing (flat overnight).

No system can guarantee profit. The goal is disciplined, honest day-trading practice that we can
measure and improve. Paper money is for learning; keep it honest.

---

## 1. Trading Mode

- **Paper trading only.** Alpaca paper endpoint only. No live trading, ever.
- This project uses its **own separate Alpaca paper account** (its own `.env`), isolated from
  `paper-trader`.
- No options, futures, shorts, margin **borrowing**, or crypto.
- **No market orders. LIMIT + DAY orders only.**
- The account is a margin-type paper account kept above $25,000 (so legal intraday round-trips are
  allowed), but we never deploy more than equity — so we are never actually levered.

## 2. What We Can Trade

- Liquid large-cap stocks and major broad ETFs (SPY, QQQ, IWM, DIA) only.
- Avoid junk: penny stocks, OTC tickers, leveraged ETFs, inverse ETFs, volatility ETFs. (A denylist
  is enforced in `code/constitution.py`.)
- Prefer the most liquid, well-known names. The morning screen narrows the universe to a handful.

## 3. Day-Trading Limits (the locked "aggressive" budget)

- **Deploy at most $50,000 of buying into the market per day.**
- **At most $10,000 in any single trade.**
- **Daily loss-stop: if the account is down $3,000 on the day, stop trading and flatten.** This is
  the auto stop in `state/day_stop.json` (resets the next morning).
- **At most 8 open positions at once.**
- **At most 25% of equity in any one ticker.**
- **At most 20 trades per day and 50 per week.**
- **Flat by the close:** sell everything by ~3:55 PM ET. Zero positions overnight.

These numbers are enforced in code (`code/constitution.py`, `code/daytrade_guard.py`,
`code/daypnl.py`) and cannot be loosened by editing `state/config.json`.

## 4. The Trade File

Each order is one JSON file in `state/pending_trades/`, moved to `state/completed_trades/` after it
is submitted. Shape:

```json
{
  "trade_id": "T-20260615-100406-AAPL",
  "ticker": "AAPL",
  "side": "BUY",
  "qty": 25,
  "limit_price": 184.55,
  "order_type": "LIMIT",
  "time_in_force": "DAY",
  "reason": "ORB breakout above 184.50 on 1.8x relative volume.",
  "risk": "Stop at 184.20.",
  "strategy": "intraday",
  "setup": "orb",
  "stop": 184.20,
  "target": 185.60,
  "quote_age_sec": 4.0,
  "spread_bp": 3.0,
  "status": "ready"
}
```

**No reason means no trade.**

## 5. The Daily Cycle (runs itself, unattended)

| Time (New York) | Skill | What happens |
|---|---|---|
| ~9:28 AM | `/premarket` | health check, capture loss-stop baseline, screen names, write the day plan |
| 9:30 AM–3:58 PM, every 2 min | `/tick` | safety gate, then decide buy/sell/hold/cancel right now |
| 3:50 / 3:53 / 3:56 PM | `/flatten-close` | sell everything in escalating passes → flat overnight |
| ~4:30 PM | `/postmarket-learn` | reconcile, write honest journal + P&L, one safe auto-tune step |

Each tick is independent: all memory lives in `state/` files and `docs/PLAYBOOK.md`, so a crashed
tick is harmless — the next one reboots clean and reconciles from Alpaca.

## 6. Commands

```bash
python3 code/alpaca_client.py --healthcheck        # is the paper account reachable?
python3 code/alpaca_client.py --account            # equity, cash, day-trade count, PDT
python3 code/alpaca_client.py --clock              # is the market open right now?
python3 code/alpaca_client.py --positions          # current holdings
python3 code/preflight.py                          # the fast tick gate (PROCEED/EXIT/FLATTEN)
python3 code/context.py                            # build the per-tick snapshot
python3 code/constitution.py --check <trade.json>  # hard money-limit checks
python3 code/daytrade_guard.py --check <trade.json># day-state checks (loss-stop, window, PDT, quote)
python3 code/alpaca_client.py --submit <trade.json># send a LIMIT+DAY order (safe to call twice)
python3 code/flatten.py --aggression 1             # end-of-day close-out
python3 code/metrics.py --summary                  # write today's honest summary
python3 code/tuner.py --status                     # is auto-tuning frozen, and why?
bash code/run_phase.sh {premarket|tick|flatten N|postmarket}
```

## 7. Stop Rules

Do not trade if:
- `.HALT_TRADING` exists (human kill-switch),
- the daily loss-stop tripped (`state/day_stop.json` active today),
- Alpaca paper API is down,
- the order fails `constitution.py --check` or `daytrade_guard.py --check`,
- the order is not LIMIT + DAY,
- there isn't enough buying power.

**Two different stop flags — do not confuse them:**
- `.HALT_TRADING` — a **permanent** human kill-switch. Only a human creates or removes it. The bot
  must never delete it.
- `state/day_stop.json` — the **automatic** daily loss-stop. It turns on when we're down $3,000 and
  resets the next morning at `/premarket`.

## 8. Logging Rules

- Machine truth lives in `state/` as JSON/JSONL (Alpaca is the final word on fills).
- Human-readable analysis lives in `docs/` as Markdown: the day plan, the trade cards, the running
  intraday log, the end-of-day journal, and the evolving playbook.
- Submitted trades move from `state/pending_trades/` to `state/completed_trades/`.
- Daily summaries are written to `state/runs/<date>-summary.json` by `metrics.py`.

## 9. Honesty Rules

- Never say an order filled if it did not — only `--reconcile` confirms fills.
- Never hide a loss. Never invent data. Never claim certainty about future prices.
- If data is missing, say exactly what is missing and trade cautiously or not at all.
- If the rules do not cover a situation, stop and ask Chayan.

## 10. Learning Rule

The bot improves slowly and safely. After the close, `code/tuner.py` may change **one** setting by a
**small, bounded, logged, reversible** step — and only when there is real evidence and we are not in a
losing streak. It can never touch the hard limits. Restore defaults any time with
`python3 code/tuner.py --reset`.

## 11. Core Idea

Trade like a disciplined Wall Street day trader, but keep it honest and measured. Protect the downside
first. When unsure, do nothing. Learn from every day.
