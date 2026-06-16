"""
flatten.py — get the account to ZERO positions before the close (true day trading).

Why: this bot is flat overnight on purpose, so a surprise overnight gap can never
hurt us. Because the constitution bans market orders, we cannot "just sell at market".
Instead we place SELL limits priced BELOW the current bid ("marketable" limits) so
they cross the spread and fill right away — but still as LIMIT + DAY orders.

It runs in escalating passes (called at 15:50, 15:53, 15:56 ET). Each later pass
prices more aggressively so anything still unsold gets filled:
    pass 1 → 0.05% below bid
    pass 2 → 0.20% below bid
    pass 3 → 0.50% below bid

Each pass first cancels all working orders (so leftover BUY limits don't refill us),
then sells every position, then reconciles and reports what (if anything) is left.

Usage:
    python3 code/flatten.py --aggression 1
    python3 code/flatten.py --verify        # just check whether we are flat
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone as tz
from pathlib import Path

import alpaca_client as ac
from clockutil import et_now, et_today_str

ROOT = Path(__file__).resolve().parent.parent
PENDING_DIR = ROOT / "state" / "pending_trades"
RUNS_DIR = ROOT / "state" / "runs"

OFFSET_BY_AGGRESSION = {1: 0.0005, 2: 0.0020, 3: 0.0050}


def _positions() -> list[dict]:
    c = ac._client()
    out = []
    for p in c.get_all_positions():
        out.append({"ticker": p.symbol.upper(), "qty": float(p.qty)})
    return out


def _bid_for(symbols: list[str]) -> dict:
    if not symbols:
        return {}
    from alpaca.data.requests import StockLatestQuoteRequest
    from alpaca.data.enums import DataFeed
    dc = ac._data_client()
    res = dc.get_stock_latest_quote(StockLatestQuoteRequest(symbol_or_symbols=symbols, feed=DataFeed.IEX))
    return {s: float(res[s].bid_price) for s in symbols if s in res and res[s].bid_price}


def _submit(trade: dict) -> dict:
    PENDING_DIR.mkdir(parents=True, exist_ok=True)
    path = PENDING_DIR / f"{trade['trade_id']}.json"
    path.write_text(json.dumps(trade, indent=2))
    out = subprocess.run([sys.executable, "code/alpaca_client.py", "--submit", str(path)],
                         cwd=ROOT, text=True, capture_output=True)
    return {"trade_id": trade["trade_id"], "rc": out.returncode,
            "stdout": out.stdout.strip(), "stderr": out.stderr.strip()}


def flatten(aggression: int) -> dict:
    ac._require_paper()
    offset = OFFSET_BY_AGGRESSION.get(aggression, 0.0005)
    now = et_now()
    hhmm = now.strftime("%H%M")
    date = et_today_str(now)

    # 1. cancel all working orders so a leftover BUY limit can't refill us mid-flatten
    subprocess.run([sys.executable, "code/alpaca_client.py", "--cancel-all"],
                   cwd=ROOT, text=True, capture_output=True)

    positions = _positions()
    longs = [p for p in positions if p["qty"] > 0]
    bids = _bid_for([p["ticker"] for p in longs])

    submissions = []
    for p in longs:
        sym = p["ticker"]
        bid = bids.get(sym)
        if not bid:
            submissions.append({"ticker": sym, "skipped": "no bid quote"})
            continue
        limit = round(bid * (1.0 - offset), 2)
        trade = {
            "trade_id": f"FLAT-{date}-{sym}-{hhmm}",
            "created_at_utc": datetime.now(tz.utc).isoformat(),
            "ticker": sym,
            "side": "SELL",
            "qty": p["qty"],
            "limit_price": limit,
            "order_type": "LIMIT",
            "time_in_force": "DAY",
            "reason": f"End-of-day flatten (pass {aggression}): closing intraday position to be flat overnight.",
            "risk": "Marketable sell limit; if unfilled a later, more aggressive pass re-prices it.",
            "strategy": "flatten",
            "setup": "eod_flatten",
            "status": "ready",
        }
        submissions.append(_submit(trade))

    # reconcile to capture fills
    subprocess.run([sys.executable, "code/alpaca_client.py", "--reconcile"],
                   cwd=ROOT, text=True, capture_output=True)

    remaining = [p for p in _positions() if abs(p["qty"]) > 0]
    summary = {
        "phase": "flatten",
        "aggression": aggression,
        "timestamp_et": now.isoformat(),
        "attempted": len(longs),
        "submissions": submissions,
        "remaining_positions": remaining,
        "is_flat": len(remaining) == 0,
    }
    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    (RUNS_DIR / f"{now.strftime('%Y%m%d-%H%M%S')}-flatten.json").write_text(json.dumps(summary, indent=2))
    return summary


def verify() -> dict:
    ac._require_paper()
    remaining = [p for p in _positions() if abs(p["qty"]) > 0]
    return {"is_flat": len(remaining) == 0, "remaining_positions": remaining}


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--aggression", type=int, default=1, choices=[1, 2, 3])
    p.add_argument("--verify", action="store_true")
    args = p.parse_args()
    if args.verify:
        print(json.dumps(verify(), indent=2))
        return 0
    print(json.dumps(flatten(args.aggression), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
