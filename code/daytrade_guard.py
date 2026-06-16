"""
daytrade_guard.py — the day-STATE safety checks, run on every order alongside the
constitution.

The constitution (constitution.py) checks the money limits that never change
(LIMIT+DAY, 25% per name, $10k/trade, $50k/day, 8 positions, ...). THIS module
checks things that depend on where we are in the day:

  * Is the daily loss-stop already tripped?      → block new BUYs
  * Are we past the "no new entries" cutoff?      → block new BUYs
  * Are we in the end-of-day flatten window?      → block new BUYs
  * Is the account near the PDT / $25k floor?     → block new BUYs
  * Is the quote we priced off of too old/stale?  → block new BUYs
  * Is the bid/ask spread too wide right now?      → block new BUYs

SELLs are NEVER blocked here — getting out / reducing risk must always be allowed.

Usage:
    python3 code/daytrade_guard.py --check state/pending_trades/<trade_id>.json
Exit 0 = PASS, non-zero = FAIL.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from constitution import CheckResult  # reuse the same little result type
from clockutil import et_today_str, is_after
from daypnl import load_config

ROOT = Path(__file__).resolve().parent.parent
DAY_STOP_FILE = ROOT / "state" / "day_stop.json"
ACCOUNT_FILE = ROOT / "state" / "account.json"


def _is_buy(trade: dict) -> bool:
    return trade.get("side", "").upper() == "BUY"


def day_stop_active(date: str | None = None) -> bool:
    date = date or et_today_str()
    if not DAY_STOP_FILE.exists():
        return False
    try:
        d = json.loads(DAY_STOP_FILE.read_text())
    except Exception:
        return False
    return bool(d.get("active")) and str(d.get("date")) == date


def check_day_stop(trade: dict) -> CheckResult:
    if not _is_buy(trade):
        return CheckResult("day_stop", True, "sell — always allowed")
    if day_stop_active():
        return CheckResult("day_stop", False, "daily loss-stop is active — no new BUYs today")
    return CheckResult("day_stop", True)


def check_entry_window(trade: dict, config: dict) -> CheckResult:
    if not _is_buy(trade):
        return CheckResult("entry_window", True, "sell — always allowed")
    flatten_start = config.get("flatten_start_et", "15:50")
    no_new = config.get("no_new_entries_after_et", "15:30")
    if is_after(flatten_start):
        return CheckResult("entry_window", False, f"in flatten window (after {flatten_start} ET) — no new BUYs")
    if is_after(no_new):
        return CheckResult("entry_window", False, f"after no-new-entries cutoff ({no_new} ET) — no new BUYs")
    return CheckResult("entry_window", True)


def check_pdt_safe(trade: dict, config: dict) -> CheckResult:
    if not _is_buy(trade):
        return CheckResult("pdt_safe", True, "sell — always allowed")
    floor = float(config.get("pdt_equity_floor_usd", 26000))
    if not ACCOUNT_FILE.exists():
        # No account snapshot — be cautious but don't hard-block; the constitution
        # still gates buying power. Note it.
        return CheckResult("pdt_safe", True, "no account.json — PDT check skipped (run --account)")
    try:
        a = json.loads(ACCOUNT_FILE.read_text())
    except Exception:
        return CheckResult("pdt_safe", True, "account.json unreadable — PDT check skipped")
    equity = float(a.get("equity", 0))
    if equity < floor:
        return CheckResult("pdt_safe", False,
                           f"equity ${equity:,.0f} below ${floor:,.0f} PDT floor — no new BUYs (avoid pattern-day-trader limits)")
    return CheckResult("pdt_safe", True, f"equity ${equity:,.0f} above ${floor:,.0f} floor")


def check_quote_fresh(trade: dict, config: dict) -> CheckResult:
    if not _is_buy(trade):
        return CheckResult("quote_fresh", True, "sell — always allowed")
    max_age = float(config.get("min_quote_freshness_sec", 30))
    age = trade.get("quote_age_sec")
    if age is None:
        return CheckResult("quote_fresh", False,
                           "BUY is missing quote_age_sec — refusing to trade on an unknown-age price")
    if float(age) > max_age:
        return CheckResult("quote_fresh", False,
                           f"quote is {float(age):.0f}s old (> {max_age:.0f}s) — too stale to trust")
    return CheckResult("quote_fresh", True, f"quote {float(age):.0f}s old")


def check_spread_ok(trade: dict, config: dict) -> CheckResult:
    if not _is_buy(trade):
        return CheckResult("spread_ok", True, "sell — always allowed")
    max_bp = float(config.get("max_spread_bp", 25))
    sbp = trade.get("spread_bp")
    if sbp is None:
        return CheckResult("spread_ok", True, "no spread_bp provided — skipped")
    if float(sbp) > max_bp:
        return CheckResult("spread_ok", False,
                           f"spread {float(sbp):.0f}bp wider than {max_bp:.0f}bp limit — too costly to enter")
    return CheckResult("spread_ok", True, f"spread {float(sbp):.0f}bp")


def run_all_checks(trade_path: Path) -> tuple[bool, list[CheckResult]]:
    trade = json.loads(Path(trade_path).read_text())
    config = load_config()
    results = [
        check_day_stop(trade),
        check_entry_window(trade, config),
        check_pdt_safe(trade, config),
        check_quote_fresh(trade, config),
        check_spread_ok(trade, config),
    ]
    return all(r.passed for r in results), results


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--check", required=True, help="path to trade JSON")
    args = p.parse_args()
    trade_path = Path(args.check)
    if not trade_path.exists():
        print(f"ERROR: trade file not found: {trade_path}", file=sys.stderr)
        return 2
    passed, results = run_all_checks(trade_path)
    print(f"Day-trade guard: {'PASS' if passed else 'FAIL'} — {trade_path.name}")
    for r in results:
        print(r)
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
