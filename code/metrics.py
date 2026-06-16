"""
metrics.py — honest scorekeeping. Two jobs:

1. A long-run, risk-adjusted report card vs SPY (Sharpe, drawdown, vol, fill rate).
   Judge the bot on THIS, not on one lucky/unlucky day.

2. A per-day intraday summary (--summary --date YYYY-MM-DD) that reconstructs the
   day's round-trip trades from the REAL reconciled fills and writes
   state/runs/<date>-summary.json. The journal-writer and the auto-tuner both read
   those summary files, so this is the single honest source of "how did today go".

Round-trip P&L is computed FIFO: each SELL is matched against the earliest unmatched
BUY of the same ticker. The "R multiple" of a trade is its profit divided by the
risk we set at entry (entry price minus the stop on the buy order). If a buy carried
no stop, we fall back to treating 1% of price as 1R and say so.

Usage:
    python3 code/metrics.py                         # long-run report (plain English)
    python3 code/metrics.py --json                  # long-run report (JSON)
    python3 code/metrics.py --summary --date 2026-06-15   # write today's summary JSON
"""

from __future__ import annotations

import argparse
import json
import math
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HISTORY_FILE = ROOT / "state" / "portfolio_history.jsonl"
COMPLETED_DIR = ROOT / "state" / "completed_trades"
RUNS_DIR = ROOT / "state" / "runs"
DAY_STOP_FILE = ROOT / "state" / "day_stop.json"

RISK_FREE_RATE = float(os.environ.get("RISK_FREE_RATE", "0.045"))


# ===================== long-run, risk-adjusted report =====================

def load_equity_series() -> list[dict]:
    if not HISTORY_FILE.exists():
        return []
    by_day: dict[str, float] = {}
    for line in HISTORY_FILE.read_text().splitlines():
        try:
            d = json.loads(line)
            by_day[d["timestamp_utc"][:10]] = float(d["equity"])
        except Exception:
            continue
    return [{"date": k, "equity": by_day[k]} for k in sorted(by_day)]


def daily_returns(values: list[float]) -> list[float]:
    return [values[i] / values[i - 1] - 1 for i in range(1, len(values)) if values[i - 1] > 0]


def sharpe(values: list[float], rf: float = RISK_FREE_RATE) -> float | None:
    rets = daily_returns(values)
    if len(rets) < 2:
        return None
    mean = sum(rets) / len(rets)
    var = sum((r - mean) ** 2 for r in rets) / (len(rets) - 1)
    sd = math.sqrt(var)
    if sd <= 0:
        return None
    daily_rf = (1 + rf) ** (1 / 252) - 1
    return (mean - daily_rf) / sd * math.sqrt(252)


def max_drawdown(values: list[float]) -> float:
    if not values:
        return 0.0
    hwm, mdd = values[0], 0.0
    for v in values:
        hwm = max(hwm, v)
        if hwm > 0:
            mdd = min(mdd, v / hwm - 1)
    return mdd


def annualized_vol(values: list[float]) -> float:
    rets = daily_returns(values)
    if len(rets) < 2:
        return 0.0
    mean = sum(rets) / len(rets)
    var = sum((r - mean) ** 2 for r in rets) / (len(rets) - 1)
    return math.sqrt(var) * math.sqrt(252)


def cagr(values: list[float]) -> float | None:
    if len(values) < 2 or values[0] <= 0:
        return None
    years = len(values) / 252
    if years <= 0:
        return None
    return (values[-1] / values[0]) ** (1 / years) - 1


def fill_rate_for(trades: list[dict]) -> tuple[float | None, dict]:
    details = {"final_orders": 0, "filled": 0, "partial": 0, "unfilled": 0, "pending": 0}
    for t in trades:
        status = str(t.get("status", "")).lower()
        if status in ("submitted", "accepted", "pending_new", "new", "partially_filled"):
            details["pending"] += 1
            if status != "partially_filled":
                continue
        details["final_orders"] += 1
        fq = float(t.get("filled_qty") or 0)
        q = float(t.get("qty") or 0)
        if fq <= 0:
            details["unfilled"] += 1
        elif q and fq >= q:
            details["filled"] += 1
        else:
            details["partial"] += 1
    final = details["final_orders"]
    rate = (details["filled"] / final) if final else None
    return rate, details


def fill_rate() -> tuple[float | None, dict]:
    return fill_rate_for(_all_trades())


def _all_trades() -> list[dict]:
    out = []
    if COMPLETED_DIR.exists():
        for path in COMPLETED_DIR.glob("*.json"):
            try:
                out.append(json.loads(path.read_text()))
            except Exception:
                continue
    return out


