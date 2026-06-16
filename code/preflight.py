"""
preflight.py — the fast gate that runs at the START of every 2-minute tick.

This is pure Python with NO language-model cost. Its whole job is to answer one
question cheaply: "should the expensive thinking part of this tick even run?"

It prints a JSON verdict and sets an exit code:
    verdict = "PROCEED"  (exit 0)  → go ahead, wake the intraday-trader brain
    verdict = "EXIT"     (exit 3)  → do nothing this tick (closed / halted / stopped)
    verdict = "FLATTEN"  (exit 4)  → loss-stop just tripped: flatten everything, halt day

Order of checks (cheapest / most important first):
    1. .HALT_TRADING present?            → EXIT (human kill-switch; never auto-removed)
    2. Alpaca reachable + market open?    → else EXIT (Alpaca clock is the authority)
    3. day_stop already active today?     → EXIT (loss-stop fired earlier)
    4. today's P&L <= -loss_stop?         → write day_stop, FLATTEN
    5. otherwise                          → PROCEED

Usage:
    python3 code/preflight.py
"""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import daypnl
from clockutil import et_today_str
from daytrade_guard import day_stop_active

ROOT = Path(__file__).resolve().parent.parent
HALT_FILE = ROOT / ".HALT_TRADING"
DAY_STOP_FILE = ROOT / "state" / "day_stop.json"
INTRADAY_HISTORY_FILE = ROOT / "state" / "intraday_history.jsonl"


def _run_client(*flags: str) -> dict | None:
    try:
        out = subprocess.run(
            [sys.executable, "code/alpaca_client.py", *flags],
            cwd=ROOT, text=True, capture_output=True,
        )
        if out.returncode != 0:
            return None
        return json.loads(out.stdout)
    except Exception:
        return None


def _write_day_stop(reason: str, details: dict) -> None:
    DAY_STOP_FILE.parent.mkdir(parents=True, exist_ok=True)
    DAY_STOP_FILE.write_text(json.dumps({
        "date": et_today_str(),
        "active": True,
        "reason": reason,
        "tripped_at_utc": datetime.now(timezone.utc).isoformat(),
        "details": details,
    }, indent=2))


def _log_equity(equity: float, cash: float | None) -> None:
    try:
        INTRADAY_HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
        with INTRADAY_HISTORY_FILE.open("a") as f:
            f.write(json.dumps({
                "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                "equity": equity,
                "cash": cash,
            }) + "\n")
    except Exception:
        pass


def verdict(name: str, reason: str, **extra) -> dict:
    return {"verdict": name, "reason": reason, **extra}


def run() -> tuple[dict, int]:
    today = et_today_str()

    # 1. Human kill-switch
    if HALT_FILE.exists():
        return verdict("EXIT", ".HALT_TRADING present — trading halted by a human"), 3

    # 2. Market actually open right now (Alpaca is the authority on holidays/half-days)
    clock = _run_client("--clock")
    if clock is None:
        return verdict("EXIT", "Alpaca unreachable — doing nothing this tick (safe)"), 3
    if not clock.get("is_open"):
        return verdict("EXIT", "market is closed", next_open=clock.get("next_open")), 3

    # 3. Loss-stop already active earlier today
    if day_stop_active(today):
        return verdict("EXIT", "daily loss-stop already active — halted for the day"), 3

    # 4. Evaluate today's P&L vs the loss-stop
    acct = _run_client("--account")
    if acct is None:
        return verdict("EXIT", "could not read account — doing nothing this tick (safe)"), 3
    equity = float(acct.get("equity"))
    _log_equity(equity, acct.get("cash"))

    ev = daypnl.evaluate(today, equity)
    if ev.get("baseline_equity") is None:
        return verdict("EXIT", "no open_baseline.json — run /premarket first"), 3

    if ev.get("tripped"):
        _write_day_stop("daily loss-stop reached", ev)
        return verdict("FLATTEN", "daily loss-stop reached — flatten everything and halt", pnl=ev), 4

    remaining = ev["loss_stop_usd"] + (ev["day_pnl"] or 0.0)  # how much more we can lose
    return verdict(
        "PROCEED", "ok to trade",
        equity=equity,
        day_pnl=ev["day_pnl"],
        loss_budget_remaining=round(remaining, 2),
    ), 0


def main() -> int:
    v, code = run()
    print(json.dumps(v, indent=2))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
