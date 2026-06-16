# agentic-trader

A **fully-agentic intraday day-trader** built on Claude Code. Claude *is* the trader: it researches,
decides, buys, and sells **paper money** on Alpaca by itself, all day, and improves a little each night.

> **Paper money only.** No live trading. See [`CLAUDE.md`](CLAUDE.md) for the full rulebook.

## What it does
- Runs itself every weekday: plan in the morning → decide every 2 minutes → sell everything at the close
  → review and learn at night.
- Trades only liquid large-cap stocks and big ETFs, with LIMIT + DAY orders only.
- Aggressive-but-bounded budget: ≤ $50k/day, ≤ $10k/trade, hard −$3,000 daily loss-stop, ≤ 8 positions,
  flat overnight.
- Logs everything in plain English (plan, every trade with its reasoning, a running log, a nightly
  journal) and learns via a tiny, safe, reversible nightly auto-tune.

New here? Read [`docs/HOW_IT_WORKS.md`](docs/HOW_IT_WORKS.md) first, then
[`docs/STRATEGY.md`](docs/STRATEGY.md) and [`docs/GLOSSARY.md`](docs/GLOSSARY.md).

## Setup

1. **Install dependencies** (the run scripts also do this automatically):
   ```bash
   python3 -m pip install -r requirements.txt
   ```

2. **Add your OWN separate Alpaca paper keys** (a different paper account from `paper-trader`):
   ```bash
   cp .env.example .env
   # edit .env and paste this account's paper key + secret
   ```

3. **Health check** — confirm it connects and is a *different* account:
   ```bash
   python3 code/alpaca_client.py --healthcheck
   ```

4. **Run the tests** (no network needed):
   ```bash
   for t in code/tests/test_*.py; do python3 "$t"; done
   ```

## Try one phase by hand (recommended before automating)
```bash
bash code/run_phase.sh premarket     # build the plan + today's names
bash code/run_phase.sh tick          # one safety-gated tick (PROCEED/EXIT/FLATTEN)
bash code/run_phase.sh flatten 1     # close everything out
bash code/run_phase.sh postmarket    # reconcile + summary + gated auto-tune
```

## Run it unattended (Claude Code `/schedule`)
Create four cloud routines (all times **New York**), and set `ALPACA_API_KEY`, `ALPACA_SECRET_KEY`, and
`ALPACA_ENDPOINT=https://paper-api.alpaca.markets` as **environment variables on each routine's cloud
environment** (routines do not read the repo `.env`):

| Routine | Schedule (New York) | Prompt |
|---|---|---|
| Morning plan | weekdays 9:28am | `/premarket` |
| Trade loop | weekdays, every 2 min 9:30am–3:58pm | `/tick` |
| Close-out | weekdays 3:50, 3:53, 3:56pm | `/flatten-close` |
| Review + learn | weekdays 4:30pm | `/postmarket-learn` |

If the platform won't accept a 2-minute interval, use 3–5 minutes (it barely changes results for liquid
large-caps and costs less). The market-hours/holiday check happens inside each tick via Alpaca's clock,
so the schedule only needs to be roughly inside the window.

## Stop it any time
Create `.HALT_TRADING` in the project root (or run `/halt`). The bot then places no orders until **you**
delete that file. To also go flat, run `/flatten-close` first.

## Layout
```
code/      the engine (Alpaca client, guards, setups math, tick gate, flatten, tuner, metrics, tests)
state/     machine truth (config, per-day data, trades, summaries) — JSON/JSONL
docs/      human-readable plan, trade cards, intraday log, nightly journal, glossary, playbook
.claude/   the 7 agents and 5 skills that make it agentic
CLAUDE.md  the constitution (rules the bot must obey)
```
