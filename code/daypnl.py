"""
daypnl.py — how much we are up or down TODAY, and whether the daily loss-stop tripped.

Plain English: at the open we record the account's equity (the "baseline"). At any
moment, today's profit/loss is just (equity now) minus (equity at the open). If that
loss reaches the daily loss-stop, the bot stops opening new trades and flattens for
the day.

The loss-stop number is read from state/config.json BUT is hard-floored at $3,000
right here in code, so no config edit (or auto-tune) can ever let a single day lose
more than $3,000 before the brakes come on.

Usage:
    python3 code/daypnl.py                       # today, equity fetched from Alpaca
    python3 code/daypnl.py --date 2026-06-15
    python3 code/daypnl.py --equity 98750.10     # offline / testing: pass equity in
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from clockutil import et_today_str

ROOT = Path(__file__).resolve().parent.parent
CONFIG_FILE = ROOT / "state" / "config.json"

# Inviolable: a single day may never be allowed to lose more than this before the
# loss-stop fires. Hard-coded so config/tuner cannot loosen it.
HARD_LOSS_STOP_USD = 3000.0


def load_config() -> dict:
    if CONFIG_FILE.exists():
        try:
            return json.loads(CONFIG_FILE.read_text())
        except Exception:
            return {}
    return {}


def effective_loss_stop_usd(config: dict | None = None) -> float:
    """The smaller (safer) of the configured stop and the hard $3,000 floor."""
    config = config if config is not None else load_config()
    configured = float(config.get("daily_loss_stop_usd", HARD_LOSS_STOP_USD))
    return min(abs(configured), HARD_LOSS_STOP_USD)


def baseline_path(date: str) -> Path:
    return ROOT / "state" / "day" / date / "open_baseline.json"


def load_baseline(date: str) -> dict | None:
    p = baseline_path(date)
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text())
    except Exception:
        return None


def _baseline_from_last_equity() -> float | None:
    """Fallback baseline for cloud runs that don't have the morning's open_baseline.json.
    Because we are flat overnight, Alpaca's last_equity (yesterday's close) equals
    today's open equity, so it is a correct baseline for the daily loss-stop."""
    p = ROOT / "state" / "account.json"
    if p.exists():
        try:
            le = json.loads(p.read_text()).get("last_equity")
            return float(le) if le is not None else None
        except Exception:
            return None
    return None


def day_pnl(current_equity: float, baseline_equity: float) -> float:
    return current_equity - baseline_equity


def loss_stop_tripped(pnl: float, loss_stop_usd: float) -> bool:
    return pnl <= -abs(loss_stop_usd)


def _fetch_account() -> dict | None:
    """Ask Alpaca for the current account (via the one paper-only client)."""
    try:
        out = subprocess.run(
            [sys.executable, "code/alpaca_client.py", "--account"],
            cwd=ROOT, text=True, capture_output=True,
        )
        if out.returncode != 0:
            return None
        return json.loads(out.stdout)
    except Exception:
        return None


def _fetch_equity() -> float | None:
    a = _fetch_account()
    return float(a["equity"]) if a and a.get("equity") is not None else None


def set_baseline(date: str) -> dict:
    """Record the account's equity at the open as today's baseline, and reset the
    day-stop so a fresh day starts clean. Called by /premarket."""
    a = _fetch_account()
    if not a:
        return {"error": "could not read account from Alpaca — baseline NOT set"}
    bp = baseline_path(date)
    bp.parent.mkdir(parents=True, exist_ok=True)
    baseline = {
        "date": date,
        "equity": float(a["equity"]),
        "cash": float(a.get("cash", 0)),
        "captured_utc": a.get("timestamp_utc"),
    }
    bp.write_text(json.dumps(baseline, indent=2))

    # fresh day → clear any stale loss-stop
    day_stop = ROOT / "state" / "day_stop.json"
    day_stop.write_text(json.dumps({"date": date, "active": False, "reason": "reset at open"}, indent=2))
    return {"baseline_set": True, **baseline, "day_stop": "cleared"}


def evaluate(date: str, current_equity: float | None) -> dict:
    config = load_config()
    stop = effective_loss_stop_usd(config)
    baseline = load_baseline(date)

    result = {
        "date": date,
        "loss_stop_usd": stop,
        "baseline_equity": None,
        "current_equity": current_equity,
        "day_pnl": None,
        "tripped": False,
        "note": "",
    }

    if baseline is None:
        fb = _baseline_from_last_equity()
        if fb is None:
            result["note"] = "no baseline file and no account.json — cannot evaluate loss-stop"
            return result
        result["baseline_equity"] = fb
        result["baseline_source"] = "account.last_equity (flat-overnight fallback)"
    else:
        result["baseline_equity"] = float(baseline.get("equity"))

    if current_equity is None:
        result["note"] = "current equity unavailable (Alpaca down?) — cannot evaluate loss-stop"
        return result

    pnl = day_pnl(current_equity, result["baseline_equity"])
    result["day_pnl"] = round(pnl, 2)
    result["tripped"] = loss_stop_tripped(pnl, stop)
    result["note"] = "LOSS-STOP TRIPPED — flatten and halt for the day" if result["tripped"] else "ok"
    return result


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--date", default=None)
    p.add_argument("--equity", type=float, default=None)
    p.add_argument("--set-baseline", action="store_true", help="capture open equity + reset day-stop")
    args = p.parse_args()

    date = args.date or et_today_str()
    if args.set_baseline:
        print(json.dumps(set_baseline(date), indent=2))
        return 0
    equity = args.equity if args.equity is not None else _fetch_equity()
    print(json.dumps(evaluate(date, equity), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