def spy_series_for(dates: list[str]) -> list[float] | None:
    if len(dates) < 2:
        return None
    span = 30
    try:
        from datetime import date
        span = (date.fromisoformat(dates[-1]) - date.fromisoformat(dates[0])).days + 15
    except Exception:
        pass
    try:
        out = subprocess.run(
            [sys.executable, "code/alpaca_client.py", "--bars", "SPY", "--timeframe", "day", "--days", str(max(span, 20))],
            cwd=ROOT, text=True, capture_output=True,
        )
        if out.returncode != 0:
            return None
        bars = json.loads(out.stdout).get("bars", [])
    except Exception:
        return None
    by_day = {b["t"][:10]: float(b["c"]) for b in bars}
    aligned, last = [], None
    for d in dates:
        for bd in sorted(by_day):
            if bd <= d:
                last = by_day[bd]
        if last is not None:
            aligned.append(last)
    return aligned if len(aligned) >= 2 else None


def build_report() -> dict:
    series = load_equity_series()
    if len(series) < 2:
        return {"error": "Not enough history yet — run the bot for at least two days."}
    values = [s["equity"] for s in series]
    dates = [s["date"] for s in series]
    rate, fill_details = fill_rate()
    spy = spy_series_for(dates)

    report = {
        "as_of": dates[-1], "started": dates[0], "days_of_history": len(series),
        "equity": round(values[-1], 2),
        "total_return": round(values[-1] / values[0] - 1, 4),
        "sharpe": round(sharpe(values), 2) if sharpe(values) is not None else None,
        "max_drawdown": round(max_drawdown(values), 4),
        "annualized_vol": round(annualized_vol(values), 4),
        "fill_rate": round(rate, 3) if rate is not None else None,
        "fill_details": fill_details,
    }
    cg = cagr(values)
    report["mar"] = round(cg / abs(max_drawdown(values)), 2) if cg is not None and max_drawdown(values) < 0 else None
    if spy:
        report["spy_total_return"] = round(spy[-1] / spy[0] - 1, 4)
        report["spy_sharpe"] = round(sharpe(spy), 2) if sharpe(spy) is not None else None
        report["spy_max_drawdown"] = round(max_drawdown(spy), 4)
    return report


def print_plain(r: dict) -> None:
    if "error" in r:
        print(r["error"]); return
    print(f"RISK-ADJUSTED REPORT — as of {r['as_of']} (started {r['started']}, {r['days_of_history']} days)")
    print(f"  Account value:       ${r['equity']:,.2f}   (total return {r['total_return']:+.2%})")
    print(f"  Sharpe ratio:        {r['sharpe']}" + (f"   vs SPY {r['spy_sharpe']}" if r.get('spy_sharpe') is not None else ""))
    print(f"  Max drawdown:        {r['max_drawdown']:.2%}" + (f"   vs SPY {r['spy_max_drawdown']:.2%}" if r.get('spy_max_drawdown') is not None else ""))
    print(f"  Annualized vol:      {r['annualized_vol']:.2%}")
    print(f"  MAR (return/drawdn): {r['mar']}")
    if r["fill_rate"] is not None:
        fd = r["fill_details"]
        print(f"  LIMIT fill rate:     {r['fill_rate']:.0%}  ({fd['filled']} filled / {fd['final_orders']} final)")
    print("  Reminder: judge this on Sharpe / drawdown vs SPY, not on raw return.")


# ===================== per-day intraday summary =====================

def _trades_for_date(date: str) -> list[dict]:
    """All orders submitted on the given ET-ish date (matched by submitted_at_utc prefix)."""
    out = []
    for t in _all_trades():
        if str(t.get("submitted_at_utc", ""))[:10] == date:
            out.append(t)
    # order by submission time so FIFO matching is chronological
    out.sort(key=lambda t: t.get("submitted_at_utc", ""))
    return out


def _risk_per_share(buy: dict, entry: float) -> tuple[float, bool]:
    stop = buy.get("stop")
    if stop is not None and float(stop) > 0 and float(stop) < entry:
        return entry - float(stop), True
    return max(entry * 0.01, 1e-9), False   # fallback: 1% of price = 1R


def fifo_roundtrips(trades: list[dict]) -> tuple[list[dict], dict[str, float]]:
    """Match SELLs against earlier BUYs (FIFO) per ticker. Returns the closed
    round trips and the leftover open quantity per ticker."""
    lots: dict[str, list[dict]] = {}     # ticker -> queue of open buy lots
    roundtrips: list[dict] = []

    for t in trades:
        status = str(t.get("status", "")).lower()
        fq = float(t.get("filled_qty") or 0)
        price = t.get("filled_avg_price")
        if fq <= 0 or price is None or status not in ("filled", "partially_filled"):
            continue
        price = float(price)
        sym = t.get("ticker", "").upper()
        side = t.get("side", "").upper()

        if side == "BUY":
            lots.setdefault(sym, []).append({
                "qty": fq, "price": price,
                "stop": t.get("stop"), "setup": t.get("setup") or t.get("strategy") or "unknown",
            })
        elif side == "SELL":
            remaining = fq
            queue = lots.get(sym, [])
            while remaining > 1e-9 and queue:
                lot = queue[0]
                matched = min(remaining, lot["qty"])
                entry = lot["price"]
                rps, had_stop = _risk_per_share(lot, entry)
                pnl = (price - entry) * matched
                r_mult = (price - entry) / rps
                roundtrips.append({
                    "ticker": sym, "setup": lot["setup"], "qty": matched,
                    "entry": entry, "exit": price, "pnl": round(pnl, 2),
                    "r": round(r_mult, 3), "win": pnl > 0, "had_stop": had_stop,
                })
                lot["qty"] -= matched
                remaining -= matched
                if lot["qty"] <= 1e-9:
                    queue.pop(0)

    leftover = {sym: round(sum(l["qty"] for l in q), 4) for sym, q in lots.items() if sum(l["qty"] for l in q) > 1e-9}
    return roundtrips, leftover


def build_day_summary(date: str, ended_flat: bool | None = None) -> dict:
    trades = _trades_for_date(date)
    roundtrips, leftover = fifo_roundtrips(trades)
    closed = len(roundtrips)
    wins = [rt for rt in roundtrips if rt["win"]]
    losses = [rt for rt in roundtrips if not rt["win"]]
    realized = round(sum(rt["pnl"] for rt in roundtrips), 2)
    rate, fill_details = fill_rate_for(trades)

    per_setup: dict[str, dict] = {}
    for rt in roundtrips:
        s = per_setup.setdefault(rt["setup"], {"trades": 0, "wins": 0, "pnl": 0.0, "r_sum": 0.0})
        s["trades"] += 1
        s["wins"] += 1 if rt["win"] else 0
        s["pnl"] = round(s["pnl"] + rt["pnl"], 2)
        s["r_sum"] += rt["r"]
    for s in per_setup.values():
        s["expectancy_r"] = round(s["r_sum"] / s["trades"], 3) if s["trades"] else 0.0
        del s["r_sum"]

    hit_loss_stop = False
    if DAY_STOP_FILE.exists():
        try:
            d = json.loads(DAY_STOP_FILE.read_text())
            hit_loss_stop = bool(d.get("active")) and str(d.get("date")) == date
        except Exception:
            pass

    if ended_flat is None:
        ended_flat = len(leftover) == 0

    return {
        "date": date,
        "num_trades": len(trades),
        "num_roundtrips": closed,
        "realized_pnl": realized,
        "win_rate": round(len(wins) / closed, 3) if closed else 0.0,
        "avg_win_r": round(sum(rt["r"] for rt in wins) / len(wins), 3) if wins else 0.0,
        "avg_loss_r": round(sum(rt["r"] for rt in losses) / len(losses), 3) if losses else 0.0,
        "fill_rate": round(rate, 3) if rate is not None else None,
        "fill_details": fill_details,
        "hit_loss_stop": hit_loss_stop,
        "ended_flat": ended_flat,
        "leftover_positions": leftover,
        "per_setup": per_setup,
        "roundtrips": roundtrips,
    }


def write_day_summary(date: str, ended_flat: bool | None = None) -> Path:
    summary = build_day_summary(date, ended_flat)
    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    path = RUNS_DIR / f"{date}-summary.json"
    path.write_text(json.dumps(summary, indent=2))
    return path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--summary", action="store_true", help="write the per-day summary JSON")
    parser.add_argument("--date", default=None)
    args = parser.parse_args()

    if args.summary:
        from clockutil import et_today_str
        date = args.date or et_today_str()
        summary = build_day_summary(date)
        path = write_day_summary(date)
        print(f"wrote {path.relative_to(ROOT)}")
        print(json.dumps({k: summary[k] for k in
                          ("date", "num_trades", "num_roundtrips", "realized_pnl",
                           "win_rate", "fill_rate", "hit_loss_stop", "ended_flat")}, indent=2))
        return 0

    report = build_report()
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print_plain(report)
    return 0 if "error" not in report else 1


if __name__ == "__main__":
    raise SystemExit(main())
